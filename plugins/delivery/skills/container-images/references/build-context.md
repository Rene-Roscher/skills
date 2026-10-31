# Build context

## Allowlist form

Start from nothing and re-include what the build needs:

```text
**
!go.mod
!go.sum
!cmd
!internal
```

- `**` matches any number of directories, `!` makes an exception, and the last matching line decides.
- Re-including a directory (`!internal` or `!internal/**`) brings its contents back; both forms behaved the same in a
  test with Docker 29.9.2 (2026-10-31).
- The Dockerfile and the ignore file don't need re-including for the build to run.
- A denylist form (listing what to exclude) works too, but must at least list `.env*`, `.git`, private keys
  (`*.pem`, `*.key`, `id_*`), cloud credential files and local override files. New secret files are then excluded
  only if someone remembers to add them.

## Dockerfile-specific ignore files

A file named after the Dockerfile (`Dockerfile.dockerignore` next to `Dockerfile`, `web.Dockerfile.dockerignore`
next to `web.Dockerfile`) takes precedence over the root `.dockerignore`. It replaces the root file for that
build; the two are not merged. Reproduced 2026-10-31 with Docker 29.9.2: root `.dockerignore` listed `.env*`,
`Dockerfile.dockerignore` listed only `.git`, and `COPY . /ctx/` copied `.env.canary` into the image.

So each Dockerfile-specific file carries the full set of exclusions. A sub-application with its own Dockerfile
and ignore file is the usual place this goes wrong.

## Context canary

Prove it in CI for every build context, before the build:

```bash
set -eu
ctx="[build context directory]"
printf 'canary\n' > "$ctx/.env.ci-canary"
mkdir -p "$ctx/.git" && printf 'canary\n' > "$ctx/.git/ci-canary"
# build the image as the release does, then:
cid=$(docker create "[image]")
hits=$(docker export "$cid" | tar -t | grep -c 'ci-canary' || true)
docker rm "$cid" >/dev/null
test "$hits" -eq 0 || { echo "::error::build context leaks .env or .git into the image"; exit 1; }
```

`docker create` plus `docker export` works for distroless images, which have no shell to run `ls` in. The
`|| true` only stops `grep -c` from failing the pipeline on zero matches; the `test` line is the gate.

## Sources

- https://docs.docker.com/build/concepts/context/ (verified 2026-10)
