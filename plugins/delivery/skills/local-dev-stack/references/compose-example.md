# Compose example: invoicing app

## Contents

- Port table
- compose.yaml
- .env.example
- Test database init script
- Notes

The example was checked with `docker compose config -q` and its infrastructure part started with
`docker compose up -d --wait` on Docker Engine 29.9.2 and Compose v5.6.1 (2026-11-03). The app commands
(`./bin/app ...`) stand for whatever the project's framework uses; replace them.

## Port table

Block 14100 to 14199, recorded in `docs/PROJECT-FACTS.md` and `.env.example`.

| Offset | Host port | Service | Container port |
|---|---|---|---|
| +00 | 14100 | web | 8080 |
| +01 | 14101 | vite (frontend dev server) | 14101, same number on purpose |
| +02 | 14102 | websocket | 8081 |
| +10 | 14110 | postgres | 5432 |
| +11 | 14111 | valkey | 6379 |
| +20 | 14120 | mailpit UI | 8025 (SMTP 1025 stays internal) |
| +30 | 14130 | search (profile `search`) | 7700 |

## compose.yaml

```yaml
# Local development stack for the invoicing app. Not used in production.
# Host port block: 14100-14199 (recorded in docs/PROJECT-FACTS.md and .env.example).
name: invoicing

x-app: &app
  build:
    context: .
    target: dev            # dev stage of the production Dockerfile: same runtime version
  image: invoicing-app:dev
  env_file: .env
  volumes:
    - ./:/srv/app          # source code: bind mount
  depends_on:
    postgres:
      condition: service_healthy
    valkey:
      condition: service_healthy
    migrate:
      condition: service_completed_successfully
  deploy:
    resources:
      limits:
        memory: 512M
        cpus: "1.0"

services:
  postgres:
    image: postgres:17     # same major version as production
    environment:
      POSTGRES_USER: invoicing
      POSTGRES_PASSWORD: ${DB_PASSWORD:?set DB_PASSWORD in .env}
      POSTGRES_DB: invoicing
    volumes:
      - pgdata:/var/lib/postgresql/data      # 18 and later: /var/lib/postgresql
      - ./docker/postgres/init:/docker-entrypoint-initdb.d:ro
    ports:
      - "127.0.0.1:${DB_HOST_PORT:-14110}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U invoicing -d invoicing"]
      interval: 2s
      timeout: 3s
      retries: 30
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"

  valkey:
    image: valkey/valkey:8
    volumes:
      - valkeydata:/data
    ports:
      - "127.0.0.1:${CACHE_HOST_PORT:-14111}:6379"
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 2s
      timeout: 3s
      retries: 30
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: "0.5"

  mailpit:
    image: axllent/mailpit:v1.27
    environment:
      MP_SMTP_AUTH_ACCEPT_ANY: "1"
      MP_SMTP_AUTH_ALLOW_INSECURE: "1"
    ports:
      - "127.0.0.1:${MAIL_UI_HOST_PORT:-14120}:8025"   # SMTP stays internal: mailpit:1025
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: "0.25"

  migrate:                 # one-shot: runs on every up, exits 0, then the app starts
    <<: *app
    command: ["./bin/app", "migrate"]
    depends_on:
      postgres:
        condition: service_healthy

  web:
    <<: *app
    command: ["./bin/app", "serve", "--host=0.0.0.0", "--port=8080"]
    ports:
      - "127.0.0.1:${APP_HOST_PORT:-14100}:8080"
    healthcheck:
      test: ["CMD", "./bin/app", "health"]
      interval: 5s
      timeout: 3s
      retries: 30

  worker-default:
    <<: *app
    command: ["./bin/app", "queue:work", "--queue=default"]

  worker-mail:
    <<: *app
    command: ["./bin/app", "queue:work", "--queue=mail"]

  scheduler:
    <<: *app
    command: ["./bin/app", "schedule:run-loop"]

  websocket:
    <<: *app
    command: ["./bin/app", "websocket:serve", "--host=0.0.0.0", "--port=8081"]
    ports:
      - "127.0.0.1:${WS_HOST_PORT:-14102}:8081"

  vite:
    image: node:22
    working_dir: /srv/app
    volumes:
      - ./:/srv/app
    # Same port number inside and outside: the dev server writes its own URL into pages.
    command: ["npx", "vite", "--host", "0.0.0.0", "--port", "${VITE_HOST_PORT:-14101}", "--strictPort"]
    ports:
      - "127.0.0.1:${VITE_HOST_PORT:-14101}:${VITE_HOST_PORT:-14101}"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"

  search:                  # heavy and optional: make up PROFILES=search
    image: getmeili/meilisearch:v1.15
    profiles: ["search"]
    environment:
      MEILI_ENV: development
      MEILI_MASTER_KEY: ${SEARCH_KEY:?set SEARCH_KEY in .env}
    volumes:
      - searchdata:/meili_data
    ports:
      - "127.0.0.1:${SEARCH_HOST_PORT:-14130}:7700"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "1.0"

volumes:
  pgdata:
  valkeydata:
  searchdata:
```

## .env.example

```dotenv
# Copy to .env (gitignored). Dev-only values; nothing here works outside this machine.
# Host port block for this project: 14100-14199.
APP_HOST_PORT=14100
VITE_HOST_PORT=14101
WS_HOST_PORT=14102
DB_HOST_PORT=14110
CACHE_HOST_PORT=14111
MAIL_UI_HOST_PORT=14120
SEARCH_HOST_PORT=14130

# Inside the compose network, services use their default ports.
DB_HOST=postgres
DB_PORT=5432
DB_DATABASE=invoicing
DB_TEST_DATABASE=invoicing_test
DB_USERNAME=invoicing
DB_PASSWORD=local-dev-only
CACHE_HOST=valkey
MAIL_HOST=mailpit
MAIL_PORT=1025
SEARCH_KEY=local-dev-only-search-key

# Third parties: test mode only. doctor refuses live keys.
PAYMENTS_SECRET_KEY=sk_test_replace_me
```

## Test database init script

`docker/postgres/init/01-test-database.sql`:

```sql
-- Runs only when the data volume is empty. The test suite uses its own database on the same engine.
CREATE DATABASE invoicing_test OWNER invoicing;
```

## Notes

- `x-app` is a Compose extension field; the anchor keeps the app services identical apart from their command.
  `migrate` overrides `depends_on`, because it must not wait for itself.
- `migrate` runs on every `up` and must be idempotent. App services start only after it exited 0.
- The app services have no host port except `web` and `websocket`. Workers and the scheduler need none.
- Mailpit's image defines its own health check (`/mailpit readyz`, observed in `docker inspect` of v1.27), so no
  `healthcheck` is written for it here.
- The images are pinned to a major or minor tag for readability. Pin them the way `container-images` describes if
  the project pins dev images too.
- To add a microservice, copy the `web` block with its own build context, give it the next free offset if it
  needs a host port, and add it to `LONG_LIVED` in the Makefile if it does not reload code.
