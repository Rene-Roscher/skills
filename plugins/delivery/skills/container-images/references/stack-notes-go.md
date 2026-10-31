# Stack notes: Go

- Without cgo (`CGO_ENABLED=0`), the binary is static and fits `distroless/static`. Check what the base carries
  (CA bundle, time zone data, user entries) instead of assuming it, and copy what is missing from the build stage.
- With cgo, the binary needs glibc and whatever C libraries it links: use `distroless/base` or `distroless/cc`, and
  run `ldd` on the binary in the build stage to see the list.
- Pin the toolchain to a patch version in one place (the `golang` image tag in the build stage, matched by the
  `toolchain` line in `go.mod` and the version CI installs). A floating minor means two builds of the same commit
  can differ.
- `go.sum` is committed; `go mod download` runs before `COPY . .` so the dependency layer caches. Don't run
  `go mod tidy` in the image build.
- `-trimpath` removes local file system paths from the binary, which also helps reproducibility.
- Cross-compile with `GOOS=$TARGETOS GOARCH=$TARGETARCH` from `FROM --platform=$BUILDPLATFORM`; never a literal
  `GOARCH`.
- Version information goes in with `-ldflags "-X main.version=..."` from a build argument that holds no secret.
- Health: a `health` subcommand in the binary that calls its own endpoint, used by an exec-form `HEALTHCHECK` if
  Docker users need one.

Sources: https://docs.docker.com/build/building/multi-platform/,
https://github.com/GoogleContainerTools/distroless (verified 2026-10).
