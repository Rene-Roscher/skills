#!/usr/bin/env bash
set -euo pipefail
mkdir -p .github/workflows cmd/invoicing
cat > go.mod <<'EOF'
module example.com/invoicing

go 1.25
EOF
cat > cmd/invoicing/main.go <<'EOF'
package main

func main() {}
EOF
cat > Dockerfile <<'EOF'
FROM golang:1.25 AS build
WORKDIR /src
COPY . .
RUN go build -o /out/invoicing ./cmd/invoicing

FROM gcr.io/distroless/static-debian13
COPY --from=build /out/invoicing /app/invoicing
ENTRYPOINT ["/app/invoicing"]
EOF
cat > .github/workflows/ci.yml <<'EOF'
name: ci
on:
  pull_request:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go test ./...
EOF
