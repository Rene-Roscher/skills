# Multi-architecture images

## Decide first

Build only the architectures something deploys. Each extra platform doubles build work and test surface. A
single-architecture image is fine when it is a recorded decision.

## Cross-compile instead of emulating

Emulated builds (QEMU) can be much slower than native builds, compilation most of all. Run the build stage on the
builder's platform and compile for the target:

```dockerfile
FROM --platform=$BUILDPLATFORM golang:[go-version]@sha256:[digest] AS build
ARG TARGETOS TARGETARCH
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /out/app ./cmd/app
```

- Never hard-code `GOARCH=amd64` or similar; it builds the wrong binary for the other platform without an error.
- The runtime stage has no `--platform` flag, so it resolves to the target platform.

Per language:

- Go without cgo: cross-compiles directly.
- Go with cgo, Rust with C dependencies: needs a cross toolchain for the target, or native runners per platform.
- Node with native modules: install dependencies in a stage that runs on the target platform, or on native
  runners; modules compiled for the builder's architecture fail at run time.
- PHP extensions: compiled per platform, so build on native runners per platform.

## Native runners per platform

When cross-compilation isn't practical, build each platform on a native runner, push each by digest, and merge
them into one index with `docker buildx imagetools create`. Sign the index digest.

## Check

`docker buildx imagetools inspect [image]@[digest]` lists exactly the intended platforms. Run the smoke test on
each platform that something deploys.

## Sources

- https://docs.docker.com/build/building/multi-platform/ (verified 2026-10)
