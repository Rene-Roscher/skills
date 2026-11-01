#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
touch src/__init__.py
printf '# no third-party dependencies yet\n' > requirements.txt
cat > src/dates.py <<'PY'
def parse_day(text):
    raise NotImplementedError("parse an ISO date string like 2026-11-01")
PY
