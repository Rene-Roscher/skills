#!/usr/bin/env bash
set -euo pipefail
mkdir -p app
cat > app/telemetry.py <<'PY'
import logging
import sentry_sdk

sentry_sdk.init(
    dsn="https://public@errors.example.com/1",
    send_default_pii=True,
    max_request_body_size="always",
)

log = logging.getLogger("http")

def log_request(request):
    log.info("request %s %s headers=%s body=%s", request.method, request.url, dict(request.headers), request.body)
PY
