#!/usr/bin/env bash
set -euo pipefail
mkdir -p k8s
cat > k8s/namespaces.yaml <<'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: shop
---
apiVersion: v1
kind: Namespace
metadata:
  name: reports
YAML
cat > k8s/secrets.yaml <<'YAML'
apiVersion: v1
kind: Secret
metadata: {name: db, namespace: shop}
stringData: {password: example-password-1}
---
apiVersion: v1
kind: Secret
metadata: {name: db-copy, namespace: reports}
stringData: {password: example-password-1}
YAML
