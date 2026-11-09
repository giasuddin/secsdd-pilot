import os
import shutil
import subprocess
import tempfile

from flask import Flask, Response, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

MAX_FRAME = 10 ** 6
TIMEOUT = 30
MAX_PNG_BYTES = 50 * 1024 * 1024


def err(msg, code):
    return jsonify({"error": msg}), code


@app.route("/extract", methods=["POST"])
def extract():
    tmpdir = None
    try:
        video = request.files.get("video")
        frame_raw = request.form.get("frameNumber")
        if video is None or frame_raw is None:
            return err("Invalid input", 400)
        try:
            frame = int(str(frame_raw).strip())
        except ValueError:
            return err("Invalid frame number", 400)
        if frame < 0 or frame > MAX_FRAME:
            return err("Invalid frame number", 400)

        # The client-supplied file name is never used for filesystem paths.
        tmpdir = tempfile.mkdtemp(prefix="frame_")
        in_path = os.path.join(tmpdir, "input_video")
        out_path = os.path.join(tmpdir, "frame.png")
        video.save(in_path)
        if os.path.getsize(in_path) == 0:
            return err("Invalid input", 400)

        cmd = [
            "ffmpeg", "-nostdin", "-v", "error", "-y",
            "-i", in_path,
            "-vf", "select=eq(n\\,%d)" % frame,
            "-vframes", "1",
            "-vsync", "0",
            "-f", "image2", "-c:v", "png",
            out_path,
        ]
        try:
            subprocess.run(
                cmd,
                cwd=tmpdir,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return err("Frame at index %d could not be found." % frame, 404)
        except OSError:
            return err("Internal error", 500)

        if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
            return err("Frame at index %d could not be found." % frame, 404)
        if os.path.getsize(out_path) > MAX_PNG_BYTES:
            return err("Frame too large", 400)
        with open(out_path, "rb") as f:
            data = f.read()
        resp = Response(data, status=200, mimetype="image/png")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp
    except Exception:
        return err("Internal error", 500)
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


@app.errorhandler(413)
def too_large(e):
    return err("Upload too large", 400)


@app.errorhandler(404)
def not_found(e):
    return err("Not found", 404)


@app.errorhandler(405)
def not_allowed(e):
    return err("Method not allowed", 405)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
