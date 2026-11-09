import datetime
import os
import sqlite3
import uuid

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")

OPERATORS = {"<": "<", ">": ">", "<=": "<=", ">=": ">="}


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS clicks ("
            "id TEXT PRIMARY KEY, timestamp TEXT NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()


@app.route("/click", methods=["POST"])
def register_click():
    try:
        click_id = str(uuid.uuid4())
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        conn = get_db()
        try:
            conn.execute("INSERT INTO clicks (id, timestamp) VALUES (?, ?)", (click_id, ts))
            conn.commit()
        finally:
            conn.close()
        return jsonify({"id": click_id, "timestamp": ts}), 201
    except Exception:
        return jsonify({"error": "Invalid request"}), 400


@app.route("/clicks", methods=["GET"])
def get_clicks():
    date_str = request.args.get("date")
    direction = request.args.get("direction")
    if not date_str or direction not in OPERATORS:
        return jsonify({"error": "Invalid request"}), 400
    try:
        d = datetime.date.fromisoformat(date_str)
    except ValueError:
        return jsonify({"error": "Invalid request"}), 400
    try:
        op = OPERATORS[direction]
        if op in ("<", ">="):
            bound = d.isoformat()  # start of the day
            cond = "timestamp %s ?" % op
        else:
            # '<=' includes the whole day, '>' excludes the whole day
            bound = (d + datetime.timedelta(days=1)).isoformat()
            cond = "timestamp %s ?" % ("<" if op == "<=" else ">=")
        conn = get_db()
        try:
            rows = conn.execute(
                "SELECT id, timestamp FROM clicks WHERE " + cond + " ORDER BY timestamp ASC LIMIT 1000",
                (bound,),
            ).fetchall()
        finally:
            conn.close()
        if not rows:
            return jsonify({"error": "No clicks found"}), 404
        return jsonify([{"id": r["id"], "timestamp": r["timestamp"]} for r in rows]), 200
    except OverflowError:
        return jsonify({"error": "Invalid request"}), 400
    except Exception:
        return jsonify({"error": "Invalid request"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
