#!/bin/sh
set -eu
cat > package.json <<'JSON'
{ "private": true, "type": "module", "devDependencies": { "nuxt": "^4.0.0" } }
JSON
cat > nuxt.config.ts <<'TS'
export default defineNuxtConfig({
  devtools: { enabled: false },
  routeRules: {
    '/': { prerender: true },
  },
})
TS
