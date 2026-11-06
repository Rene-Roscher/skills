#!/bin/sh
# A project whose AGENTS.md carries the no-emoji rule, a plain deploy script and a list of what shipped.
set -eu
mkdir -p copy scripts
cat > AGENTS.md <<'MD'
## Working rules for coding agents

### User-facing text
- Never write a Unicode emoji or pictographic symbol character yourself, anywhere: code, UI strings,
  flags, docs, commit messages, comments, logs, CLI output. Visuals come from the project's icon set
  (for example Lucide) or SVG assets. What a user entered stays as entered.
MD
cat > copy/shipped.md <<'MD'
# Shipped in 2.4

- Bulk export of invoices as CSV from the invoice list.
- Invoices now round each line before summing, matching the tax office's method.
- German and English date formats follow the user's language setting.
MD
cat > scripts/deploy.sh <<'SH'
#!/bin/sh
set -eu
echo "building"
make build
echo "migrating"
php artisan migrate --force
echo "done"
SH
