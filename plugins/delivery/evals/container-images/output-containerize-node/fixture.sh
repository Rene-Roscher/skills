#!/usr/bin/env bash
set -euo pipefail
git init -q .
cat > package.json <<'EOF'
{
  "name": "taskboard-web",
  "private": true,
  "type": "module",
  "scripts": { "build": "nuxt build", "start": "node .output/server/index.mjs" },
  "dependencies": { "nuxt": "^4.0.0" }
}
EOF
cat > package-lock.json <<'EOF'
{ "name": "taskboard-web", "lockfileVersion": 3, "requires": true, "packages": { "": { "name": "taskboard-web", "dependencies": { "nuxt": "^4.0.0" } } } }
EOF
cat > nuxt.config.ts <<'EOF'
export default defineNuxtConfig({ runtimeConfig: { apiSecret: '' } })
EOF
cat > .env <<'EOF'
NUXT_API_SECRET=fixture-value-not-a-real-secret
EOF
