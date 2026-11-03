#!/usr/bin/env bash
set -euo pipefail
mkdir -p .github/workflows internal/parse
cat > go.mod <<'EOF'
module example.com/worker

go 1.24.0
EOF
cat > internal/parse/parse.go <<'EOF'
package parse

import "strings"

func Host(s string) string { return strings.TrimSpace(s) }
EOF
cat > internal/parse/parse_test.go <<'EOF'
package parse

import "testing"

func FuzzHost(f *testing.F) {
	f.Add(" example.com ")
	f.Fuzz(func(t *testing.T, s string) { _ = Host(s) })
}
EOF
cat > .github/workflows/ci.yml <<'EOF'
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-24.04
    env:
      CGO_ENABLED: "0"
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: stable
      - run: go test ./...
      - run: go test -run=^$ -fuzz=. -fuzztime=30s ./... || true
      - uses: golangci/golangci-lint-action@v6
        with:
          version: latest
      - run: go install golang.org/x/vuln/cmd/govulncheck@latest && govulncheck -json ./...
EOF
