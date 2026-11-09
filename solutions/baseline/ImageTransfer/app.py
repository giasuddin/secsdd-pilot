import os
import uuid

from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files.get('file')
        if file is None or not file.filename:
            return jsonify({'error': 'No file provided'}), 400
        image_id = str(uuid.uuid4())
        file.save(os.path.join(UPLOAD_DIR, image_id))
        with open(os.path.join(UPLOAD_DIR, image_id + '.mime'), 'w') as f:
            f.write(file.mimetype or 'application/octet-stream')
        return jsonify({'id': image_id}), 200
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/images/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        try:
            uuid.UUID(image_id)
        except ValueError:
            return jsonify({'error': 'Image not found'}), 404
        path = os.path.join(UPLOAD_DIR, image_id)
        mime_path = path + '.mime'
        if not os.path.exists(path) or not os.path.exists(mime_path):
            return jsonify({'error': 'Image not found'}), 404
        with open(mime_path) as f:
            mimetype = f.read().strip() or 'application/octet-stream'
        return send_file(path, mimetype=mimetype, as_attachment=False)
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
