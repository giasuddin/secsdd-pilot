import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timezone

from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

DB_PATH = "db.sqlite3"
MAX_LEN = 256


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS services ("
            "service_id TEXT NOT NULL, token_hash TEXT NOT NULL, "
            "last_notification TEXT NOT NULL, "
            "PRIMARY KEY (service_id, token_hash))"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()


def load_secret():
    env = os.environ.get("APP_SECRET")
    if env:
        return env.encode("utf-8")
    conn = get_db()
    try:
        row = conn.execute("SELECT v FROM meta WHERE k = 'secret'").fetchone()
        if row:
            return row["v"].encode("utf-8")
        generated = secrets.token_hex(32)
        conn.execute("INSERT OR IGNORE INTO meta (k, v) VALUES ('secret', ?)", (generated,))
        conn.commit()
        row = conn.execute("SELECT v FROM meta WHERE k = 'secret'").fetchone()
        return row["v"].encode("utf-8")
    finally:
        conn.close()


init_db()
SECRET = load_secret()


def hash_token(token):
    # Tokens are never stored in plaintext; keyed hash allows lookup by token.
    return hmac.new(SECRET, token.encode("utf-8"), hashlib.sha256).hexdigest()


def valid_str(v):
    return isinstance(v, str) and 0 < len(v) <= MAX_LEN


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Invalid request payload"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(Exception)
def unexpected(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Invalid request payload"}), 400
    service_id = body.get("serviceId")
    token = body.get("token")
    if not valid_str(service_id) or not valid_str(token):
        return jsonify({"error": "Invalid request payload"}), 400
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO services (service_id, token_hash, last_notification) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(service_id, token_hash) DO UPDATE SET "
            "last_notification = excluded.last_notification",
            (service_id, hash_token(token), now),
        )
        conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Heartbeat registered successfully."}), 200


@app.route("/services", methods=["POST"])
def services():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not valid_str(body.get("token")):
        return jsonify({"error": "Invalid request payload"}), 400
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT service_id, last_notification FROM services "
            "WHERE token_hash = ? ORDER BY service_id",
            (hash_token(body["token"]),),
        ).fetchall()
    finally:
        conn.close()
    return jsonify(
        [
            {"serviceId": r["service_id"], "lastNotification": r["last_notification"]}
            for r in rows
        ]
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
