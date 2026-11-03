#!/usr/bin/env bash
set -euo pipefail
mkdir -p app
cat > app/settings.py <<'PY'
DEFAULTS = {"reminders_enabled": True}


def reminders_enabled(tenant) -> bool:
    value = tenant.settings.get("reminders_enabled")
    return DEFAULTS["reminders_enabled"] if value is None else value
PY
cat > app/jobs.py <<'PY'
from app.settings import reminders_enabled


def send_due_reminders(tenant, bookings, sms):
    if not reminders_enabled(tenant):
        return
    for booking in bookings:
        sms.send(booking.phone, "Reminder")
PY
cat > app/ui_props.py <<'PY'
def shared_props(tenant, user):
    return {
        "tenant_name": tenant.name,
        "user_name": user.name,
        "reminders_enabled": tenant.settings.get("reminders_enabled", False),
    }
PY
