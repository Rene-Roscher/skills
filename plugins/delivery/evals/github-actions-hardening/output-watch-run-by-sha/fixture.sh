#!/usr/bin/env bash
# A CI watch script that follows whatever run is newest.
set -euo pipefail
mkdir -p scripts .github/workflows
cat > scripts/ci-watch.sh <<'SH'
#!/usr/bin/env bash
# Push, then wait for CI and fail if it is red.
set -euo pipefail
git push
sleep 5
id=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch "$id" --exit-status
SH
chmod +x scripts/ci-watch.sh
cat > .github/workflows/ci.yml <<'YAML'
name: ci
on:
  push:
    branches: [main]
  pull_request:
permissions: {}
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    permissions:
      contents: read
    steps:
      - run: echo test
YAML
cat > .github/dependabot.yml <<'YAML'
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
YAML
