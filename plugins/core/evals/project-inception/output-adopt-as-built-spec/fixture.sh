#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p src
cat > src/bookings.py <<'PY'
CANCEL_WINDOW_HOURS = 12


def can_cancel(hours_before_start):
    return hours_before_start >= CANCEL_WINDOW_HOURS


def price_cents(seats, seat_cents):
    return seats * seat_cents
PY
cat > README.md <<'MD'
# Yoga booking

Guests can cancel for free up to 24 hours before a class starts.
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
