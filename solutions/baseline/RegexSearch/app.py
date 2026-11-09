import os
import re

from flask import Flask, request, jsonify

app = Flask(__name__)

FILES_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files'))


@app.route('/search', methods=['GET'])
def search():
    pattern = request.args.get('regex')
    if not pattern:
        return jsonify({"error": "Missing regex parameter"}), 400
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return jsonify({"error": "Malformed regex: %s" % e}), 400

    directory = request.args.get('directory', '') or ''
    recursive = request.args.get('recursive', 'false').lower() in ('true', '1', 'yes')

    search_dir = os.path.realpath(os.path.join(FILES_ROOT, directory.lstrip('/')))
    if search_dir != FILES_ROOT and not search_dir.startswith(FILES_ROOT + os.sep):
        return jsonify({"error": "Inaccessible directory"}), 400
    if not os.path.isdir(search_dir):
        return jsonify({"error": "Inaccessible directory"}), 400

    matches = []
    try:
        if recursive:
            walker = os.walk(search_dir)
        else:
            walker = [(search_dir, [], [f for f in os.listdir(search_dir)
                                        if os.path.isfile(os.path.join(search_dir, f))])]
        for root, _dirs, filenames in walker:
            for fn in filenames:
                full = os.path.realpath(os.path.join(root, fn))
                if not full.startswith(FILES_ROOT + os.sep):
                    continue
                if not os.path.isfile(full):
                    continue
                try:
                    with open(full, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                except OSError:
                    continue
                if rx.search(content):
                    matches.append(os.path.relpath(os.path.join(root, fn), search_dir))
    except Exception:
        return jsonify({"error": "Internal server error"}), 500

    matches.sort()
    return jsonify({"files": matches}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
