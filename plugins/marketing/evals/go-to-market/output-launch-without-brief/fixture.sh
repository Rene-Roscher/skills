#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p config
cat > config/plans.yaml <<'YAML'
plans:
  solo:
    price_eur_month_net: 15
  practice:
    price_eur_month_net: 45
YAML
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: add plans'
