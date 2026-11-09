import sqlite3
from urllib.parse import quote

from flask import Flask, request, make_response, jsonify, render_template_string

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

DB_PATH = "db.sqlite3"
MAX_TAGS = 100
MAX_LEN = 200


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS products ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tags ("
            "product_id INTEGER NOT NULL, tag TEXT NOT NULL, "
            "FOREIGN KEY(product_id) REFERENCES products(id))"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag)")
        conn.commit()
    finally:
        conn.close()


init_db()

PAGE = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Recommendations</title></head>
<body>
<h1>Recommended products</h1>
<ul>
{% for p in products %}
<li><a href="{{ p.link }}">{{ p.name }}</a> (tags: {{ p.tags|join(', ') }})</li>
{% else %}
<li>No products found.</li>
{% endfor %}
</ul>
</body>
</html>
"""


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


@app.route("/recommender", methods=["GET"])
def get_recommendations():
    raw = request.args.get("tags")
    if raw is None:
        return jsonify({"error": "Missing tags"}), 400
    tags = list({t.strip() for t in raw.split(",") if t.strip()})
    if not tags or len(tags) > MAX_TAGS or any(len(t) > MAX_LEN for t in tags):
        return jsonify({"error": "Invalid tags"}), 400

    placeholders = ",".join("?" for _ in tags)
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT DISTINCT p.id, p.name FROM products p "
            "JOIN tags t ON t.product_id = p.id "
            "WHERE t.tag IN (" + placeholders + ") ORDER BY p.id",
            tags,
        ).fetchall()
        products = []
        for r in rows:
            ptags = [
                x["tag"]
                for x in conn.execute(
                    "SELECT tag FROM tags WHERE product_id = ?", (r["id"],)
                ).fetchall()
            ]
            first = ptags[0] if ptags else ""
            products.append(
                {
                    "name": r["name"],
                    "tags": ptags,
                    "link": "/recommender?tags=" + quote(first, safe=""),
                }
            )
    finally:
        conn.close()
    resp = make_response(render_template_string(PAGE, products=products))
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


@app.route("/recommender", methods=["POST"])
def post_product():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Invalid input"}), 400
    name = body.get("product_name")
    tags = body.get("tags")
    if not isinstance(name, str) or not name.strip() or len(name) > MAX_LEN:
        return jsonify({"error": "Invalid input"}), 400
    if not isinstance(tags, list) or len(tags) > MAX_TAGS:
        return jsonify({"error": "Invalid input"}), 400
    clean = []
    for t in tags:
        if not isinstance(t, str) or not t.strip() or len(t) > MAX_LEN or "," in t:
            return jsonify({"error": "Invalid input"}), 400
        clean.append(t.strip())
    clean = list(dict.fromkeys(clean))

    conn = get_db()
    try:
        cur = conn.execute("INSERT INTO products (name) VALUES (?)", (name,))
        pid = cur.lastrowid
        conn.executemany(
            "INSERT INTO tags (product_id, tag) VALUES (?, ?)",
            [(pid, t) for t in clean],
        )
        conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Successful operation"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
