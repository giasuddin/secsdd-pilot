import hashlib
import sqlite3
from datetime import datetime, timezone

from flask import Flask, request, jsonify

app = Flask(__name__)
DB = 'db.sqlite3'


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS services ("
                 "service_id TEXT NOT NULL, token_hash TEXT NOT NULL, "
                 "last_notification TEXT NOT NULL, "
                 "PRIMARY KEY (service_id, token_hash))")
    conn.commit()
    conn.close()


init_db()


def hash_token(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request payload"}), 400
    service_id = data.get('serviceId')
    token = data.get('token')
    if not isinstance(service_id, str) or not service_id or not isinstance(token, str) or not token:
        return jsonify({"error": "Invalid request payload"}), 400
    now = datetime.now(timezone.utc).isoformat()
    try:
        conn = get_db()
        conn.execute(
            "INSERT INTO services (service_id, token_hash, last_notification) VALUES (?, ?, ?) "
            "ON CONFLICT(service_id, token_hash) DO UPDATE SET last_notification = excluded.last_notification",
            (service_id, hash_token(token), now))
        conn.commit()
        conn.close()
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
    return jsonify({"message": "Heartbeat registered successfully."}), 200


@app.route('/services', methods=['POST'])
def services():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('token'), str) or not data['token']:
        return jsonify({"error": "Invalid request payload"}), 400
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT service_id, last_notification FROM services WHERE token_hash = ? "
            "ORDER BY service_id", (hash_token(data['token']),)).fetchall()
        conn.close()
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
    return jsonify([{"serviceId": r['service_id'], "lastNotification": r['last_notification']}
                    for r in rows]), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
