---
description: Asked to add shareable download links for invoices to a small stdlib Python service, the agent must build expiring links with an HMAC over path and expiry from a key outside the source, verify them with a constant-time compare, and add tests that tamper with the link, use it after expiry and use it without a signature, seen failing when the check is disabled. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: invoices/links.py (or similar) signs the invoice path and an expiry with hmac and hashlib.sha256 using a key read from the environment, verify uses hmac.compare_digest, the handler rejects a missing, altered or expired signature, and tests/test_links.py has a tamper test, an expiry test and a missing-signature test that pass; the reply names what the link does not protect against (anyone holding a valid link before it expires).
tags: [security-assurance, output]
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Customers want to share invoice PDFs with their accountant without giving them a login. Add download links they can share, in this service. Keep it simple.
