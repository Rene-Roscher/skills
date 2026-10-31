#!/usr/bin/env bash
set -euo pipefail
mkdir -p .github/workflows
cat > package.json <<'JSON'
{ "name": "booking-web", "private": true, "scripts": { "build": "vite build" }, "dependencies": { "@booking/ui": "^2.0.0", "vite": "^7.0.0" } }
JSON
cat > package-lock.json <<'JSON'
{ "name": "booking-web", "lockfileVersion": 3, "requires": true, "packages": { "": { "name": "booking-web" } } }
JSON
cat > .npmrc <<'NPMRC'
@booking:registry=https://npm.pkg.example.com/
//npm.pkg.example.com/:_authToken=${NPM_TOKEN}
NPMRC
cat > Dockerfile <<'DOCKERFILE'
FROM node:22 AS build
WORKDIR /app
COPY package.json package-lock.json .npmrc ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:22-slim
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
USER 1000
CMD ["node", "dist/server.js"]
DOCKERFILE
cat > .github/workflows/image.yml <<'YAML'
name: image
on:
  push:
    branches: [main]
permissions: {}
jobs:
  image:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/example/booking-web:latest
YAML
