import os
import subprocess
import tempfile

from flask import Flask, request, jsonify, send_file, after_this_request

app = Flask(__name__)


@app.route('/concatenate', methods=['POST'])
def concatenate():
    files = request.files.getlist('files')
    files = [f for f in files if f and f.filename]
    if not files:
        return jsonify({"error": "Invalid input or missing files."}), 400

    tmpdir = tempfile.mkdtemp()
    try:
        paths = []
        for i, f in enumerate(files):
            path = os.path.join(tmpdir, "in_%d.pdf" % i)
            f.save(path)
            with open(path, 'rb') as fh:
                if not fh.read(5).startswith(b'%PDF'):
                    raise ValueError("not a pdf")
            paths.append(path)
    except ValueError:
        cleanup(tmpdir)
        return jsonify({"error": "Invalid input or missing files."}), 400
    except Exception:
        cleanup(tmpdir)
        return jsonify({"error": "An error occurred while processing the files."}), 500

    out_path = os.path.join(tmpdir, "concatenated.pdf")
    try:
        if len(paths) == 1:
            with open(paths[0], 'rb') as src, open(out_path, 'wb') as dst:
                dst.write(src.read())
        else:
            result = subprocess.run(["pdfunite"] + paths + [out_path],
                                    capture_output=True, timeout=60)
            if result.returncode != 0:
                cleanup(tmpdir)
                return jsonify({"error": "Invalid input or missing files."}), 400
        with open(out_path, 'rb') as fh:
            data = fh.read()
    except Exception:
        cleanup(tmpdir)
        return jsonify({"error": "An error occurred while processing the files."}), 500

    cleanup(tmpdir)
    from flask import Response
    return Response(data, mimetype='application/pdf')


def cleanup(tmpdir):
    try:
        for name in os.listdir(tmpdir):
            os.remove(os.path.join(tmpdir, name))
        os.rmdir(tmpdir)
    except OSError:
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
