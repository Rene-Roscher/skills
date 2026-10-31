#!/usr/bin/env bash
set -euo pipefail
mkdir -p src/reports tests
cat > src/reports/cache.py <<'PY2'
"""Monthly report rows, built once and shared through the cache."""
import time

LOCK_TTL = 30
WAIT_TIMEOUT = 5


def wait_for(cache, key, timeout=WAIT_TIMEOUT, step=0.1):
    """Wait until another worker has stored the key, or the timeout passes."""
    waited = 0.0
    while waited < timeout:
        if cache.get(key) is not None:
            return
        time.sleep(step)
        waited += step


def monthly_report(cache, workspace_id, month, build):
    key = f"report:{workspace_id}:{month}"
    cached = cache.get(key)
    if cached is not None:
        return cached["rows"]
    if not cache.add(key + ":lock", "1", ttl=LOCK_TTL):
        # Another worker is building the report; wait for it.
        wait_for(cache, key)
        return cache.get(key)["rows"]
    try:
        rows = build(workspace_id, month)
        cache.set(key, {"rows": rows}, ttl=3600)
        return rows
    finally:
        cache.delete(key + ":lock")
PY2
cat > src/reports/views.py <<'PY2'
from src.reports.cache import monthly_report
from src.reports.build import build_rows


def month_view(request, cache, month):
    # Dashboards of every workspace load this view when the scheduled 06:00 refresh runs.

    rows = monthly_report(cache, request.workspace_id, month, build_rows)
    return {"rows": rows}
PY2
cat > src/reports/build.py <<'PY2'
def build_rows(workspace_id, month):
    """Aggregate the month's bookings. Slow on the first days of a month, when the previous month closes."""
    raise NotImplementedError("reads the bookings database")
PY2
touch src/__init__.py src/reports/__init__.py tests/__init__.py
