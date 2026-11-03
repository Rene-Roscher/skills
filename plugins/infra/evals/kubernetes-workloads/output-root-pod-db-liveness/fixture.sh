#!/usr/bin/env bash
set -euo pipefail
mkdir -p k8s
cat > k8s/api.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: shop
spec:
  replicas: 3
  selector:
    matchLabels: {app: api}
  template:
    metadata:
      labels: {app: api}
    spec:
      containers:
        - name: api
          image: registry.example.com/shop/api:latest
          ports: [{containerPort: 8080}]
          livenessProbe:
            httpGet: {path: /health, port: 8080}
          readinessProbe:
            httpGet: {path: /health, port: 8080}
YAML
