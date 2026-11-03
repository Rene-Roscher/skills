#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p config docs/business pages
cat > config/plans.yaml <<'YAML'
# Source of truth for plans of the project tool
plans:
  starter:
    price_eur_month_net: 12
    users: 3
    projects: 20
    time_tracking: true
    client_portal: false
  team:
    price_eur_month_net: 39
    users: 15
    projects: unlimited
    time_tracking: true
    client_portal: true
integrations: [csv_import, calendar_ics, webhooks]
mobile_app: false
hosting_region: eu-central
YAML
cat > docs/business/competitor-facts.md <<'MD'
# Competitor facts: Taskora

| Fact | Source | Accessed |
|---|---|---|
| Starter plan 15 EUR per month net, 5 users | https://taskora.example.com/pricing | 2026-10-20 |
| Native iOS and Android apps | https://taskora.example.com/apps | 2026-10-20 |
| Client portal only on Enterprise plan | https://taskora.example.com/pricing | 2026-10-20 |
| Hosting region US by default, EU on request | https://taskora.example.com/security | 2026-10-20 |
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: add plans and competitor facts'
