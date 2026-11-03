#!/usr/bin/env bash
set -euo pipefail
git init -q .
mkdir -p bin
cat > compose.yaml <<'EOF'
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: secret
    ports:
      - "5432:5432"
    restart: always
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    restart: always
  app:
    build: .
    command: ["./bin/app", "serve", "--port=8080"]
    ports:
      - "8080:8080"
    depends_on:
      - db
      - redis
    restart: always
  worker:
    build: .
    command: ["./bin/app", "queue:work"]
    depends_on:
      - db
    restart: always
EOF
cat > README.md <<'EOF'
# Project tool

Runs locally with `docker compose up`. Migrations: `./bin/app migrate`. Tests: `./bin/app test`.
Production runs PostgreSQL 17 and one queue worker next to the web process.
EOF
