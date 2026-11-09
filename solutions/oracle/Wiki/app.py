import difflib
import sqlite3
from datetime import datetime, timezone

from flask import Flask, request, jsonify, make_response, render_template_string

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

DB_PATH = "db.sqlite3"
MAX_TITLE = 300
MAX_CONTENT = 200000
MAX_NAME = 200
MAX_SUMMARY = 1000


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS entries ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, "
            "content TEXT NOT NULL, last_modified_by TEXT NOT NULL, "
            "last_modified_at TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS edits ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id INTEGER NOT NULL, "
            "contributor TEXT NOT NULL, summary TEXT NOT NULL, "
            "old_content TEXT NOT NULL, new_content TEXT NOT NULL, "
            "edited_at TEXT NOT NULL, "
            "FOREIGN KEY(entry_id) REFERENCES entries(id))"
        )
        conn.commit()
    finally:
        conn.close()


init_db()

LIST_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Wiki entries</title></head>
<body>
<h1>Wiki entries</h1>
<ul>
{% for e in entries %}
<li><a href="/entries/{{ e.id }}">{{ e.title }}</a></li>
{% else %}
<li>No entries yet.</li>
{% endfor %}
</ul>
</body></html>
"""

ENTRY_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{{ entry.title }}</title></head>
<body>
<h1>{{ entry.title }}</h1>
<div class="content"><pre>{{ entry.content }}</pre></div>
<p>Last edited: {{ entry.last_modified_at }} by {{ entry.last_modified_by }}</p>
<h2>Contributors</h2>
<ul>
{% for c in contributors %}<li>{{ c }}</li>{% endfor %}
</ul>
<p><a href="/entries/{{ entry.id }}/edits">View edit history</a> | <a href="/entries">All entries</a></p>
</body></html>
"""

EDITS_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Edits for {{ entry.title }}</title></head>
<body>
<h1>Edit history: {{ entry.title }}</h1>
{% for ed in edits %}
<div class="edit">
<h3>Edit by {{ ed.contributor }} at {{ ed.edited_at }}</h3>
<p>Summary: {{ ed.summary }}</p>
<pre>{{ ed.diff }}</pre>
</div>
{% else %}
<p>No edits.</p>
{% endfor %}
<p><a href="/entries/{{ entry.id }}">Back to entry</a></p>
</body></html>
"""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def entry_json(row):
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "content": row["content"],
        "lastModifiedBy": row["last_modified_by"],
        "lastModifiedAt": row["last_modified_at"],
    }


def html_response(html):
    resp = make_response(html)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
    return resp


def parse_id(entry_id):
    if not entry_id.isascii() or not entry_id.isdigit() or len(entry_id) > 18:
        return None
    return int(entry_id)


def valid_str(v, maxlen, allow_empty=False):
    if not isinstance(v, str) or len(v) > maxlen:
        return False
    return allow_empty or bool(v.strip())


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Request too large"}), 400


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(Exception)
def unexpected(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/entries", methods=["GET"])
def list_entries():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id, title FROM entries ORDER BY id").fetchall()
    finally:
        conn.close()
    return html_response(render_template_string(LIST_PAGE, entries=rows))


@app.route("/entries", methods=["POST"])
def create_entry():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Invalid input"}), 400
    title = body.get("title")
    content = body.get("content")
    created_by = body.get("createdBy")
    if (
        not valid_str(title, MAX_TITLE)
        or not valid_str(content, MAX_CONTENT, allow_empty=True)
        or not valid_str(created_by, MAX_NAME)
    ):
        return jsonify({"error": "Invalid input"}), 400
    ts = now_iso()
    conn = get_db()
    try:
        cur = conn.execute(
            "INSERT INTO entries (title, content, last_modified_by, last_modified_at) "
            "VALUES (?, ?, ?, ?)",
            (title, content, created_by, ts),
        )
        eid = cur.lastrowid
        conn.execute(
            "INSERT INTO edits (entry_id, contributor, summary, old_content, new_content, edited_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (eid, created_by, "Initial creation", "", content, ts),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (eid,)).fetchone()
    finally:
        conn.close()
    return jsonify(entry_json(row)), 201


@app.route("/entries/<entry_id>", methods=["GET"])
def get_entry(entry_id):
    eid = parse_id(entry_id)
    if eid is None:
        return jsonify({"error": "Entry not found"}), 404
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (eid,)).fetchone()
        if row is None:
            return jsonify({"error": "Entry not found"}), 404
        contributors = [
            r["contributor"]
            for r in conn.execute(
                "SELECT contributor FROM edits WHERE entry_id = ? "
                "GROUP BY contributor ORDER BY MIN(id)",
                (eid,),
            ).fetchall()
        ]
    finally:
        conn.close()
    return html_response(render_template_string(ENTRY_PAGE, entry=row, contributors=contributors))


@app.route("/entries/<entry_id>", methods=["PUT"])
def update_entry(entry_id):
    eid = parse_id(entry_id)
    if eid is None:
        return jsonify({"error": "Entry not found"}), 404
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Invalid input"}), 400
    content = body.get("content")
    modified_by = body.get("modifiedBy")
    summary = body.get("summary", "")
    if (
        not valid_str(content, MAX_CONTENT, allow_empty=True)
        or not valid_str(modified_by, MAX_NAME)
        or not valid_str(summary, MAX_SUMMARY, allow_empty=True)
    ):
        return jsonify({"error": "Invalid input"}), 400
    ts = now_iso()
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (eid,)).fetchone()
        if row is None:
            return jsonify({"error": "Entry not found"}), 404
        conn.execute(
            "UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?",
            (content, modified_by, ts, eid),
        )
        conn.execute(
            "INSERT INTO edits (entry_id, contributor, summary, old_content, new_content, edited_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (eid, modified_by, summary, row["content"], content, ts),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (eid,)).fetchone()
    finally:
        conn.close()
    return jsonify(entry_json(row)), 200


@app.route("/entries/<entry_id>/edits", methods=["GET"])
def get_edits(entry_id):
    eid = parse_id(entry_id)
    if eid is None:
        return jsonify({"error": "Entry not found"}), 404
    conn = get_db()
    try:
        row = conn.execute("SELECT * FROM entries WHERE id = ?", (eid,)).fetchone()
        if row is None:
            return jsonify({"error": "Entry not found"}), 404
        rows = conn.execute(
            "SELECT * FROM edits WHERE entry_id = ? ORDER BY id", (eid,)
        ).fetchall()
    finally:
        conn.close()
    edits = []
    for r in rows:
        diff = "\n".join(
            difflib.unified_diff(
                r["old_content"].splitlines(),
                r["new_content"].splitlines(),
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )
        edits.append(
            {
                "contributor": r["contributor"],
                "summary": r["summary"],
                "edited_at": r["edited_at"],
                "diff": diff,
            }
        )
    return html_response(render_template_string(EDITS_PAGE, entry=row, edits=edits))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
