# Makefile and doctor

## Contents

- Makefile
- scripts/dev/doctor.sh
- What each check catches

Both files were run on Docker Engine 29.9.2, Compose v5.6.1 and GNU Make 4.3 (2026-11-03): `make` lists the
targets, `make fresh` refuses without `CONFIRM` and with a remote `DB_HOST`, and `doctor` failed on a port held
by another process, on `COMPOSE_PROJECT_NAME=other` and on an `sk_live_` value in `.env`.

## Makefile

Recipe lines start with a tab.

```make
# One entry point for the local stack. `make` lists the targets.
SHELL := /bin/bash
.DEFAULT_GOAL := help

PROJECT    := invoicing
COMPOSE    := docker compose
PROFILES   ?=
PROFILE_FLAGS := $(foreach p,$(PROFILES),--profile $(p))
LONG_LIVED := worker-default worker-mail scheduler websocket
TEST_DB    := invoicing_test
RUN        := $(COMPOSE) run --rm --no-deps web

.PHONY: help up infra down stop logs ps restart-workers migrate seed fresh test shell doctor

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

.env:
	cp .env.example .env
	@echo "Created .env from .env.example. Review it, then run the target again."
	@exit 1

up: .env ## Start everything: infra, health, migrations, app processes (PROFILES=search)
	$(COMPOSE) $(PROFILE_FLAGS) up -d --wait --wait-timeout 180
	@$(MAKE) --no-print-directory ps

infra: .env ## Start only the datastores and the mail catcher, wait for health
	$(COMPOSE) up -d --wait --wait-timeout 120 postgres valkey mailpit

down: ## Stop and remove containers; named volumes (the data) stay
	$(COMPOSE) --profile '*' down --remove-orphans

stop: ## Stop containers without removing them
	$(COMPOSE) --profile '*' stop

logs: ## Follow logs, all or one service: make logs S=worker-mail
	$(COMPOSE) logs -f --tail=200 $(S)

ps: ## Services with state, health and published ports
	@$(COMPOSE) --profile '*' ps -a --format 'table {{.Service}}\t{{.State}}\t{{.Health}}\t{{.Ports}}'

restart-workers: ## Restart long-lived processes after a code change
	$(COMPOSE) restart $(LONG_LIVED)

migrate: infra ## Run migrations against the local database
	$(RUN) ./bin/app migrate

seed: infra ## Load development seed data
	$(RUN) ./bin/app db:seed

test: infra ## Run the tests in the app container, on PostgreSQL, in the test database
	$(RUN) env DB_DATABASE=$(TEST_DB) ./bin/app test $(ARGS)

shell: ## Shell in a running service: make shell S=worker-mail
	$(COMPOSE) exec $(or $(S),web) sh

doctor: ## Check config, project name, env, keys, ports and health
	@./scripts/dev/doctor.sh

fresh: ## Delete THIS project's local volumes and start over: make fresh CONFIRM=invoicing
	@test "$(CONFIRM)" = "$(PROJECT)" || { echo "fresh deletes all local data of $(PROJECT). Run: make fresh CONFIRM=$(PROJECT)"; exit 1; }
	@services=" $$($(COMPOSE) --profile '*' config --services | tr '\n' ' ') "; \
	for var in DB_HOST CACHE_HOST; do \
	  host=$$(sed -n "s/^$$var=//p" .env); \
	  case "$$services" in *" $$host "*) ;; *) echo "$$var=$$host is not a service of this stack; fresh refuses."; exit 1;; esac; \
	done
	$(COMPOSE) --profile '*' down --volumes --remove-orphans
	$(MAKE) --no-print-directory up
	$(MAKE) --no-print-directory seed
```

## scripts/dev/doctor.sh

```bash
#!/usr/bin/env bash
# Checks the local stack and exits 1 on any failure. The values below come from docs/PROJECT-FACTS.md.
set -uo pipefail
expected_name="invoicing"
block_start=14100
block_end=14199
live_key_pattern='(sk|rk|pk)_live_'   # add the live-key marker of every provider the project uses

fail=0
bad() { echo "FAIL  $*"; fail=1; }
ok()  { echo "ok    $*"; }

docker info >/dev/null 2>&1 || { echo "FAIL  docker daemon not reachable"; exit 1; }
[ -f .env ] || { echo "FAIL  .env missing: cp .env.example .env"; exit 1; }
docker compose config -q || { echo "FAIL  compose file does not resolve"; exit 1; }
config=$(docker compose --profile '*' config)

name=$(sed -n 's/^name: //p' <<<"$config" | head -n1)
if [ "$name" = "$expected_name" ]; then ok "project name $name"
else bad "project name is '$name', expected '$expected_name' (COMPOSE_PROJECT_NAME in the shell or .env?)"; fi

if git check-ignore -q .env; then ok ".env is gitignored"; else bad ".env is not gitignored"; fi
missing=$(comm -23 <(grep -oE '^[A-Z0-9_]+' .env.example | sort -u) <(grep -oE '^[A-Z0-9_]+' .env | sort -u) | tr '\n' ' ')
if [ -z "$missing" ]; then ok ".env has every key of .env.example"; else bad ".env lacks: $missing"; fi
if grep -qE "$live_key_pattern" .env; then bad "a live provider key is in .env; use test-mode keys"
else ok "no live provider keys"; fi

published=$(grep -c 'published:' <<<"$config")
loopback=$(grep -c 'host_ip: 127.0.0.1' <<<"$config")
if [ "$published" = "$loopback" ]; then ok "all $published published ports bind 127.0.0.1"
else bad "$((published - loopback)) published port(s) not bound to 127.0.0.1"; fi

ours=$(docker compose --profile '*' ps --format '{{.Ports}}')
for var in $(grep -oE '^[A-Z0-9_]+_HOST_PORT' .env.example); do
  port=$(sed -n "s/^$var=//p" .env)
  if [ -z "$port" ] || [ "$port" -lt "$block_start" ] || [ "$port" -gt "$block_end" ]; then
    bad "$var=$port is outside $block_start-$block_end"; continue
  fi
  if [ -n "$(ss -Htln "sport = :$port")" ] && ! grep -q "127.0.0.1:$port->" <<<"$ours"; then
    bad "$var=$port is held by another process (ss -ltnp 'sport = :$port')"
  else ok "$var=$port"; fi
done

while IFS='|' read -r svc state health code; do
  [ -z "$svc" ] && continue
  if [ "$state" = "running" ] && { [ -z "$health" ] || [ "$health" = "healthy" ]; }; then ok "$svc running $health"
  elif [ "$svc" = "migrate" ] && [ "$state" = "exited" ] && [ "$code" = "0" ]; then ok "migrate finished"
  else bad "$svc is $state $health (exit $code): make logs S=$svc"; fi
done < <(docker compose ps -a --format '{{.Service}}|{{.State}}|{{.Health}}|{{.ExitCode}}')

exit "$fail"
```

## What each check catches

| Check | Catches |
|---|---|
| project name | a `COMPOSE_PROJECT_NAME` in the shell or `.env` that overrides `name:` |
| `.env` gitignored | a secrets file one `git add .` away from the repository |
| key parity | a key added to `.env.example` that this machine's `.env` lacks |
| live keys | a production provider key in a dev stack |
| loopback | a published port without `127.0.0.1` |
| port block | a port outside the recorded block, or held by another project or process |
| health | a service that is unhealthy, restarting or exited, and a migrate step that failed |

`doctor` reads `.env` only locally and prints key names, never values.
