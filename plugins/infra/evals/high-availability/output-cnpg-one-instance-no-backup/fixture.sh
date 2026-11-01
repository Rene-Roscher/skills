#!/usr/bin/env bash
set -euo pipefail
mkdir -p db
cat > db/cluster.yaml <<'YAML'
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: invoices-db
  namespace: billing
spec:
  instances: 1
  imageName: ghcr.io/cloudnative-pg/postgresql:17
  storage:
    size: 50Gi
  postgresql:
    parameters:
      max_connections: "200"
YAML
cat > README.md <<'MD'
# invoicing database
Holds all invoices. The business can lose at most 5 minutes of data and must be back within 2 hours of a total cluster loss.
MD
