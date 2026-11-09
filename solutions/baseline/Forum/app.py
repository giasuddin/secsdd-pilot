import sqlite3
from datetime import datetime

from flask import Flask, request, jsonify, Response
from markupsafe import escape

app = Flask(__name__)
DB_NAME = 'db.sqlite3'


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        'CREATE TABLE IF NOT EXISTS messages ('
        'id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'username TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL)'
    )
    conn.commit()
    conn.close()


@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
    except ValueError:
        return jsonify({'error': 'Invalid input'}), 400
    if limit < 0 or offset < 0:
        return jsonify({'error': 'Invalid input'}), 400
    sort = request.args.get('sort', 'desc').upper()
    if sort not in ('ASC', 'DESC'):
        return jsonify({'error': 'Invalid input'}), 400

    conn = get_db()
    rows = conn.execute(
        'SELECT username, content, created_at FROM messages ORDER BY created_at ' + sort +
        ', id ' + sort + ' LIMIT ? OFFSET ?',
        (limit, offset),
    ).fetchall()
    conn.close()

    html = ['<!DOCTYPE html><html><head><title>MyForum</title></head><body><h1>MyForum</h1>']
    for r in rows:
        html.append(
            '<div class="message"><b>{}</b> <small>{}</small><p>{}</p></div>'.format(
                escape(r['username']), escape(r['created_at']), escape(r['content'])
            )
        )
    html.append('</body></html>')
    return Response(''.join(html), mimetype='text/html')


@app.route('/messages', methods=['POST'])
def post_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid input'}), 400
    content = data.get('content')
    username = data.get('username')
    if not isinstance(content, str) or not isinstance(username, str) or not content or not username:
        return jsonify({'error': 'Invalid input'}), 400

    conn = get_db()
    conn.execute(
        'INSERT INTO messages (username, content, created_at) VALUES (?, ?, ?)',
        (username, content, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Successful operation'}), 200


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
