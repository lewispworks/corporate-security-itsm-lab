import hmac
import os

from flask import Flask, jsonify, request

app = Flask(__name__)


def admin_token_is_valid():
    expected_token = os.environ.get("ADMIN_TOKEN")
    authorization = request.headers.get("Authorization", "")
    scheme, _, supplied_token = authorization.partition(" ")

    if not expected_token or scheme.lower() != "bearer" or not supplied_token:
        return False

    return hmac.compare_digest(supplied_token, expected_token)


@app.route("/")
def home():
    return jsonify({
        "service": "Corporate Admin Service",
        "status": "online"
    })


@app.route("/public")
def public():
    return jsonify({
        "resource": "public",
        "access": "granted"
    })

@app.route("/internal")
def internal():
    if not admin_token_is_valid():
        return jsonify({
            "error": "unauthorized"
        }), 401

    return jsonify({
        "resource": "internal",
        "access": "granted"
    })

@app.route("/admin")
def admin():
    if not admin_token_is_valid():
        return jsonify({
            "error": "unauthorized"
        }), 401

    return jsonify({
        "resource": "administrative",
        "access": "granted"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
