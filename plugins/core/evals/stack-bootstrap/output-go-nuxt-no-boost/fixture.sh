#!/bin/sh
set -eu
mkdir -p .claude cmd/api web
cat > go.mod <<'MOD'
module example.com/shop

go 1.24
MOD
cat > web/package.json <<'JSON'
{ "private": true, "dependencies": { "nuxt": "^4.0.0", "vue": "^3.5.0" } }
JSON
cat > Dockerfile <<'DOCKER'
FROM golang:1.24 AS build
WORKDIR /src
COPY . .
RUN go build -o /api ./cmd/api
DOCKER
cat > .claude/settings.json <<'JSON'
{
  "permissions": {
    "deny": ["Read(.env)"]
  }
}
JSON
