#!/usr/bin/env bash
set -euo pipefail
mkdir -p monitoring
cat > monitoring/rules.yml <<'YAML'
groups:
  - name: api
    rules:
      - alert: ApiAllDown
        expr: count(up{job="api"} == 1) == 0
        for: 2m
        labels: {severity: critical}
YAML
cat > monitoring/alertmanager.yml <<'YAML'
route:
  receiver: chat
  routes:
    - matchers: [alertname="Watchdog"]
      receiver: "null"
receivers:
  - name: chat
    webhook_configs: [{url: "https://chat.example.com/hook"}]
  - name: "null"
YAML
