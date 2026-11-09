import re
from email import message_from_string, policy
from email.utils import parseaddr
from html.parser import HTMLParser

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

KEYWORDS = [
    r"unsubscribe",
    r"un-subscribe",
    r"remove\s+me",
    r"deregister\s+me",
    r"de-register\s+me",
    r"stop\s+sending\s+me",
    r"delete\s+me",
    r"take\s+me\s+off",
    r"opt\s+me\s+out",
    r"opt\s+out",
]
KEYWORD_RE = re.compile(r"\b(?:" + "|".join(KEYWORDS) + r")", re.I)
NEGATION_RE = re.compile(
    r"(?:\bdo\s*not|\bdon'?t|\bdo\s*n't|\bnever|\bnot|\bwon'?t|\bno\s+need\s+to|\bplease\s+don'?t)\s+(?:\w+\s+){0,2}$",
    re.I,
)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in ("br", "p", "div", "li"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(content):
    p = TextExtractor()
    try:
        p.feed(content)
        p.close()
    except Exception:
        return ""
    return "".join(p.parts)


def extract_text(msg):
    plain = []
    html_parts = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        ctype = part.get_content_type()
        if ctype not in ("text/plain", "text/html"):
            continue
        try:
            content = part.get_content()
        except Exception:
            try:
                payload = part.get_payload(decode=True) or b""
                content = payload.decode("utf-8", errors="replace")
            except Exception:
                continue
        if not isinstance(content, str):
            continue
        if ctype == "text/plain":
            plain.append(content)
        else:
            html_parts.append(html_to_text(content))
    if plain:
        return "\n".join(plain)
    return "\n".join(html_parts)


def wants_unsubscribe(text):
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            continue
        lines.append(stripped)
    body = "\n".join(lines)
    for m in KEYWORD_RE.finditer(body):
        prefix = body[max(0, m.start() - 40): m.start()]
        prefix = prefix.split("\n")[-1]
        if NEGATION_RE.search(prefix):
            continue
        return True
    return False


def decide(raw):
    msg = message_from_string(raw, policy=policy.default)
    sender_header = msg.get("From", "")
    _, addr = parseaddr(str(sender_header))
    subject = str(msg.get("Subject", "") or "")
    body = extract_text(msg)
    text = body
    if not body.strip():
        text = subject
    return addr, wants_unsubscribe(text)


@app.after_request
def add_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/decideUnsubscribe", methods=["POST"])
def decide_unsubscribe():
    raw_bytes = request.get_data(cache=False)
    if not raw_bytes or not raw_bytes.strip():
        return jsonify({"error": "Invalid request"}), 400
    try:
        raw = raw_bytes.decode("utf-8", errors="replace")
        email_addr, unsub = decide(raw)
    except Exception:
        return jsonify({"error": "Invalid request"}), 400
    return jsonify({"email": email_addr, "unsubscribe": bool(unsub)}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "Invalid request"}), 400


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": "Internal error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
