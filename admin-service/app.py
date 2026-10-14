from flask import Flask, jsonify

app = Flask(__name__)


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
    return jsonify({
        "resource": "internal",
        "access": "granted"
    })


@app.route("/admin")
def admin():
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
