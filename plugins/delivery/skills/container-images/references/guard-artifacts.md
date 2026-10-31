# Guard artifacts

## Contents

- Build checks in every Dockerfile
- The Dockerfile checker and its fixture
- CI jobs
- Updater and deployment-side entries

These files make the rules hold by build. Create them in the target repository and adapt names and paths.

## Build checks in every Dockerfile

First two lines of every Dockerfile:

```dockerfile
# syntax=docker/dockerfile:1
# check=error=true
```

CI runs `docker build --check -f [Dockerfile] [context]` per Dockerfile, or the build-push-action input
`call: check`. With `check=error=true`, `SecretsUsedInArgOrEnv` and `JSONArgsRecommended` fail the build (both
reproduced with Docker 29.9.2 and Buildx 0.38.1 on 2026-10-31).

## The Dockerfile checker and its fixture

`scripts/ci/check-dockerfiles` (or the project's tool location), in POSIX sh or the language the repository already
uses for tooling. It checks every Dockerfile and Containerfile, and prints the file, line and fix for each finding:

1. Every `FROM` that is not `scratch` and not an earlier stage name contains `@sha256:`.
2. No `ARG` or variable in a `FROM` image reference.
3. Every directory with a Dockerfile is covered by the updater config.
4. The final stage sets `USER` to a numeric, non-zero UID (optionally `:gid`).
5. `ENTRYPOINT` and `CMD` in the final stage are JSON arrays that don't start with `sh` or `bash`.
6. No `ARG` or `ENV` whose name contains `TOKEN`, `SECRET`, `PASSWORD`, `PASSWD`, `KEY` or `CREDENTIAL`.
7. No fetch command piped into a shell; no `npm install` or `npm i` (use `npm ci`); no `yarn install` without
   `--immutable`; no `pnpm install` without `--frozen-lockfile`; no global install without an exact version.
8. A manifest (`package.json`, `composer.json`, `requirements*.txt`, `go.mod`) is never copied without its lockfile.
9. No literal `GOARCH=` or `GOOS=` values.
10. Every build context has an ignore file, and every Dockerfile-specific ignore file is complete on its own:
    it starts with `**`, or it lists `.env` and `.git` patterns.

Ship `scripts/ci/fixtures/bad.Dockerfile`, which breaks each check once, with a comment naming the check. The
self-test runs the checker on the fixture and fails unless every check reports. A checker that reports nothing on
its fixture is broken.

## CI jobs

- `image-check`: the build checks and the Dockerfile checker with its self-test.
- `image-smoke`: builds the production `target`, runs the smoke test, the context canary, the source-map check, the
  user and entrypoint checks (see the image tests reference).
- `image-scan`: pinned scanner, fails on fixable HIGH and CRITICAL, ignores with reason and expiry.
- `release` (if images are published): `needs` the three jobs above; pushes by digest, signs, attests, tags,
  verifies. Its permissions, trigger and runner follow `github-actions-hardening`.
- A scheduled workflow re-scans the deployed digests.

## Updater and deployment-side entries

- Updater: Dependabot `docker` entries (or Renovate with `docker:pinDigests`) for every Dockerfile directory, and
  for compose files that reference images.
- Deployment repository, if images are signed: an admission or GitOps verification policy pinned to the release
  workflow identity, with a policy test that rejects an unsigned image and an image signed by another workflow or
  ref.

## Sources

- https://docs.docker.com/build/checks/ (verified 2026-10)
- https://docs.docker.com/build/building/best-practices/ (verified 2026-10)
- https://docs.renovatebot.com/docker/ (verified 2026-10)
