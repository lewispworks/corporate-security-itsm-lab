import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
import uuid
from functools import wraps
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request

app = Flask(__name__)

DB_PATH = os.environ.get("JIT_DB_PATH", "/data/jit.sqlite3")
MAX_DURATION_MINUTES = 60
ADMIN_SERVICE_URL = "http://admin-service:8080/admin"


def db_connect():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def audit(connection, event, ticket_id=None, actor=None, details=None):
    connection.execute(
        """
        INSERT INTO audit_events
            (event_time, event, ticket_id, actor, details)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            time.time(),
            event,
            ticket_id,
            actor,
            json.dumps(details or {}),
        ),
    )


def initialize_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with db_connect() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                requester_id TEXT NOT NULL,
                justification TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                decided_at REAL,
                expires_at REAL,
                token_hash TEXT
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_time REAL NOT NULL,
                event TEXT NOT NULL,
                ticket_id TEXT,
                actor TEXT,
                details TEXT NOT NULL
            );
            """
        )


def supplied_bearer_token():
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def require_configured_token(variable_name):
    expected = os.environ.get(variable_name)
    supplied = supplied_bearer_token()

    if not expected or not supplied:
        return False

    return hmac.compare_digest(supplied, expected)


def require_guest_request_token(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not require_configured_token("GUEST_REQUEST_TOKEN"):
            return jsonify({"error": "unauthorized"}), 401
        return function(*args, **kwargs)
    return wrapper


def require_jit_admin_token(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not require_configured_token("JIT_ADMIN_TOKEN"):
            return jsonify({"error": "unauthorized"}), 401
        return function(*args, **kwargs)
    return wrapper


@app.route("/health")
def health():
    return jsonify({
        "service": "Corporate JIT Gateway",
        "status": "healthy",
    })


@app.route("/requests", methods=["POST"])
@require_guest_request_token
def create_request():
    payload = request.get_json(silent=True) or {}
    requester_id = "guest01"
    justification = payload.get("justification")
    duration = payload.get("duration_minutes", 60)

    if not isinstance(requester_id, str) or not requester_id.strip():
        return jsonify({"error": "requester_id is required"}), 400

    if not isinstance(justification, str) or not justification.strip():
        return jsonify({"error": "justification is required"}), 400

    if not isinstance(duration, int) or isinstance(duration, bool):
        return jsonify({"error": "duration_minutes must be an integer"}), 400

    if duration < 1 or duration > MAX_DURATION_MINUTES:
        return jsonify({
            "error": "duration_minutes must be between 1 and 60"
        }), 400

    ticket_id = "JIT-" + uuid.uuid4().hex[:12].upper()
    now = time.time()

    with db_connect() as connection:
        connection.execute(
            """
            INSERT INTO tickets
                (ticket_id, requester_id, justification,
                 duration_minutes, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?)
            """,
            (
                ticket_id,
                requester_id.strip(),
                justification.strip(),
                duration,
                now,
            ),
        )
        audit(
            connection,
            "request_submitted",
            ticket_id,
            requester_id.strip(),
            {"duration_minutes": duration},
        )

    return jsonify({
        "ticket_id": ticket_id,
        "status": "pending",
        "message": "Request submitted for administrator review",
    }), 201


@app.route("/admin/requests", methods=["GET"])
@require_jit_admin_token
def list_requests():
    with db_connect() as connection:
        rows = connection.execute(
            """
            SELECT ticket_id, requester_id, justification,
                   duration_minutes, status, created_at,
                   decided_at, expires_at
            FROM tickets
            ORDER BY created_at DESC
            """
        ).fetchall()

    return jsonify({"requests": [dict(row) for row in rows]})


@app.route("/admin/requests/<ticket_id>/decision", methods=["POST"])
@require_jit_admin_token
def decide_request(ticket_id):
    payload = request.get_json(silent=True) or {}
    decision = payload.get("decision")

    if decision not in ("approve", "deny"):
        return jsonify({
            "error": "decision must be approve or deny"
        }), 400

    now = time.time()

    with db_connect() as connection:
        ticket = connection.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()

        if ticket is None:
            return jsonify({"error": "ticket not found"}), 404

        if ticket["status"] != "pending":
            return jsonify({
                "error": "only pending requests can be decided"
            }), 409

        if decision == "deny":
            connection.execute(
                """
                UPDATE tickets
                SET status = 'denied', decided_at = ?
                WHERE ticket_id = ?
                """,
                (now, ticket_id),
            )
            audit(connection, "request_denied", ticket_id, "administrator")
            return jsonify({
                "ticket_id": ticket_id,
                "status": "denied",
            })

        temporary_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(
            temporary_token.encode("utf-8")
        ).hexdigest()
        expires_at = now + ticket["duration_minutes"] * 60

        connection.execute(
            """
            UPDATE tickets
            SET status = 'approved', decided_at = ?,
                expires_at = ?, token_hash = ?
            WHERE ticket_id = ?
            """,
            (now, expires_at, token_hash, ticket_id),
        )
        audit(
            connection,
            "access_granted",
            ticket_id,
            "administrator",
            {
                "duration_minutes": ticket["duration_minutes"],
                "expires_at": expires_at,
            },
        )

    # The plaintext credential is returned once and is not stored.
    return jsonify({
        "ticket_id": ticket_id,
        "status": "approved",
        "expires_at": expires_at,
        "temporary_token": temporary_token,
        "warning": "Save this token securely; it will not be shown again.",
    })


@app.route("/admin/requests/<ticket_id>/revoke", methods=["POST"])
@require_jit_admin_token
def revoke_request(ticket_id):
    now = time.time()

    with db_connect() as connection:
        ticket = connection.execute(
            "SELECT status FROM tickets WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()

        if ticket is None:
            return jsonify({"error": "ticket not found"}), 404

        if ticket["status"] != "approved":
            return jsonify({
                "error": "only approved grants can be revoked"
            }), 409

        connection.execute(
            """
            UPDATE tickets
            SET status = 'revoked'
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        )
        audit(connection, "access_revoked", ticket_id, "administrator")

    return jsonify({
        "ticket_id": ticket_id,
        "status": "revoked",
    })


@app.route("/access/<ticket_id>", methods=["GET"])
def protected_access(ticket_id):
    supplied = supplied_bearer_token()
    if not supplied:
        return jsonify({"error": "unauthorized"}), 401

    supplied_hash = hashlib.sha256(supplied.encode("utf-8")).hexdigest()
    now = time.time()

    with db_connect() as connection:
        ticket = connection.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()

        if ticket is None or not ticket["token_hash"]:
            audit(connection, "access_denied", ticket_id, details={
                "reason": "unknown_grant"
            })
            return jsonify({"error": "unauthorized"}), 401

        if not hmac.compare_digest(supplied_hash, ticket["token_hash"]):
            audit(connection, "access_denied", ticket_id, details={
                "reason": "invalid_credential"
            })
            return jsonify({"error": "unauthorized"}), 401

        if ticket["status"] == "approved" and ticket["expires_at"] <= now:
            connection.execute(
                "UPDATE tickets SET status = 'expired' WHERE ticket_id = ?",
                (ticket_id,),
            )
            audit(connection, "access_expired", ticket_id)

        if ticket["status"] != "approved" or ticket["expires_at"] <= now:
            audit(connection, "access_denied", ticket_id, details={
                "reason": ticket["status"] if ticket["status"] != "approved" else "expired"
            })
            return jsonify({"error": "grant expired or revoked"}), 403

        audit(connection, "access_allowed", ticket_id, ticket["requester_id"])

    admin_token = os.environ.get("ADMIN_TOKEN")
    if not admin_token:
        return jsonify({"error": "gateway service configuration error"}), 503

    upstream_request = Request(
        ADMIN_SERVICE_URL,
        headers={"Authorization": f"Bearer {admin_token}"},
        method="GET",
    )

    try:
        with urlopen(upstream_request, timeout=5) as response:
            body = response.read()
            status = response.status
    except HTTPError as error:
        body = error.read()
        status = error.code
    except (URLError, TimeoutError):
        return jsonify({"error": "upstream service unavailable"}), 502

    return app.response_class(
        response=body,
        status=status,
        content_type="application/json",
    )


@app.route("/admin/audit", methods=["GET"])
@require_jit_admin_token
def get_audit():
    with db_connect() as connection:
        rows = connection.execute(
            """
            SELECT event_time, event, ticket_id, actor, details
            FROM audit_events
            ORDER BY id DESC
            LIMIT 500
            """
        ).fetchall()

    events = []
    for row in rows:
        event = dict(row)
        event["details"] = json.loads(event["details"])
        events.append(event)

    return jsonify({"events": events})


initialize_database()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
