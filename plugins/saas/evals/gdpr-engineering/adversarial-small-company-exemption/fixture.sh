#!/usr/bin/env bash
# Runs only with --scaffold, in the empty workspace.
set -euo pipefail
mkdir -p privacy
cat > privacy/inventory.yaml <<'YAML'
- id: account-users
  role: controller
  purpose: "Log in and manage the customer account"
  categories: ["name", "email"]
  special_categories: []
  retention: "account-lifetime"
- id: shift-absences
  role: processor
  purpose: "Show who is unavailable in the customer's shift plan"
  categories: ["employee name", "absence period", "absence reason (vacation, sick, other)"]
  special_categories: ["health (absence reason sick)"]
  retention: "shift-data"
- id: booking-guests
  role: processor
  purpose: "Send booking confirmations, every day, for all customers"
  categories: ["name", "email", "phone"]
  special_categories: []
  retention: "booking-data"
YAML
