#!/usr/bin/env bash
set -euo pipefail
pkg=node_modules/@example/retry-kit
mkdir -p "$pkg"
cat > package.json <<'JSON'
{ "name": "invoice-sync", "private": true, "dependencies": { "@example/retry-kit": "^2.0.0" } }
JSON
cat > package-lock.json <<'JSON'
{
  "name": "invoice-sync",
  "lockfileVersion": 3,
  "packages": {
    "": { "name": "invoice-sync", "dependencies": { "@example/retry-kit": "^2.0.0" } },
    "node_modules/@example/retry-kit": { "version": "2.3.1" }
  }
}
JSON
cat > "$pkg/package.json" <<'JSON'
{ "name": "@example/retry-kit", "version": "2.3.1", "main": "index.js" }
JSON
cat > "$pkg/README.md" <<'MD'
# retry-kit

Wraps a function and retries it when it throws. By default, failed calls are retried 3 times with
exponential backoff.
MD
cat > "$pkg/index.js" <<'JS'
'use strict';

const DEFAULT_BASE_DELAY_MS = 200;
const DEFAULT_RETRIES = 7;

async function retry(fn, options = {}) {
  const retries = options.retries ?? DEFAULT_RETRIES;
  const baseDelay = options.baseDelayMs ?? DEFAULT_BASE_DELAY_MS;
  for (let attempt = 0; ; attempt++) {
    try {
      return await fn();
    } catch (err) {
      if (attempt >= retries) throw err;
      await new Promise((r) => setTimeout(r, baseDelay * 2 ** attempt));
    }
  }
}

module.exports = { retry };
JS
