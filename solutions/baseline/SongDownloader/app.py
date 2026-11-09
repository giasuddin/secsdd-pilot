import os

from flask import Flask, request, jsonify, Response, abort

app = Flask(__name__)

SONGS_DIR = '/var/songs'


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input"}), 400
    filename = data.get('filename')
    if not isinstance(filename, str) or not filename or '\x00' in filename:
        return jsonify({"error": "Invalid input"}), 400

    base = os.path.realpath(SONGS_DIR)
    path = os.path.realpath(os.path.join(base, filename))
    if not path.startswith(base + os.sep):
        return jsonify({"error": "Invalid input"}), 400
    if not os.path.isfile(path):
        return jsonify({"error": "File does not exist"}), 404

    def generate():
        with open(path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                yield chunk

    return Response(generate(), mimetype='audio/mpeg')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
