import sqlite3
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
    conn.execute("CREATE TABLE IF NOT EXISTS products ("
                 "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS tags ("
                 "product_id INTEGER NOT NULL, tag TEXT NOT NULL, "
                 "FOREIGN KEY(product_id) REFERENCES products(id))")
    conn.commit()
    conn.close()


init_db()


@app.route('/recommender', methods=['GET'])
def get_recommendations():
    tags_param = request.args.get('tags')
    if not tags_param:
        return Response("Missing tags parameter", status=400, mimetype='text/plain')
    tags = [t.strip() for t in tags_param.split(',') if t.strip()]
    if not tags:
        return Response("Missing tags parameter", status=400, mimetype='text/plain')
    placeholders = ','.join('?' * len(tags))
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT p.id, p.name FROM products p JOIN tags t ON t.product_id = p.id "
        "WHERE t.tag IN (%s) ORDER BY p.id" % placeholders, tags).fetchall()
    conn.close()
    items = ''.join('<li><a href="/recommender?tags=%s">%s</a></li>' % (
        escape(','.join([]), quote=True), escape(r['name'])) for r in rows)
    html = "<html><body><h1>Recommended products</h1><ul>%s</ul></body></html>" % items
    return Response(html, mimetype='text/html')


@app.route('/recommender', methods=['POST'])
def post_product():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    name = data.get('product_name')
    tags = data.get('tags')
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Invalid input"}), 400
    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        return jsonify({"error": "Invalid input"}), 400
    conn = get_db()
    cur = conn.execute("INSERT INTO products (name) VALUES (?)", (name,))
    pid = cur.lastrowid
    for t in tags:
        conn.execute("INSERT INTO tags (product_id, tag) VALUES (?, ?)", (pid, t.strip()))
    conn.commit()
    conn.close()
    return jsonify({"message": "Successful operation"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
