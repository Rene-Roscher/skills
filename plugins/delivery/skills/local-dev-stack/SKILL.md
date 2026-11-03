---
name: local-dev-stack
description: "Sets up and reviews a Docker Compose dev stack that runs beside other projects on one Linux workstation: own host port block on 127.0.0.1, fixed project name, one Makefile with doctor, health-gated startup, one service per process, test-mode providers, tests on the production engine. Use when writing compose files, a dev Makefile or .env.example. Not for production images or Kubernetes."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
paths:
  - "**/compose.yaml"
  - "**/compose.yml"
  - "**/compose.*.yaml"
  - "**/docker-compose*.yml"
  - "**/docker-compose*.yaml"
  - "**/Makefile"
  - "**/justfile"
  - "**/Taskfile.yml"
  - "**/.env.example"
  - "**/.devcontainer/**"
---

# Local dev stack

This skill decides how a project runs on a developer's workstation: which host ports it takes, what its
containers, volumes and networks are called, how one command brings it up in the right order, how each process
is restarted on its own, and what it may reach outside the machine. The setting it assumes is a Linux
workstation, often an Ubuntu desktop, where several projects live side by side, some idle and some running at the
same time. Compose syntax stays in Docker's docs; image contents stay with `container-images`. It prevents the
second project that fails with "address already in use", the reset that wipes another project's database, and
the dev stack that sends a real invoice mail to a customer.

## Applies when / does not apply

- Applies: writing or reviewing `compose.yaml` or `docker-compose*.yml` for local development, a dev `Makefile`,
  `justfile` or `Taskfile.yml`, `.env.example`; adding a service, queue worker or microservice to the local stack;
  "port already allocated", "my other project stopped working", "make up", "reset my local database"; deciding
  how tests run locally.
- Does not apply: what goes into the production image and how it is built (`container-images`); CI jobs
  (`github-actions-hardening`); Kubernetes manifests; production data, which the local stack never touches.

## Rules

Ordered by blast radius. Examples use an invoicing app, a booking system and a project tool.

- [invariant] **The local stack reaches no real third party and no shared data by default.** Mail goes to a
  local catcher such as Mailpit, payments and SMS use the provider's test mode or a stub, webhooks come from the
  provider's CLI or a fixture, and every database, cache and queue host is a service of this compose project.
  Any exception is listed in the project facts as an action that leaves the machine. Why: a dev stack with a live
  key sends real mail, charges real cards or writes to a shared database, and nobody notices until a customer
  does. Test: `make doctor` fails on a live-key marker in `.env` (Stripe marks live keys `sk_live_`, `rk_live_`,
  `pk_live_`); a mail sent by the app appears in the catcher's UI and nowhere else. Source:
  https://docs.stripe.com/keys (key prefixes), https://mailpit.axllent.org/docs/configuration/runtime-options/
  (SMTP 1025, UI 8025) (verified 2026-11-03).
- [invariant] **Resets are explicit and local.** `make down` keeps data; only `make fresh` deletes it, only with
  `CONFIRM=[project name]`, only this project's named volumes, and it refuses when a database or cache host in
  `.env` is not a service of this stack. No alias or target runs `docker compose down -v` without that guard.
  Why: `down --volumes` removes every named volume declared in the compose file, and a reset that follows `.env`
  to a remote host deletes data that is not yours. Test: `make fresh` without `CONFIRM` exits non-zero and
  `docker volume ls` still lists the volumes; with `DB_HOST=db.staging.example.com` it refuses before any
  `down`. Source: https://docs.docker.com/reference/cli/docker/compose/down/ (verified 2026-11-03).
- [invariant] **Every published port binds to 127.0.0.1.** Write `"127.0.0.1:${DB_HOST_PORT:-14110}:5432"`,
  never `"14110:5432"`. Inside the container a server still listens on `0.0.0.0`; the restriction belongs on the
  host side. Why: without a host IP Docker publishes on all IPv4 and IPv6 addresses, and on a desktop with ufw
  the published port is reachable from the network because Docker's rules run before ufw's. Test: every
  `published:` entry in `docker compose --profile '*' config` has `host_ip: 127.0.0.1`; `ss -Htln` shows
  `127.0.0.1:[port]`, never `0.0.0.0:[port]` or `[::]:[port]`. Source:
  https://docs.docker.com/engine/network/port-publishing/,
  https://docs.docker.com/engine/network/packet-filtering-firewalls/ (verified 2026-11-03).
- [invariant] **The project name is set in the committed compose file.** Set top-level `name: invoicing` and
  don't set `COMPOSE_PROJECT_NAME` in `.env.example`. Why: container, volume and network names start with the
  project name, which otherwise defaults to the directory name, so two checkouts called `app` or `backend` share
  volumes and one `down` stops the other. Test: `docker compose config | sed -n 's/^name: //p'` prints the name
  recorded in the project facts; `make doctor` checks it. Source:
  https://docs.docker.com/compose/how-tos/project-name/ (verified 2026-11-03).
- [invariant] **Each project owns a host port block, and no host port is a well-known default.** Never publish
  on 5432, 3306, 6379, 8080, 5173, 80, 443 or similar on the host side; containers keep their default ports and
  services talk to each other on them (`postgres:5432`). The block is recorded in the project facts and in
  `.env.example`. Before choosing one, check the candidate range with `ss -Htln` and against the blocks other
  projects on the machine have recorded, because an idle project holds no ports while it waits. Why: two
  projects that both publish 5432 cannot run at once; the second one fails at start. Test: `make doctor` fails
  when a `*_HOST_PORT` value lies outside the block or is held by a process that is not this stack (reproduced
  with Compose v5.6.1: `failed to bind host port 127.0.0.1:14191/tcp: address already in use`).
- [invariant] **Startup is gated on health, not on sleeps.** Every datastore has a `healthcheck`; services that
  need it use `depends_on` with `condition: service_healthy`; migrations run as a one-shot service that app
  services wait for with `condition: service_completed_successfully`; `make up` runs
  `docker compose up -d --wait`. Why: Compose waits only until a container is running, not until it accepts
  connections, so a worker that starts first crashes or retries on a database that is still booting. Test:
  `make up` exits 0 only when every service is running and healthy and the migrate container exited 0
  (reproduced with Compose v5.6.1); a healthcheck that never passes makes it exit non-zero. Source:
  https://docs.docker.com/compose/how-tos/startup-order/,
  https://docs.docker.com/reference/cli/docker/compose/up/ (verified 2026-11-03).
- [invariant] **One long-running process per service.** Web server, each queue group, the scheduler, the
  websocket server, each microservice and the frontend dev server are separate services, each restartable alone.
  No process manager runs several of them in one container. Why: a stuck mail worker in a shared container means
  restarting the web server too, and its logs are mixed with everything else. Test:
  `docker compose config --services` lists every process named in the project facts;
  `docker compose restart worker-mail` leaves the `web` container's start time unchanged.
- [invariant] **After a code change, restart every long-lived process that loaded the changed code before
  judging the change.** Request-per-process runtimes and dev servers with hot reload pick up edits; queue
  workers, schedulers, websocket servers and compiled services keep the code they started with. Use
  `make restart-workers`, or `docker compose watch` with `sync+restart` for those services. Why: a worker that
  still runs yesterday's code makes a correct fix look broken, or a broken fix look correct. Test: change a log
  line in a job handler, dispatch the job: the old line appears until the worker is restarted. Source:
  https://docs.docker.com/compose/how-tos/file-watch/ (verified 2026-11-03).
- [invariant] **Tests run inside the app container, on the production runtime version, against the production
  database engine.** `make test` uses the dev stage of the production Dockerfile and a separate test database on
  the same engine and major version as production. Why: a host with another minor runtime version or a test run
  on an in-memory engine passes code that fails in production, silently. Test: `make test` prints the runtime
  version from the container and it matches the version pinned for production; the test connection's driver
  names the production engine. The test lanes themselves belong to `test-strategy`.
- [invariant] **Dev secrets live in a gitignored `.env`; `.env.example` is committed and complete.** Every key
  the stack reads appears in `.env.example` with a dev-only value or an empty placeholder, and compose fails
  early on a missing value (`${DB_PASSWORD:?set DB_PASSWORD in .env}`). Why: a key missing from the example
  turns into a half-working stack on the next machine, and a committed `.env` publishes whatever someone pasted
  into it. Test: `git check-ignore -q .env` succeeds; `make doctor` lists keys in `.env.example` missing from
  `.env`. Source: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
  (verified 2026-11-03).
- [default] **One entry point: a Makefile with fixed target names.** `help` (default), `up`, `infra`, `down`,
  `stop`, `logs`, `ps`, `restart-workers`, `migrate`, `seed`, `test`, `shell`, `doctor`, `fresh`, all `.PHONY`.
  The choice of runner is recorded in the project facts with the command to start the stack. A Makefile pays off
  once there is more than one app process (queues, scheduler, websocket server, microservices) or more than one
  step (migrate, seed, test database); for a single app with one database, plain `docker compose up --wait` is
  enough, because the ordering lives in the compose file either way. Alternatives: `just` is a command runner
  without Make's build-system quirks, at the cost of one more binary on every machine; Task (`Taskfile.yml`) is
  YAML and also a separate binary; a dev container (`devcontainer.json` with `dockerComposeFile`) adds editor
  integration on top of the same compose stack and doesn't replace it. Pick one, not two. Trade-off: Make's tab
  indentation and `.PHONY` declarations. Deviate only with an ADR that names this trade-off. Source:
  https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html, https://just.systems/man/en/,
  https://taskfile.dev/, https://containers.dev/implementors/json_reference/ (verified 2026-11-03).
- [default] **A block of 100 ports below 32768, with fixed offsets.** For example 14100 to 14199: `+00` web,
  `+01` frontend dev server, `+02` websocket, `+10` database, `+11` cache, `+20` mail catcher UI, `+30` and up
  for optional services. The next project takes 14200. Why below 32768: Linux picks outgoing ports from
  32768 to 60999 by default, so a block there can be taken by a client connection at the moment the stack starts.
  Trade-off: a fixed layout leaves gaps and needs a list of who owns which block. Deviate only with an ADR that
  names this trade-off. Source: https://docs.kernel.org/networking/ip-sysctl.html (`ip_local_port_range`)
  (verified 2026-11-03).
- [default] **Every service has memory and CPU limits, and no restart policy.** Set `deploy.resources.limits`
  per service and leave `restart` at its default `no`. Why: one leaking worker or file watcher should not slow
  every other project on the machine, and with `always` or `unless-stopped` every stack that was running at
  shutdown comes back at boot. Trade-off: a limit set too low kills a heavy job or migration with an
  out-of-memory error; raise that one service's limit. Deviate only with an ADR that names this trade-off. Test:
  `docker inspect -f '{{.HostConfig.Memory}} {{.HostConfig.RestartPolicy.Name}}' [container]` shows the limit and
  `no` (Compose v5.6.1 applies `deploy.resources.limits` outside Swarm, reproduced 2026-11-03). Source:
  https://docs.docker.com/reference/compose-file/deploy/,
  https://docs.docker.com/engine/containers/start-containers-automatically/ (verified 2026-11-03).
- [default] **Heavy optional services sit behind profiles.** A search engine, an analytics database or a second
  frontend gets `profiles: ["search"]` and starts with `make up PROFILES=search`. Trade-off: a feature that needs
  the profiled service fails until someone enables it, so the app reports a missing optional service clearly.
  Deviate only with an ADR that names this trade-off. Source: https://docs.docker.com/compose/how-tos/profiles/
  (verified 2026-11-03).
- [default] **Data in named volumes, source code in a bind mount.** Database, cache and search data use named
  volumes, which carry the project name; only the source tree is bind-mounted. Trade-off: data is not visible in
  the project folder; inspect it through the service. Deviate only with an ADR that names this trade-off.
  Source: https://docs.docker.com/reference/cli/docker/compose/down/ (named volumes survive `down`) (verified
  2026-11-03).

## Procedure

1. Gate: read `docs/PROJECT-FACTS.md` for the port block, project name and runner. Inventory the compose files,
   `.env.example`, the runner file and the list of production processes (web, queues, scheduler, websocket,
   services). If no block is recorded, list the blocks other projects on the machine use (ask, or read their
   `.env.example`), run `ss -Htln` over the candidate range, and propose a free block.
2. New stack: start from [references/compose-example.md](references/compose-example.md) and
   [references/makefile-and-doctor.md](references/makefile-and-doctor.md). Existing stack: list each rule it
   breaks with the file and line, then fix in the order of the rules.
3. Run `docker compose config -q`, `make doctor`, `make up`, `make doctor` again, `make test`, then `make down`
   and confirm with `docker volume ls` that the data volumes are still there.
4. Record in the project facts: project name, port block and the port table, runner and commands, the processes
   and their services, which providers run in test mode and anything that still leaves the machine.
5. Report per rule which check ran and what it showed, and what was not run (`verify-before-done`).

## Traps

- `COMPOSE_PROJECT_NAME` in the shell or in `.env` overrides `name:` in the compose file without a warning
  (reproduced with Compose v5.6.1). A stale export from another project's shell makes two stacks share volumes.
- Docker Engine before 28.0.0 let hosts on the same L2 segment reach ports published to localhost. Check
  `docker version` on the workstation before relying on the loopback binding (source:
  https://docs.docker.com/engine/network/port-publishing/).
- Database init scripts in `/docker-entrypoint-initdb.d` run only when the data directory is empty. A test
  database added later needs `make fresh` or a manual `CREATE DATABASE`.
- The official PostgreSQL image changed its data path in version 18 (volume at `/var/lib/postgresql`); 17 and
  earlier use `/var/lib/postgresql/data`. A major upgrade with the old mount path loses data on the next
  recreate (source: https://github.com/docker-library/docs/blob/master/postgres/content.md).
- A frontend dev server that writes its own URL into the page (hot-reload socket, asset origin) breaks when the
  host port differs from the container port. Run it on the host port number inside the container too, with a
  strict-port flag; Vite otherwise moves to the next free port silently.
- `ss -ltn` shows only stacks that are running. An idle project still owns its block; check the recorded blocks.
- A compose file copied from production brings `restart: unless-stopped`, published ports without a host IP and
  real provider settings. Review it against every rule above before the first `up`.

## Done when

- `docker compose config -q` passes and `make doctor` exits 0 with the stack up.
- Every published port binds 127.0.0.1 inside the recorded block, and the project name matches the facts.
- `make up` returns only after health; `make test` ran in the container on the production engine.
- `make down` kept the volumes; `make fresh` refused without `CONFIRM` and with a non-local host.
- The project facts list the block, the ports, the runner, the processes and the test-mode providers.

## References

- [references/compose-example.md](references/compose-example.md): load when writing or reviewing a compose file
  or `.env.example`; an invoicing app with datastores, mail catcher, migrate step, workers, scheduler, websocket,
  frontend dev server and an optional profile.
- [references/makefile-and-doctor.md](references/makefile-and-doctor.md): load when writing the Makefile, the
  `doctor` check or the guarded `fresh` target.

## Sources

- https://docs.docker.com/compose/how-tos/project-name/: precedence of `-p`, `COMPOSE_PROJECT_NAME`, `name:`,
  directory name; allowed characters, verified 2026-11-03.
- https://docs.docker.com/reference/compose-file/services/: `ports` host IP default `0.0.0.0`, `depends_on`
  conditions, `healthcheck`, `profiles`, `restart` default `no`, verified 2026-11-03.
- https://docs.docker.com/engine/network/port-publishing/: publishing is insecure by default, loopback binding,
  localhost reachability before Engine 28.0.0, verified 2026-11-03.
- https://docs.docker.com/engine/network/packet-filtering-firewalls/: published ports bypass ufw rules,
  verified 2026-11-03.
- https://docs.docker.com/compose/how-tos/startup-order/: Compose waits for running, not ready, verified
  2026-11-03.
- https://docs.docker.com/reference/cli/docker/compose/up/ and
  https://docs.docker.com/reference/cli/docker/compose/down/: `--wait`, what `down` and `--volumes` remove,
  verified 2026-11-03.
- https://docs.docker.com/compose/how-tos/profiles/, https://docs.docker.com/compose/how-tos/file-watch/,
  https://docs.docker.com/reference/compose-file/deploy/: profiles, watch actions, resource limits, verified
  2026-11-03.
- https://docs.kernel.org/networking/ip-sysctl.html: `ip_local_port_range` default 32768 to 60999, verified
  2026-11-03.
- Reproduced on Docker Engine 29.9.2 with Compose v5.6.1, 2026-11-03: `.env` overriding `name:`, `--wait` with
  a one-shot service, limits applied, loopback binding, port collision error, `fresh` guards, `doctor` checks.
