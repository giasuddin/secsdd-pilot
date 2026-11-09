import os
import re
import shutil
import subprocess
import tempfile

from flask import Flask, Response, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 30 * 1024 * 1024

MAX_IMAGES = 30
MAX_DIM = 2000
MAX_DELAY_MS = 60000
TIMEOUT = 60
SIZE_RE = re.compile(r"^(\d{1,4})x(\d{1,4})$")


def err(msg, code):
    return jsonify({"error": msg}), code


def detect_format(head):
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith(b"GIF87a") or head.startswith(b"GIF89a"):
        return "gif"
    if head.startswith(b"BM"):
        return "bmp"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


def parse_bool(v):
    if v is None:
        return False
    s = str(v).strip().lower()
    if s in ("true", "1", "yes", "on"):
        return True
    if s in ("false", "0", "no", "off", ""):
        return False
    raise ValueError("bad bool")


@app.route("/create-gif", methods=["POST"])
def create_gif():
    tmpdir = None
    try:
        files = [f for f in request.files.getlist("images") if f and f.filename is not None]
        if not files:
            return err("No images provided", 400)
        if len(files) > MAX_IMAGES:
            return err("Too many images", 400)

        size = request.form.get("targetSize")
        m = SIZE_RE.match((size or "").strip())
        if not m:
            return err("Invalid targetSize, expected WIDTHxHEIGHT", 400)
        w, h = int(m.group(1)), int(m.group(2))
        if not (1 <= w <= MAX_DIM and 1 <= h <= MAX_DIM):
            return err("targetSize out of range", 400)

        delay_raw = request.form.get("delay")
        if delay_raw is None or delay_raw.strip() == "":
            delay_ms = 10
        else:
            try:
                delay_ms = int(delay_raw.strip())
            except ValueError:
                return err("Invalid delay", 400)
        if delay_ms < 0 or delay_ms > MAX_DELAY_MS:
            return err("Invalid delay", 400)

        try:
            append_rev = parse_bool(request.form.get("appendReverted"))
        except ValueError:
            return err("Invalid appendReverted", 400)

        tmpdir = tempfile.mkdtemp(prefix="gif_")
        paths = []
        for i, f in enumerate(files):
            head = f.stream.read(16)
            fmt = detect_format(head)
            if fmt is None:
                return err("Unsupported or invalid image file", 400)
            f.stream.seek(0)
            # Server-chosen file name; client name is never used.
            path = os.path.join(tmpdir, "img%03d.%s" % (i, "jpg" if fmt == "jpeg" else fmt))
            f.save(path)
            paths.append((fmt, path))

        # Use explicit coder prefix so ImageMagick cannot be tricked into other delegates.
        inputs = ["%s:%s" % (fmt, p) for fmt, p in paths]
        if append_rev and len(inputs) > 1:
            inputs = inputs + list(reversed(inputs))[1:]
        elif append_rev:
            inputs = inputs + inputs

        out_path = os.path.join(tmpdir, "out.gif")
        centis = max(0, int(round(delay_ms / 10.0)))
        cmd = [
            "convert",
            "-limit", "memory", "256MiB",
            "-limit", "map", "512MiB",
            "-limit", "disk", "1GiB",
            "-limit", "time", "50",
            "-delay", str(centis),
        ]
        for inp in inputs:
            cmd += [inp + "[0]", "-resize", "%dx%d!" % (w, h)]
        cmd += ["-loop", "0", "gif:" + out_path]

        try:
            proc = subprocess.run(
                cmd,
                cwd=tmpdir,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return err("Processing timed out", 500)
        except OSError:
            return err("Image conversion unavailable", 500)

        if proc.returncode != 0 or not os.path.isfile(out_path):
            return err("Failed to create GIF", 500)
        with open(out_path, "rb") as fh:
            data = fh.read()
        resp = Response(data, status=200, mimetype="image/gif")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp
    except Exception:
        return err("Internal server error", 500)
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
