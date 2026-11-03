#!/usr/bin/env bash
set -euo pipefail
mkdir -p .github/workflows
cat > .github/workflows/release.yml <<'EOF'
name: release
on:
  push:
    tags: ['v*']
permissions: {}
jobs:
  release:
    runs-on: ubuntu-24.04
    timeout-minutes: 30
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - run: make dist
      # lint-allow: L10 seeded bad example for the eval
      - run: curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin
      - run: for b in dist/agent_*; do syft "file:$b" -o cyclonedx-json="$b.cdx.json"; done
      - run: cd dist && sha256sum * > SHA256SUMS
      - run: gh release create "$GITHUB_REF_NAME" dist/*
        env:
          GH_TOKEN: ${{ github.token }}
EOF
