#!/usr/bin/env bash
set -euo pipefail
mkdir -p src tests
touch src/__init__.py tests/__init__.py
cat > src/notify.py <<'PY'
import json
import urllib.request


def send_sms(number, text):
    req = urllib.request.Request(
        "https://sms.example.com/v1/messages",
        data=json.dumps({"to": number, "body": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return resp.status == 200
PY
