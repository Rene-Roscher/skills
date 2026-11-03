#!/usr/bin/env bash
set -euo pipefail
mkdir -p voice
cat > voice/script.json <<'JSON'
{"segments": [
  {"id": "l01", "text": "Friday, 6 pm. A client is angry.", "spoken": "Friday, 6 pm. A client is angry."},
  {"id": "l02", "text": "Their invoice was due on Monday.", "spoken": "Their invoice was due on Monday."}
]}
JSON
cat > voice/transcript.json <<'JSON'
{"chunks": [
  {"timestamp": [0.0, 2.1], "text": "Friday, 6 pm. A client is angry."},
  {"timestamp": [2.1, 4.4], "text": "Their invoice was due on Monday."},
  {"timestamp": [4.4, 5.0], "text": "Thank you."}
]}
JSON
