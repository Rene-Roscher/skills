# Dockerfile baseline

An annotated starting point for a compiled service, here a booking API written in Go. Adapt the build stage to the
language (see the stack notes) and keep the runtime stage's shape. Placeholders in square brackets are resolved
from the registry and the base image, never guessed.

```dockerfile
# syntax=docker/dockerfile:1
# check=error=true
# The two lines above pin the Dockerfile frontend major and make build-check warnings fail the build.

# Build stage: toolchain only. Runs on the builder's platform and cross-compiles.
FROM --platform=$BUILDPLATFORM golang:[go-version]@sha256:[digest] AS build
WORKDIR /src
# Manifests and lockfiles first, so the dependency layer is cached separately from the source.
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
ARG TARGETOS TARGETARCH
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH \
    go build -trimpath -o /out/booking-api ./cmd/booking-api

# Runtime stage: last in the file, so an untargeted build produces the production image.
FROM gcr.io/distroless/static-debian13:nonroot@sha256:[digest] AS runtime
# COPY without --chown keeps the binary owned by root, so the runtime user cannot replace it.
COPY --from=build /out/booking-api /app/booking-api
# Numeric user, read from the base image config with docker inspect.
USER [uid]:[gid]
# Exec form: the binary is PID 1 and receives SIGTERM.
ENTRYPOINT ["/app/booking-api"]
```

Notes on the template:

- Every external `FROM` is a literal `image:tag@sha256:[digest]`, so the updater can rewrite it. No `ARG` in
  `FROM` lines.
- Build-time credentials use `RUN --mount=type=secret` (see the build secrets reference). No `ARG` or `ENV` for
  them.
- `RUN` lines that pipe need pipefail. Debian-based stages set `SHELL ["/bin/bash", "-o", "pipefail", "-c"]`,
  because their `/bin/sh` is dash, which rejects `set -o pipefail` (dash 0.5.12 on `debian:bookworm-slim`,
  reproduced 2026-10-31). Where `/bin/sh` is busybox, as on Alpine, `set -o pipefail &&` works.
- OCI labels (`org.opencontainers.image.source`, `.revision`, `.version`) are usually set by the CI build step from
  the commit; set them in the Dockerfile only if no step does.
- Writable paths (cache, tmp, uploads) are declared in the deployment as volumes or tmpfs, not created writable in
  the image.
- A `dev` or `test` stage, if any, comes before the runtime stage. CI builds an explicit `target` anyway.

What the template leaves out on purpose:

- `HEALTHCHECK`: add one only for Docker or Compose users, in exec form, calling the binary's own health
  subcommand.
- Package installs in the runtime stage: distroless has no package manager. Anything the process needs comes from a
  build stage by `COPY --from`.

## Sources

- https://docs.docker.com/build/building/best-practices/ (verified 2026-10)
- https://docs.docker.com/build/checks/ (verified 2026-10)
- https://docs.docker.com/build/building/multi-platform/ (verified 2026-10)
- https://github.com/GoogleContainerTools/distroless (verified 2026-10)
