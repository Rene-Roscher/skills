#!/usr/bin/env bash
set -euo pipefail
git init -q .
printf '.env\n.env.staging\n' > .gitignore
cat > compose.yaml <<'EOF'
name: invoicing
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: invoicing
      POSTGRES_PASSWORD: ${DB_PASSWORD:?set DB_PASSWORD}
      POSTGRES_DB: invoicing
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:14110:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U invoicing -d invoicing"]
      interval: 2s
      retries: 30
volumes:
  pgdata:
EOF
cat > .env.example <<'EOF'
DB_HOST=postgres
DB_PORT=5432
DB_PASSWORD=local-dev-only
EOF
cp .env.example .env
cat > .env.staging <<'EOF'
DB_HOST=db.staging.example.com
DB_PORT=5432
DB_PASSWORD=fixture-not-a-real-password
EOF
