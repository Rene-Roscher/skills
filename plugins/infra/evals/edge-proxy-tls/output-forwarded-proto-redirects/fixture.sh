#!/usr/bin/env bash
set -euo pipefail
mkdir -p deploy
cat > deploy/Caddyfile <<'CADDY'
shop.example.com {
	reverse_proxy ingress.internal.example:80
}
CADDY
cat > deploy/ingress-nginx-configmap.yaml <<'YAML'
apiVersion: v1
kind: ConfigMap
metadata: {name: ingress-nginx-controller, namespace: ingress-nginx}
data:
  use-forwarded-headers: "false"
YAML
cat > deploy/app.env <<'ENV'
APP_URL=https://shop.example.com
TRUSTED_PROXIES=*
ENV
