import datetime
import html
import os
import sqlite3

from flask import Flask, Response, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")
MAX_CONTENT = 5000
MAX_USERNAME = 100
MAX_LIMIT = 100


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS messages ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "username TEXT NOT NULL, content TEXT NOT NULL, "
            "created_at TEXT NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()


def parse_int(value, default, minimum, maximum):
    if value is None:
        return default
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValueError("bad int")
    if n < minimum:
        raise ValueError("too small")
    return min(n, maximum)


@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
    return resp


@app.route("/messages", methods=["GET"])
def get_messages():
    try:
        limit = parse_int(request.args.get("limit"), 10, 0, MAX_LIMIT)
        offset = parse_int(request.args.get("offset"), 0, 0, 10 ** 9)
    except ValueError:
        return Response("Invalid input", status=400, mimetype="text/plain")
    sort = (request.args.get("sort") or "desc").upper()
    if sort not in ("ASC", "DESC"):
        return Response("Invalid input", status=400, mimetype="text/plain")
    order = "ASC" if sort == "ASC" else "DESC"
    try:
        conn = get_db()
        try:
            rows = conn.execute(
                "SELECT id, username, content, created_at FROM messages "
                "ORDER BY created_at " + order + ", id " + order + " LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        return Response("Internal error", status=500, mimetype="text/plain")

    parts = [
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\"><title>MyForum</title></head>"
        "<body><h1>MyForum</h1><ul>"
    ]
    for r in rows:
        parts.append(
            "<li><strong>%s</strong> <em>%s</em><p>%s</p></li>"
            % (
                html.escape(r["username"], quote=True),
                html.escape(r["created_at"], quote=True),
                html.escape(r["content"], quote=True),
            )
        )
    parts.append("</ul></body></html>")
    return Response("".join(parts), status=200, mimetype="text/html")


@app.route("/messages", methods=["POST"])
def post_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    content = data.get("content")
    username = data.get("username")
    if not isinstance(content, str) or not isinstance(username, str):
        return jsonify({"error": "Invalid input"}), 400
    content = content.strip()
    username = username.strip()
    if not content or not username or len(content) > MAX_CONTENT or len(username) > MAX_USERNAME:
        return jsonify({"error": "Invalid input"}), 400
    try:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO messages (username, content, created_at) VALUES (?, ?, ?)",
                (username, content, ts),
            )
            conn.commit()
        finally:
            conn.close()
    except sqlite3.Error:
        return jsonify({"error": "Internal error"}), 500
    return jsonify({"status": "ok"}), 200


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Invalid input"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
