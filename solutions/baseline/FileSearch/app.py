import os

from flask import Flask, request, jsonify

app = Flask(__name__)
DATA_DIR = '/data'


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Invalid input'}), 400

    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir')

    for v in (search_content, search_filename, search_dir):
        if v is not None and not isinstance(v, str):
            return jsonify({'error': 'Invalid input'}), 400

    base = DATA_DIR
    if search_dir:
        base = os.path.join(DATA_DIR, search_dir.lstrip('/'))
    if not os.path.isdir(base):
        return jsonify({'files': []}), 200

    results = []
    for root, dirs, files in os.walk(base):
        for name in files:
            full = os.path.join(root, name)
            matched = False
            if search_filename and name.startswith(search_filename):
                matched = True
            if not matched and search_content:
                try:
                    with open(full, 'r', errors='ignore') as f:
                        if search_content in f.read():
                            matched = True
                except Exception:
                    pass
            if matched:
                results.append(full)

    return jsonify({'files': results}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
