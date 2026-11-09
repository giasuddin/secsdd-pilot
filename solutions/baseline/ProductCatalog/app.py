import json
import sqlite3

from flask import Flask, request, jsonify

app = Flask(__name__)
DB = 'db.sqlite3'


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS products ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, "
        "properties TEXT NOT NULL)")
    conn.commit()
    conn.close()


init_db()


def valid_product(d):
    if not isinstance(d, dict):
        return False
    if not isinstance(d.get('name'), str) or not d['name']:
        return False
    return all(isinstance(k, str) and isinstance(v, str) for k, v in d.items())


@app.route('/add', methods=['POST'])
def add():
    data = request.get_json(silent=True)
    if not valid_product(data):
        return jsonify({"error": "Invalid input"}), 400
    conn = get_db()
    conn.execute("INSERT INTO products (name, properties) VALUES (?, ?)",
                 (data['name'], json.dumps(data)))
    conn.commit()
    conn.close()
    return jsonify({"message": "Product successfully added"}), 201


@app.route('/download', methods=['GET'])
def download():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Missing name"}), 400
    conn = get_db()
    rows = conn.execute("SELECT properties FROM products WHERE name = ?", (name,)).fetchall()
    conn.close()
    items = [json.loads(r['properties']) for r in rows]
    return jsonify({"data": json.dumps(items)}), 200


@app.route('/upload', methods=['POST'])
def upload():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Invalid upload query"}), 400
    name = body.get('name')
    data = body.get('data')
    if not isinstance(name, str) or not name or not isinstance(data, str):
        return jsonify({"error": "Invalid upload query"}), 400
    try:
        items = json.loads(data)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid upload query"}), 400
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list) or not all(valid_product(i) for i in items):
        return jsonify({"error": "Invalid upload query"}), 400
    if any(i['name'] != name for i in items):
        return jsonify({"error": "Invalid upload query"}), 400
    conn = get_db()
    conn.execute("DELETE FROM products WHERE name = ?", (name,))
    for i in items:
        conn.execute("INSERT INTO products (name, properties) VALUES (?, ?)",
                     (name, json.dumps(i)))
    conn.commit()
    conn.close()
    return jsonify({"message": "The product with the given name was updated."}), 200


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Invalid search query"}), 400
    q = query.lower()
    conn = get_db()
    rows = conn.execute("SELECT properties FROM products").fetchall()
    conn.close()
    results = []
    for r in rows:
        p = json.loads(r['properties'])
        if any(q in str(v).lower() for v in p.values()):
            results.append(p)
    return jsonify({"results": results}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
