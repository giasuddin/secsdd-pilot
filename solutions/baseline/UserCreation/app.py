import os
import sqlite3
import uuid
import datetime
import jwt
from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
APP_SECRET = os.environ.get("APP_SECRET", "default-secret")
DB = "db.sqlite3"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_name TEXT UNIQUE NOT NULL, "
        "password_hash TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS invitations ("
        "invite_id TEXT PRIMARY KEY, "
        "email TEXT UNIQUE NOT NULL, "
        "invited_by TEXT, "
        "used INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    conn.close()


def current_user():
    """Return the username of the authenticated user, if a valid bearer token is given."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(auth[7:].strip(), APP_SECRET, algorithms=["HS256"])
        return payload.get("user_name")
    except jwt.PyJWTError:
        return None


@app.route("/invite_user", methods=["POST"])
def invite_user():
    data = request.get_json(silent=True)
    email = data.get("email") if isinstance(data, dict) else None
    if not isinstance(email, str) or not email or "@" not in email:
        return jsonify({"message": "Invalid email"}), 400
    conn = get_db()
    row = conn.execute(
        "SELECT invite_id FROM invitations WHERE email = ?", (email,)
    ).fetchone()
    if row is not None:
        invite_id = row["invite_id"]
    else:
        invite_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO invitations (invite_id, email, invited_by) VALUES (?, ?, ?)",
            (invite_id, email, current_user()),
        )
        conn.commit()
    conn.close()
    return jsonify({"invite_id": invite_id, "message": "Invitation created"}), 200


@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "Invalid invite_id"}), 401
    invite_id = data.get("invite_id")
    user_name = data.get("user_name")
    password = data.get("password")
    if not isinstance(invite_id, str):
        return jsonify({"message": "Invalid invite_id"}), 401
    conn = get_db()
    inv = conn.execute(
        "SELECT * FROM invitations WHERE invite_id = ?", (invite_id,)
    ).fetchone()
    if inv is None or inv["used"]:
        conn.close()
        return jsonify({"message": "Invalid invite_id"}), 401
    if (
        not isinstance(user_name, str)
        or not user_name
        or not isinstance(password, str)
        or not password
    ):
        conn.close()
        return jsonify({"message": "Invalid user"}), 400
    try:
        conn.execute(
            "INSERT INTO users (user_name, password_hash) VALUES (?, ?)",
            (user_name, pbkdf2_sha256.hash(password)),
        )
    except sqlite3.IntegrityError:
        conn.close()
        return (
            jsonify({"message": "Username already exists. Try providing different username."}),
            400,
        )
    conn.execute("UPDATE invitations SET used = 1 WHERE invite_id = ?", (invite_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "User created"}), 200


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
