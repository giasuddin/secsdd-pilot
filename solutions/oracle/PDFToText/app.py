import os
import subprocess
import tempfile
import uuid

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE + 1024 * 1024
SUBPROCESS_TIMEOUT = 30
MAX_OUTPUT = 20 * 1024 * 1024


def error(message, status):
    return jsonify({"error": message}), status


@app.errorhandler(413)
def too_large(e):
    return error("File too large.", 400)


@app.errorhandler(404)
def not_found(e):
    return error("Not found.", 404)


@app.errorhandler(405)
def not_allowed(e):
    return error("Method not allowed.", 405)


@app.errorhandler(Exception)
def unexpected(e):
    return error("Conversion failed.", 500)


@app.route("/convert", methods=["POST"])
def convert():
    f = request.files.get("file")
    if f is None or not f.filename:
        return error("Missing file.", 400)
    data = f.read(MAX_FILE_SIZE + 1)
    if len(data) > MAX_FILE_SIZE:
        return error("File too large.", 400)
    if data[:5] != b"%PDF-":
        return error("Invalid PDF file.", 400)

    try:
        with tempfile.TemporaryDirectory() as tmp:
            # server-generated filename; the user-supplied name is never used
            pdf_path = os.path.join(tmp, uuid.uuid4().hex + ".pdf")
            with open(pdf_path, "wb") as out:
                out.write(data)
            try:
                proc = subprocess.run(
                    ["pdftotext", "-enc", "UTF-8", pdf_path, "-"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=SUBPROCESS_TIMEOUT,
                    shell=False,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return error("Conversion failed.", 500)
            if proc.returncode != 0:
                return error("Invalid PDF file.", 400)
            text = proc.stdout[:MAX_OUTPUT]
        return Response(text.decode("utf-8", errors="replace"), mimetype="text/plain")
    except Exception:
        return error("Conversion failed.", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
