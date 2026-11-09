import difflib
import sqlite3
import uuid
from datetime import datetime, timezone
from html import escape

from flask import Flask, request, jsonify, Response

app = Flask(__name__)
DB = 'db.sqlite3'


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS entries ("
                 "id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, "
                 "last_modified_by TEXT NOT NULL, last_modified_at TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS edits ("
                 "id INTEGER PRIMARY KEY AUTOINCREMENT, entry_id TEXT NOT NULL, "
                 "contributor TEXT NOT NULL, summary TEXT, old_content TEXT NOT NULL, "
                 "new_content TEXT NOT NULL, edited_at TEXT NOT NULL)")
    conn.commit()
    conn.close()


init_db()


def now():
    return datetime.now(timezone.utc).isoformat()


def entry_json(row):
    return {"id": row['id'], "title": row['title'], "content": row['content'],
            "lastModifiedBy": row['last_modified_by'], "lastModifiedAt": row['last_modified_at']}


def page(body):
    return Response("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Wiki</title></head>"
                    "<body>%s</body></html>" % body, mimetype='text/html')


@app.route('/entries', methods=['GET'])
def list_entries():
    conn = get_db()
    rows = conn.execute("SELECT id, title FROM entries ORDER BY title").fetchall()
    conn.close()
    items = ''.join('<li><a href="/entries/%s">%s</a></li>' % (escape(r['id'], quote=True),
                                                              escape(r['title'])) for r in rows)
    return page("<h1>Wiki entries</h1><ul>%s</ul>" % items)


@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    title, content, created_by = data.get('title'), data.get('content'), data.get('createdBy')
    if not all(isinstance(v, str) and v for v in (title, created_by)) or not isinstance(content, str):
        return jsonify({"error": "Invalid input"}), 400
    entry_id = str(uuid.uuid4())
    ts = now()
    conn = get_db()
    conn.execute("INSERT INTO entries VALUES (?, ?, ?, ?, ?)",
                 (entry_id, title, content, created_by, ts))
    conn.execute("INSERT INTO edits (entry_id, contributor, summary, old_content, new_content, edited_at) "
                 "VALUES (?, ?, ?, ?, ?, ?)",
                 (entry_id, created_by, "Initial creation", "", content, ts))
    conn.commit()
    conn.close()
    return jsonify({"id": entry_id, "title": title, "content": content,
                    "lastModifiedBy": created_by, "lastModifiedAt": ts}), 201


@app.route('/entries/<entry_id>', methods=['GET'])
def get_entry(entry_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if row is None:
        conn.close()
        return Response("Entry not found", status=404, mimetype='text/plain')
    contributors = [r['contributor'] for r in conn.execute(
        "SELECT DISTINCT contributor FROM edits WHERE entry_id = ? ORDER BY id", (entry_id,))]
    conn.close()
    body = ("<h1>%s</h1><div><pre>%s</pre></div><p>Last edited: %s by %s</p>"
            "<p>Contributors: %s</p><p><a href='/entries/%s/edits'>View edit history</a></p>"
            "<p><a href='/entries'>Back to all entries</a></p>") % (
        escape(row['title']), escape(row['content']), escape(row['last_modified_at']),
        escape(row['last_modified_by']), escape(', '.join(contributors)),
        escape(entry_id, quote=True))
    return page(body)


@app.route('/entries/<entry_id>', methods=['PUT'])
def update_entry(entry_id):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    content, modified_by = data.get('content'), data.get('modifiedBy')
    summary = data.get('summary', '')
    if not isinstance(content, str) or not isinstance(modified_by, str) or not modified_by \
            or not isinstance(summary, str):
        return jsonify({"error": "Invalid input"}), 400
    conn = get_db()
    row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if row is None:
        conn.close()
        return jsonify({"error": "Entry not found"}), 404
    ts = now()
    conn.execute("UPDATE entries SET content = ?, last_modified_by = ?, last_modified_at = ? WHERE id = ?",
                 (content, modified_by, ts, entry_id))
    conn.execute("INSERT INTO edits (entry_id, contributor, summary, old_content, new_content, edited_at) "
                 "VALUES (?, ?, ?, ?, ?, ?)",
                 (entry_id, modified_by, summary, row['content'], content, ts))
    conn.commit()
    conn.close()
    return jsonify({"id": entry_id, "title": row['title'], "content": content,
                    "lastModifiedBy": modified_by, "lastModifiedAt": ts}), 200


@app.route('/entries/<entry_id>/edits', methods=['GET'])
def entry_edits(entry_id):
    conn = get_db()
    row = conn.execute("SELECT title FROM entries WHERE id = ?", (entry_id,)).fetchone()
    if row is None:
        conn.close()
        return Response("Entry not found", status=404, mimetype='text/plain')
    edits = conn.execute("SELECT * FROM edits WHERE entry_id = ? ORDER BY id", (entry_id,)).fetchall()
    conn.close()
    parts = ["<h1>Edit history for %s</h1>" % escape(row['title'])]
    for e in edits:
        diff = '\n'.join(difflib.unified_diff(e['old_content'].splitlines(),
                                              e['new_content'].splitlines(),
                                              'before', 'after', lineterm=''))
        parts.append("<div><h3>%s by %s</h3><p>Summary: %s</p><pre>%s</pre></div>" % (
            escape(e['edited_at']), escape(e['contributor']), escape(e['summary'] or ''),
            escape(diff)))
    parts.append("<p><a href='/entries/%s'>Back to entry</a></p>" % escape(entry_id, quote=True))
    return page(''.join(parts))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
