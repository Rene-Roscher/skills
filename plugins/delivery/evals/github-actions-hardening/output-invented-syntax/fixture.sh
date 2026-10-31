#!/usr/bin/env bash
set -euo pipefail
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF'
name: ci
on: [pull_request]
permissions: write-all
jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: docker://alpine:3.20
        with:
          args: sh -c "echo lint"
EOF
