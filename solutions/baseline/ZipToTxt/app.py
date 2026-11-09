import io
import zipfile

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

MAX_TOTAL_BYTES = 50 * 1024 * 1024


@app.route('/convert', methods=['POST'])
def convert():
    f = request.files.get('file')
    if f is None or not f.filename:
        return jsonify({"error": "Invalid input"}), 400
    data = f.read()
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return jsonify({"error": "Invalid input"}), 400

    parts = []
    total = 0
    try:
        for info in zf.infolist():
            if info.is_dir():
                continue
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                return jsonify({"error": "Invalid input"}), 400
            with zf.open(info) as fh:
                raw = fh.read(MAX_TOTAL_BYTES + 1)
            if len(raw) > MAX_TOTAL_BYTES:
                return jsonify({"error": "Invalid input"}), 400
            if b'\x00' in raw:
                continue
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                continue
            parts.append(text)
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError):
        return jsonify({"error": "Invalid input"}), 400

    return Response('\n'.join(parts), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
