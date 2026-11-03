#!/usr/bin/env bash
set -euo pipefail
cat > webhook.py <<'PY'
import base64
import hashlib
import hmac
import json

from flask import Flask, request

from app.bookings import apply_event

app = Flask(__name__)
SECRET = b"replace-me"


@app.post("/hooks/partner")
def partner_hook():
    body = json.dumps(request.get_json())
    msg_id = request.headers["webhook-id"]
    timestamp = request.headers["webhook-timestamp"]
    signed = f"{msg_id}.{timestamp}.{body}".encode()
    expected = base64.b64encode(hmac.new(SECRET, signed, hashlib.sha256).digest()).decode()
    given = request.headers["webhook-signature"].split(",", 1)[1]
    if expected != given:
        return "bad signature", 401
    apply_event(request.get_json())
    return "", 204
PY
