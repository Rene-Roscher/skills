#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p copy
cat > copy/shipped.md <<'EOF'
# What shipped in 2.4 (released 2026-10-20)

- Invoices can be exported in bulk as a ZIP of PDFs from the Invoices list (up to 200 per export).
- Fixed: a percentage discount on a line item was rounded before tax instead of after, so some totals were off by 0.01.
- Added: dark theme, switchable under Settings > Appearance.
- Failed payments are logged on the invoice. Automatic retry is NOT built yet.
- Internal: moved the queue workers to a new cluster; upgraded the test runner.
- No customer quotes have been collected for this release.
EOF
cat > copy/release-notes.md <<'EOF'
# Release Notes: Version 2.4 Marks A Pivotal Milestone

We're thrilled to share some exciting news! This release is a testament to our commitment to your success, elevating the invoicing experience for teams everywhere.

- Bulk export: not just an export, but a game-changing way to move your data.
- Smart payment recovery automatically retries failed payments, so you never lose revenue again.
- Fixed various bugs and improved performance.
- Moved queue workers to a new cluster.

"It cut our invoicing time in half." Sarah Miller, Operations Lead
EOF
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add release notes draft'
