import re
from email import message_from_string
from email.policy import default
from email.utils import parseaddr
from flask import Flask, request, jsonify

app = Flask(__name__)

KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me",
]


def get_body_text(msg):
    parts = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    parts.append(part.get_content())
                except Exception:
                    payload = part.get_payload(decode=True)
                    if payload:
                        parts.append(payload.decode("utf-8", errors="replace"))
    else:
        try:
            parts.append(msg.get_content())
        except Exception:
            payload = msg.get_payload(decode=True)
            if payload:
                parts.append(payload.decode("utf-8", errors="replace"))
    return "\n".join(p for p in parts if isinstance(p, str))


@app.route("/decideUnsubscribe", methods=["POST"])
def decide_unsubscribe():
    raw = request.get_data(as_text=True)
    msg = message_from_string(raw, policy=default)
    sender = str(msg.get("From", ""))
    _, addr = parseaddr(sender)
    if not addr:
        m = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", sender)
        addr = m.group(0) if m else ""
    subject = str(msg.get("Subject", ""))
    body = get_body_text(msg)
    text = (subject + "\n" + body).lower()
    unsubscribe = any(k in text for k in KEYWORDS)
    return jsonify({"email": addr, "unsubscribe": unsubscribe}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
