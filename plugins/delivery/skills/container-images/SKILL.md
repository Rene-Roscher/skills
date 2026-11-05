---
name: container-images
description: "Builds small, reproducible, safe container images: multi-stage, distroless bases pinned by digest, non-root, no secrets in layers, smoke test, scan, sign. Use when writing or reviewing a Dockerfile, .dockerignore, compose or bake file, or asked to containerize, shrink an image, go distroless or pass a build-time token. Not for Kubernetes manifests or CI permissions (github-actions-hardening)."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Container images

This skill decides what goes into an image, how it is built, and what must be proven before a tag points at it:
no secrets in layers or attestations, a numeric non-root user, pinned inputs, frozen dependency installs, a smoke
test of the exact artifact, and signatures that something verifies. Dockerfile syntax and BuildKit options stay in
Docker's docs. This skill keeps the decisions, the check for each, and the traps. It prevents an image that leaks a
build token, crash-loops under the cluster's security settings, or ships unverified.

## Applies when / does not apply

- Applies: writing or reviewing a Dockerfile, Containerfile, `.dockerignore`, compose or bake file; the image build,
  scan, push and signing steps in CI; choosing a base image; moving to distroless; passing a credential into a
  build; acting on image scanner findings.
- Does not apply: Kubernetes manifests, pod `securityContext` and probe configuration in the cluster; the job's
  permissions, triggers and runners (`github-actions-hardening`); starting containers for local development.
  When a `docker/build-push-action` step is in a workflow, both skills apply: this one owns the image, the other the
  job.

## Rules

Ordered by blast radius.

- [invariant] **No secret reaches the image, its metadata or its attestations.** Build-time credentials go through
  BuildKit secret mounts (`RUN --mount=type=secret,id=npm_token,env=NPM_TOKEN ...`, or `target=` a file), in CI
  through build-push-action's `secrets:` or `secret-envs:` inputs. Never `ARG` or `ENV` for tokens, keys or
  passwords, not even in a build stage that is discarded; runtime secrets are injected when the container starts.
  Why: `ARG` and `ENV` values persist in the image, provenance in `mode=max` records build-argument values, and
  build-push-action adds `mode=max` provenance automatically when the repository is public, so a repository that
  goes public starts publishing them. Secret mounts are never included in provenance. Test: a Dockerfile with
  `# check=error=true` and `ARG NPM_TOKEN` fails `docker build --check` with `SecretsUsedInArgOrEnv` (Docker 29.9.2,
  Buildx 0.38.1, 2026-10-31); `docker history --no-trunc` and `docker inspect` of the built image show no
  secret-looking values. Source: https://docs.docker.com/build/building/secrets/,
  https://docs.docker.com/build/ci/github-actions/attestations/,
  https://docs.docker.com/build/metadata/attestations/slsa-provenance/ (verified 2026-10).
- [invariant] **The build context carries no secrets or VCS data.** Every build context has an ignore file,
  preferably in allowlist form (`**` first, then exceptions such as `!src`). It excludes at least `.env*`,
  `.git`, private keys, cloud credential files and local overrides. A Dockerfile-specific ignore file (`Dockerfile.dockerignore`,
  `[name].Dockerfile.dockerignore`) replaces the root `.dockerignore` for that build, so it carries every exclusion
  itself. Why: `COPY . .` puts whatever the ignore file lets through into a layer. Test: with a root `.dockerignore`
  listing `.env*` and a `Dockerfile.dockerignore` listing only `.git`, `COPY . /ctx/` copies `.env.canary` into the
  image (Docker 29.9.2, reproduced 2026-10-31); in CI, a canary `.env.ci-canary` and `.git/ci-canary` created before
  the build must be absent from `docker export` of the image. Source:
  https://docs.docker.com/build/concepts/context/ (the specific file "takes precedence") (verified 2026-10).
- [invariant] **The runtime stage runs as a numeric non-root user.** The final stage sets `USER [uid]:[gid]` with
  numbers, never a name and never 0. Read the base image's non-root UID from its config instead of assuming it.
  Why: under `runAsNonRoot` the kubelet cannot verify a named user and refuses to start the container
  (https://github.com/kubernetes/kubernetes/pull/56503), while a numeric UID can be checked. Test:
  `docker inspect -f '{{.Config.User}}' [image]` matches `^[1-9][0-9]*(:[0-9]+)?$`. Source:
  https://docs.docker.com/build/building/best-practices/ (verified 2026-10).
- [invariant] **Base images are pinned by digest, and an updater owns the pins.** Every external `FROM` is a
  literal `image:tag@sha256:[digest]` line with no `ARG` indirection, because the updaters' docs don't say they
  follow it. Dependabot (`docker` ecosystem) and Renovate (`docker:pinDigests`) are equally valid, and the updater
  covers every directory that holds a Dockerfile. Never a digest without an updater; a pin moved for a security
  reason names the advisory in the commit. Why: a floating tag changes the base without review, and a digest nobody
  updates opts out of security fixes. Test: the Dockerfile checker fails a `FROM` that is not `scratch`, not a stage
  name and has no `@sha256:`, and a Dockerfile directory missing from the updater config. Source:
  https://docs.docker.com/build/building/best-practices/, https://docs.renovatebot.com/docker/ (verified 2026-10).
- [invariant] **Every downloaded artifact is pinned and checksum-verified.** No download piped into a shell and no
  vendor setup script run from the network. Fetch from a versioned release URL and verify it
  (`ADD --checksum=sha256:[hex] [url] [dest]`, or `sha256sum -c`). Global package installs name an exact version.
  A `RUN` line with a pipe runs with pipefail: `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` in Debian-based
  stages, `set -o pipefail &&` where `/bin/sh` is busybox. Why: a piped script runs whatever the server returns at
  build time, unreviewed, in every image. Test: the checker fails a fetch command piped into a shell and
  `npm install -g` without `@version`; `sh -c 'set -o pipefail'` fails with "Illegal option" on
  `debian:bookworm-slim` (dash 0.5.12) and passes on Alpine (busybox), reproduced 2026-10-31. Source:
  https://docs.docker.com/build/building/best-practices/ (verified 2026-10).
- [invariant] **Dependency installs are lockfile-only and frozen.** `npm ci`; `pnpm install --frozen-lockfile` and
  `yarn install --immutable` written out, because both tools tie their frozen default to CI detection and a
  `docker build` step doesn't inherit the runner's `CI` variable; `composer install` against a committed
  `composer.lock`; `pip install --require-hashes`; Go modules with a committed `go.sum`. No image build without a
  lockfile, and lockfiles change only with the package-manager version CI uses. Why: a frozen install fails on drift
  instead of shipping a different dependency tree. Test: the checker fails `npm install`, `yarn install` without
  `--immutable`, and a manifest copied without its lockfile; `composer validate` fails on a stale lock. Source:
  https://docs.npmjs.com/cli/v11/commands/npm-ci, https://pnpm.io/cli/install, https://yarnpkg.com/cli/install,
  https://pip.pypa.io/en/stable/topics/secure-installs/, https://getcomposer.org/doc/03-cli.md (verified 2026-10).
- [invariant] **The image you test is the image you ship, and an image is done only after it ran.** A Dockerfile
  that builds is not finished. CI builds an explicit `target` (or the production stage is last), and a smoke job
  runs that exact image under production constraints before any tag points at it: `--read-only`, one `--tmpfs` per
  declared writable path with the runtime user's `uid`, `gid` and the narrowest `mode` that works, `--cap-drop=ALL`,
  `--security-opt=no-new-privileges`, the numeric user and the production entrypoint. It walks every entry path:
  the default start reaches healthy (the image `HEALTHCHECK` status, or the probe endpoint) and answers one real
  request; arguments given to `docker run [image] [args]` reach the process, so a wrapper script ends in
  `exec "$@"`; every other documented mode (worker, scheduler, migrate, one-off command) starts the same way; the
  scan runs on the result. After a base or runtime change, the test suite runs inside the final image. Why: an
  untargeted build of a Dockerfile whose last stage is `dev` ships the dev image; an entrypoint that drops its
  arguments, a tmpfs the runtime user cannot write and a proxy directive the binary rejects all build cleanly and
  fail only when the container starts. Test: the smoke job is a `needs:` dependency of the push step; a seeded-bad
  image that writes under its app directory fails it, and so does one whose entrypoint ignores its arguments
  (`docker run --rm [image] [binary] --version` must print the version, not start the server). Source:
  https://docs.docker.com/reference/cli/docker/container/run/ (`--tmpfs`, `--read-only`) (verified 2026-11-05);
  `--tmpfs /data:uid=10001,gid=10001,mode=0700` under `--read-only --user 10001:10001` gives a writable `/data`
  owned by 10001 with mode 700, while the default tmpfs is root-owned with mode 1777 (Docker 29.9.2, reproduced
  2026-11-05).
- [invariant] **No development dependencies or interactive tooling in the runtime image.** Production installs
  exclude development dependencies (`composer install --no-dev`, `npm ci --omit=dev`, `pnpm install --prod`), and
  packages that open an interactive shell into the application (REPLs such as Laravel Tinker or PsySH, debuggers,
  profilers, test runners, fakers) are absent even when the framework skeleton lists them as production
  dependencies. Why: a REPL in the image runs arbitrary code with the application's secrets for anyone who reaches
  `docker exec`, and `--no-dev` does not remove a package listed under `require`; the Laravel skeleton and its
  starter kits list `laravel/tinker` there. Test: the package inventory read from the built image
  (`vendor/composer/installed.json`, `node_modules/.package-lock.json`, `go version -m [binary]`) contains no
  entry of a committed denylist, and a seeded-bad build with a denylisted package fails the check. Source:
  https://getcomposer.org/doc/03-cli.md (`--no-dev`), https://raw.githubusercontent.com/laravel/vue-starter-kit/main/composer.json
  (`laravel/tinker` under `require`) (verified 2026-11-05).
- [invariant] **Every long-running process is supervised, reports its health and survives a kill test.** A web
  server, queue worker, scheduler or consumer runs as its own container under the orchestrator's restart policy,
  or, when several processes must share a container, under a real process supervisor; never under a shell loop
  (`while true; do ...; sleep 60; done`), which hides crashes, swallows signals and never reports unhealthy. Each
  one exposes health that reflects whether it does its work: an HTTP probe for a server, a heartbeat (a timestamp
  the work loop updates, checked against a maximum age) for workers and schedulers. A scheduler follows its
  framework's production instructions, not its development command. Why: a process that died or hangs behind a
  loop looks running to the orchestrator, so nothing restarts it and nobody is told. Test: kill the main process
  from the host (`kill -9 "$(docker inspect -f '{{.State.Pid}}' [container])"`) and watch the restart count rise
  and the health go from unhealthy back to healthy; stop the work loop without killing the process and watch the
  heartbeat check turn red within its budget. Source:
  https://docs.docker.com/engine/containers/start-containers-automatically/ (a manually stopped container is not
  restarted) (verified 2026-11-05); with `--restart=on-failure`, a host `kill -9` of the main process restarts the
  container and `docker kill` does not (Docker 29.9.2, reproduced 2026-11-05).
- [invariant] **Whatever is signed is verified before it runs.** If images are signed, a gate you control checks
  the signature and its identity (repository, workflow file, release ref, OIDC issuer) before a container starts,
  and deploy references are digests. Why: a signature nobody checks proves nothing. Test: a policy test in the
  deployment repository rejects an unsigned image and an image signed by another workflow or ref; deploy manifests
  contain `@sha256:`. Source: https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_verify.md (identity and
  issuer are required for keyless verification) (verified 2026-10).
- [default] **Verification runs at admission.** Prefer a cluster admission policy, for example Kyverno
  `ImageValidatingPolicy` or Sigstore's policy-controller, over a check in a deploy script. Trade-off: one more
  cluster component and policy to maintain; GitOps-side verification or a deploy step running `cosign verify` with
  an anchored identity are the alternatives where no admission controller runs. Deviate only with an ADR that names
  this trade-off. Source: https://kyverno.io/docs/policy-types/image-validating-policy/ (verified 2026-10).
- [default] **Sign by digest, attest, then tag.** Push by digest, sign `IMAGE@DIGEST` keyless with cosign, attach
  SBOM and provenance attestations, then create the tags and verify in the same job with an anchored
  `--certificate-identity-regexp` and `--certificate-oidc-issuer https://token.actions.githubusercontent.com`.
  Why: a tag can move after signing, and tags created first leave a window in which `latest` is pullable and
  unsigned. Trade-off: a longer release job and a push-by-digest build setup. Deviate only with an ADR that names
  this trade-off. Source: https://github.com/sigstore/cosign/blob/v3.1.4/README.md ("Always sign images based on
  their digest"), https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
  (verified 2026-10).
- [default] **Multi-stage onto a minimal runtime, after an inventory of what the runtime executes.** Build stages
  hold toolchains; the runtime stage holds the artifact and what the process needs at run time. Prefer distroless
  (`static` for static binaries, `cc` for glibc and libstdc++ needs, the language variants) or an equivalent
  minimal hardened base, and a slim distribution base when the app must spawn a shell. Trade-off: no shell for
  debugging in production, and system files (TLS and OpenSSL configuration, locales) must be copied deliberately.
  Deviate only with an ADR that names this trade-off. Test: scanner finding counts before and after are recorded in
  the change; a guard lists the executables in the final image against a committed allowlist. Source:
  https://docs.docker.com/build/building/best-practices/, https://github.com/GoogleContainerTools/distroless
  (verified 2026-10).
- [default] **Exec-form entrypoint with the application as PID 1.** `ENTRYPOINT ["/app/server"]` with no `sh -c`
  wrapper; a minimal init (tini, or the runtime's `--init`) only when the process forks children it does not reap;
  shutdown on SIGTERM is tested. Why: in shell form the executable doesn't receive signals, so every stop ends in
  SIGKILL after the grace period. Trade-off: no shell variable expansion in the entrypoint. Deviate only with an ADR
  that names this trade-off. Test: with `check=error=true`, a shell-form `CMD` fails `docker build --check` with
  `JSONArgsRecommended`; `docker stop -t 10` returns within budget. Source:
  https://docs.docker.com/reference/dockerfile/#entrypoint, https://docs.docker.com/build/checks/ (verified 2026-10).
- [default] **The image runs with a read-only root filesystem and without file capabilities.** Nothing writes
  outside declared paths, and application files belong to root and are read-only for the runtime user. Binaries
  carry no file capabilities unless the deployment grants them; for an optional capability, publish a variant
  without it and assert in the build that the default variant has none. Why: code the runtime user can rewrite lets
  an exploit persist, and a binary whose file capabilities the bounding set lacks fails `execve` with EPERM, so the
  container crash-loops. Trade-off: frameworks that write caches next to their code need those paths moved or
  pre-built. Deviate only with an ADR that names this trade-off. Source:
  https://man7.org/linux/man-pages/man7/capabilities.7.html (verified 2026-10).
- [default] **Health comes from the orchestrator's probes; an image `HEALTHCHECK` serves Docker users.** On
  Kubernetes, liveness checks only that the process is alive and never a dependency, readiness says whether this
  instance can serve, and startup probes cover slow initialization. An image `HEALTHCHECK` runs the binary's own
  health subcommand in exec form; curl or wget are not installed for it. Trade-off: Docker-only users get no health
  status unless the binary has a health subcommand. Deviate only with an ADR that names this trade-off. Source:
  https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/ (verified 2026-10).
- [default] **Multi-arch by cross-compilation, only for architectures something deploys.** Build stages use
  `FROM --platform=$BUILDPLATFORM` and map `TARGETOS` and `TARGETARCH`; no hard-coded `GOARCH`. Single-arch is a
  recorded decision. Trade-off: cross-compilation setup per language (cgo needs a cross toolchain). Deviate only with
  an ADR that names this trade-off. Test: `docker buildx imagetools inspect` lists exactly the intended platforms.
  Source: https://docs.docker.com/build/building/multi-platform/ (verified 2026-10).
- [default] **Scan before publish and keep scanning what runs.** Scan the built image with a pinned scanner and
  fail on fixable HIGH and CRITICAL findings (`trivy image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed`);
  every ignore entry carries a reason and an expiry date. A fixable finding in a base-image package is resolved in
  this order: drop the package if the runtime does not need it, move the base digest if upstream has rebuilt,
  otherwise upgrade only that package in the runtime stage (`apk add --no-cache --upgrade [package]`,
  `apt-get install --only-upgrade [package]`) with a comment naming the advisory, removed at the next base bump.
  Re-scan deployed digests on a schedule. Trade-off: a new advisory can block an unrelated release until it is
  fixed or ignored with a reason. Deviate only with an ADR that
  names this trade-off. Source: https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/configuration/filtering.md
  (verified 2026-10).
- [default] **Builds are reproducible and labelled.** `SOURCE_DATE_EPOCH` from the commit time, `rewrite-timestamp=true`
  on the image exporter (BuildKit 0.13 or later), the toolchain pinned to a patch version in one place that CI and
  the build stage share, and the OCI labels `org.opencontainers.image.source`, `.revision` and `.version`.
  Trade-off: pinned toolchains need updates like any other pin. Deviate only with an ADR that names this trade-off.
  Test: build the same commit twice and compare the digests. Source:
  https://github.com/moby/buildkit/blob/master/docs/build-repro.md (verified 2026-10).
- [default] **Runtime images contain no development artifacts.** No source maps, tests, docs, compilers or
  package-manager caches; static assets for a CDN come from a separate `FROM scratch AS assets` stage. Trade-off:
  error tracking that needs source maps gets them uploaded at build time through a secret mount, not shipped.
  Deviate only with an ADR that names this trade-off. Test: `docker export` of a container created from the image,
  piped to `tar -t | grep -E '\.map$'`, prints nothing.

## Procedure

1. Gate: inventory every Dockerfile, ignore file and build context, and the build, push and signing steps in CI.
   For each image: bases, stages, final `USER`, entrypoint, build-time credentials, downloads, installs, target.
2. New image: start from the baseline in references. Runtime change (new base, distroless): do the runtime
   inventory first, with the stack notes for the language.
3. Apply the invariants, then the defaults.
4. Run `docker build --check`, build the production target, then run it: start the container with the production
   constraints, pass arguments through the entrypoint, start every documented mode, wait for healthy, read the
   package inventory, kill the main process once, and scan, as in the image tests reference. Only then call the
   image done.
5. For signing, coordinate the CI job with `github-actions-hardening` (permissions, trigger, runner) and write the
   verification gate on the deployment side.
6. Check flags and version-bound behaviour against current docs before stating them (`evidence-before-claims`).
   An option you have not seen in the docs is unverified, and so is any flag a user proposes.
7. Report per rule which check ran and what it showed, and what was not run (`verify-before-done`).

## Traps

- On a base without `/bin/sh`, every library call that runs a command line through a shell fails at run time, not
  at build time. Search the code for shell-spawning calls before switching.
- The `:debug` distroless variants add a busybox shell and its applets. Keep them out of production tags.
- A missing OpenSSL configuration file can surface as a `false` return value instead of an error. PHP's
  `openssl_pkey_new()` returns `false` when `OPENSSL_CONF` points at a missing file (PHP 8.3.10 and 8.4.26,
  reproduced 2026-10-31), so only the test suite inside the final image shows it.
- `docker kill` and `docker stop` count as a manual stop, so the restart policy does not apply and a kill test done
  that way proves nothing. Kill the main process from the host instead.
- A wrapper entrypoint script that ends in `exec php-fpm` (or any fixed command) instead of `exec "$@"` silently
  ignores every argument; the container starts the server whatever you ask it to run.
- `composer install --no-dev` keeps packages listed under `require`; a skeleton that lists a REPL there ships it.
- Build stages on Debian-based images run `RUN` through dash, which rejects `set -o pipefail` and fails the build.
  Switch the stage's `SHELL` to bash instead of deleting pipefail.

## Done when

- `docker build --check` passes with `check=error=true` for every Dockerfile.
- The Dockerfile checker passes on the repository and fails on its seeded-bad fixture.
- The smoke test ran the production target with `--read-only`, tmpfs mounts owned by the runtime user,
  `--cap-drop=ALL`, `no-new-privileges` and the numeric user; it reached healthy, passed arguments through the
  entrypoint, started every documented mode, and the canary, source-map and package-denylist checks found nothing.
- Every long-running process came back after a host kill of its main process, with its health turning red and
  green again.
- The scan ran at a pinned version, and every ignore entry has a reason and an expiry.
- If images are signed: the release verifies its own signature, and a deployment-side policy test rejects unsigned
  and foreign-signed images.
- Every Dockerfile directory is covered by the updater.

## References

- [references/dockerfile-baseline.md](references/dockerfile-baseline.md): load when writing a new Dockerfile; the
  annotated multi-stage template.
- [references/base-images-and-updates.md](references/base-images-and-updates.md): load when choosing a base,
  writing digest pins, configuring Dependabot or Renovate for images, or handling a language security release.
- [references/build-secrets.md](references/build-secrets.md): load when any token, key or credential is needed at
  build time.
- [references/build-context.md](references/build-context.md): load when writing ignore files or setting up the
  context canary.
- [references/minimal-runtimes.md](references/minimal-runtimes.md): load when moving to distroless or another
  minimal base.
- [references/signals-and-health.md](references/signals-and-health.md): load for entrypoints, PID 1, init, and
  `HEALTHCHECK` versus orchestrator probes.
- [references/multi-arch.md](references/multi-arch.md): load when `platforms` has more than one entry.
- [references/sign-attest-verify.md](references/sign-attest-verify.md): load for signing, SBOM, provenance, the
  verify step and deployment-side verification.
- [references/image-tests.md](references/image-tests.md): load for the smoke job, test suites inside the image,
  the reproducibility check and the scan gate.
- [references/stack-notes-go.md](references/stack-notes-go.md): load for Go images.
- [references/stack-notes-node.md](references/stack-notes-node.md): load for Node images.
- [references/stack-notes-php.md](references/stack-notes-php.md): load for PHP images.
- [references/guard-artifacts.md](references/guard-artifacts.md): load when adding the enforcement files: build
  checks, Dockerfile checker and fixture, smoke and scan jobs, updater entries.

## Sources

- https://docs.docker.com/build/building/best-practices/: multi-stage, `USER`, digest pins, `ADD --checksum`,
  pipefail, verified 2026-10.
- https://docs.docker.com/build/checks/: build checks and `check=error=true`, verified 2026-10.
- https://docs.docker.com/build/building/secrets/: secret mounts, verified 2026-10.
- https://docs.docker.com/build/ci/github-actions/attestations/: provenance mode by repository visibility,
  verified 2026-10.
- https://docs.docker.com/build/concepts/context/: ignore files and precedence, verified 2026-10.
- https://github.com/GoogleContainerTools/distroless: image list, Debian 13, debug variants, signing, verified
  2026-10.
- https://github.com/sigstore/cosign/blob/v3.1.4/doc/cosign_verify.md: keyless identity and issuer flags,
  verified 2026-10.
- https://github.com/kubernetes/kubernetes/pull/56503: non-numeric user rejected under `runAsNonRoot`, verified
  2026-10.
- https://docs.docker.com/reference/cli/docker/container/run/ and
  https://docs.docker.com/engine/containers/start-containers-automatically/: tmpfs options, read-only root, restart
  policies and manual stops, verified 2026-11-05.
