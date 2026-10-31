#!/usr/bin/env bash
set -euo pipefail
mkdir -p .github/workflows
cat > package.json <<'EOF'
{ "name": "taskboard", "private": true, "scripts": { "test": "node --test" } }
EOF
cat > package-lock.json <<'EOF'
{ "name": "taskboard", "lockfileVersion": 3, "requires": true, "packages": { "": { "name": "taskboard" } } }
EOF
cat > .github/workflows/coverage.yml <<'EOF'
name: coverage
on:
  pull_request_target:
permissions:
  contents: read
  pull-requests: write
jobs:
  coverage:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm ci
      - run: npm test -- --experimental-test-coverage
      - uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({ ...context.repo, issue_number: context.issue.number, body: 'Coverage report' })
EOF
