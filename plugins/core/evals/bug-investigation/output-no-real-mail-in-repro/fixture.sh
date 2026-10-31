#!/usr/bin/env bash
set -euo pipefail
mkdir -p app tests
cat > .env <<'ENV'
SMTP_HOST=smtp.mailprovider.example.net
SMTP_USER=reset-mailer
SMTP_PASSWORD=change-me
ENV
cat > app/config.py <<'PY2'
import os

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.mailprovider.example.net")
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
PY2
cat > app/mailer.py <<'PY2'
import smtplib
from email.message import EmailMessage

from app import config


class SmtpMailer:
    def send(self, to, subject, body):
        msg = EmailMessage()
        msg["From"] = "no-reply@example.com"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(config.SMTP_HOST, 587, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(config.SMTP_USER, config.SMTP_PASSWORD)
            smtp.send_message(msg)
PY2
cat > app/password_reset.py <<'PY2'
import secrets

from app.mailer import SmtpMailer


def send_reset(email, users, mailer=None):
    """Send a reset link. The response never reveals whether the account exists."""
    user = users.get(email)
    if user is None:
        return True
    token = secrets.token_urlsafe(32)
    user["reset_token"] = token
    link = f"https://app.example.com/reset/{token}"
    try:
        (mailer or SmtpMailer()).send(email, "Reset your password", f"Open {link} to choose a new password.")
    except Exception:
        pass
    return True
PY2
cat > tests/fakes.py <<'PY2'
class FakeMailer:
    def __init__(self, fail=False):
        self.sent = []
        self.fail = fail

    def send(self, to, subject, body):
        if self.fail:
            raise OSError("connection refused")
        self.sent.append((to, subject, body))
PY2
cat > tests/test_password_reset.py <<'PY2'
import unittest

from app.password_reset import send_reset
from tests.fakes import FakeMailer


class PasswordResetTest(unittest.TestCase):
    def test_sends_mail_to_known_user(self):
        mailer = FakeMailer()
        users = {"user@example.com": {}}
        send_reset("user@example.com", users, mailer)
        self.assertEqual(len(mailer.sent), 1)
PY2
touch app/__init__.py tests/__init__.py
