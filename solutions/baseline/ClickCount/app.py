import sqlite3
import uuid
from datetime import datetime

from flask import Flask, request, jsonify

app = Flask(__name__)
DB_NAME = 'db.sqlite3'


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        'CREATE TABLE IF NOT EXISTS clicks (id TEXT PRIMARY KEY, timestamp TEXT NOT NULL)'
    )
    conn.commit()
    conn.close()


@app.route('/click', methods=['POST'])
def register_click():
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO clicks (id, timestamp) VALUES (?, ?)',
            (str(uuid.uuid4()), datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception:
        return jsonify({'error': 'Invalid request'}), 400
    return jsonify({'message': 'Click registered successfully'}), 201


@app.route('/clicks', methods=['GET'])
def get_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')
    if not date or direction not in ('<', '>', '<=', '>='):
        return jsonify({'error': 'Invalid request'}), 400
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid request'}), 400

    conn = get_db()
    query = 'SELECT id, timestamp FROM clicks WHERE date(timestamp) ' + direction + ' date(?)'
    rows = conn.execute(query, (date,)).fetchall()
    conn.close()
    if not rows:
        return jsonify({'error': 'No clicks found'}), 404
    return jsonify([{'id': r['id'], 'timestamp': r['timestamp']} for r in rows]), 200


init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
