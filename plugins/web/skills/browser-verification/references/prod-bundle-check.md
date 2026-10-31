# Production bundle check

For apps where pushing to the main branch deploys, the push is the deploy. Check the production build before
it, against a non-production backend. A preview deployment of the same commit satisfies this check.

## Why the dev server is not enough

The dev server and the production build differ in ways that only show in production: minification, message
compilation, tree shaking, environment variables baked in at build time, SSR output, asset paths and caching.
Dev fixtures may also send different data shapes than the real backend, so a fix verified against dev data can
still fail in production.

## Steps

1. Copy the committed state into a temporary directory without touching the working tree, for example
   `git archive HEAD | tar -x -C "$tmp"`. Uncommitted edits are not what will deploy.
2. Install from the lockfile (`npm ci` or the project's equivalent) and run the production build there.
3. Start the built server (or a static file server for static output), or build and run the production
   container image, with environment variables pointing at a non-production backend: a local stack or staging.
4. If pages contain absolute URLs to the production host, map that hostname to the local server in the test
   browser (Chromium accepts `--host-resolver-rules`) instead of editing the build.
5. Run the same browser checks as in the normal procedure: absence of failure, measurements, element
   screenshots.
6. Record the commit, the build command, the backend URL and the results in the report.

```sh
#!/bin/sh
set -eu
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
git archive HEAD | tar -x -C "$tmp"
( cd "$tmp" && npm ci && npm run build )
# start the built server from "$tmp" with a non-production backend, then run the browser suite against it
```

## What it must not do

- Push to see whether it works.
- Point the built app at the production backend or production data.
- Reuse a stale build from an earlier commit. Rebuild for the commit you are about to push.

## Preview deployments

A preview deployment satisfies the rule when it builds the same commit with the production build command and
talks to a non-production backend. Run the browser checks against its URL and record that URL in the report.
