#!/usr/bin/env bash
set -euo pipefail
mkdir -p .github/workflows cmd/app
cat > go.mod <<'EOF'
module example.com/app

go 1.25
EOF
cat > cmd/app/main.go <<'EOF'
package main

func main() {}
EOF
cat > Dockerfile <<'EOF'
FROM golang:1.25 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian13
COPY --from=build /out/app /app/app
ENTRYPOINT ["/app/app"]
EOF
cat > .github/workflows/release.yml <<'EOF'
name: release
on:
  push:
    tags: ["v*"]
permissions: {}
jobs:
  release:
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    permissions:
      contents: read
      packages: write
      id-token: write
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/example/app:latest
EOF
