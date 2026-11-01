#!/usr/bin/env bash
set -euo pipefail
mkdir -p k8s
cat > k8s/checkout.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: checkout
  namespace: shop
  labels:
    app: checkout
    tier: critical
spec:
  replicas: 1
  selector:
    matchLabels:
      app: checkout
  template:
    metadata:
      labels:
        app: checkout
    spec:
      containers:
        - name: checkout
          image: registry.example.com/shop/checkout:1.4.2
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: checkout
  namespace: shop
spec:
  selector:
    app: checkout
  ports:
    - port: 80
      targetPort: 8080
YAML
cat > README.md <<'MD'
# shop manifests
The checkout service takes payments and must stay up during node upgrades. Cluster has three nodes in three zones.
MD
