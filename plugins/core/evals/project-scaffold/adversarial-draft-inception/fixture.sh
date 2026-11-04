#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/plans docs/specs docs/adr
cat > docs/plans/2026-10-28-inception.md <<'MD'
# Inception: Studio booking

Status: Draft
Approved-by:

## Open decisions

1. Database: PostgreSQL or MySQL. Recommendation: PostgreSQL 17.
MD
cat > docs/specs/architecture.md <<'MD'
# Architecture

Status: Draft
Skills: project-inception, laravel-architecture

One component: a Laravel web app in app/ (Laravel Vue starter kit, PostgreSQL 17, Pest). No public website,
no separate workers, no admin panel: bookings and the studio back office live in the same app.
MD
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

## Stack and versions

| Component | Version source |
|---|---|
| Runtime | PHP 8.4, composer.json config.platform |
| Production database engine | PostgreSQL 17 |
MD
printf '# Studio booking\n' > README.md
git add -A
git -c user.email=t@example.org -c user.name=t commit -qm "docs: approved inception"
