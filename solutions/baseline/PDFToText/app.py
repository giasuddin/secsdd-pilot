import os
import subprocess
import tempfile

from flask import Flask, request, jsonify, Response

app = Flask(__name__)


@app.route('/convert', methods=['POST'])
def convert():
    f = request.files.get('file')
    if f is None or not f.filename:
        return jsonify({"error": "Missing file"}), 400

    tmpdir = tempfile.mkdtemp()
    in_path = os.path.join(tmpdir, "input.pdf")
    out_path = os.path.join(tmpdir, "output.txt")
    try:
        f.save(in_path)
        with open(in_path, 'rb') as fh:
            if not fh.read(5).startswith(b'%PDF'):
                return jsonify({"error": "Invalid PDF file"}), 400
        try:
            result = subprocess.run(["pdftotext", in_path, out_path],
                                    capture_output=True, timeout=60)
        except Exception:
            return jsonify({"error": "Conversion failed"}), 500
        if result.returncode != 0 or not os.path.exists(out_path):
            return jsonify({"error": "Conversion failed"}), 500
        with open(out_path, 'r', encoding='utf-8', errors='replace') as fh:
            text = fh.read()
        return Response(text, mimetype='text/plain')
    except Exception:
        return jsonify({"error": "Conversion failed"}), 500
    finally:
        for p in (in_path, out_path):
            try:
                os.remove(p)
            except OSError:
                pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
