# Base images and updates

## Choosing a base

| The runtime needs | Base |
|---|---|
| one static binary | `distroless/static` (or `scratch` if it needs no CA bundle, user entries or tzdata) |
| glibc, libstdc++, OpenSSL | `distroless/base` or `distroless/cc`; check the distroless README for which libraries each one carries |
| a language runtime | a distroless language image (Node, Python, Java), or the official slim image |
| a shell at run time | a slim distribution image, and record why the shell is needed |

Equally valid alternatives, when an ADR names the trade-off: other minimal hardened image families, slim Debian or
Ubuntu, Alpine. Alpine uses musl instead of glibc; check that native extensions and DNS behaviour work under musl
with the test suite inside the image.

Distroless facts (checked 2026-10-31): images are based on Debian 13; a name without a distribution suffix
currently resolves to the `-debian13` images and will change; each image has `latest`, `nonroot`, `debug` and
`debug-nonroot` tags; `:debug` adds a busybox shell. The README does not state the numeric UID of the `nonroot`
user, so read it with `docker inspect -f '{{.Config.User}}' [image]`.

## Writing the pin

```dockerfile
FROM gcr.io/distroless/cc-debian13:nonroot@sha256:[64 hex digits]
```

- Get the digest from the registry, not from a blog: `docker buildx imagetools inspect [image]:[tag]` prints it.
  For a multi-platform image, pin the index digest, not one platform's manifest.
- Keep the tag next to the digest. It tells humans and updaters which line the digest belongs to.
- No `ARG` in `FROM`. Neither Renovate's nor Dependabot's docs say they follow it (checked 2026-10-31).

Distroless images are signed keyless. Before adopting a new base, verify it with `cosign verify`, issuer
`https://accounts.google.com` and identity `keyless@distroless.iam.gserviceaccount.com` (from the distroless README). <!-- lint-allow: L13 signing identity published by the image vendor -->

## Updaters

- Dependabot: ecosystem `docker`, one entry or `directories` list covering every directory with a Dockerfile. A
  Dockerfile in a subdirectory that is not listed never gets updates. For `docker`, only `cooldown.default-days`
  is supported.
- Renovate: `docker:pinDigests` pins and updates digests, and keeps the tag in the `FROM` line.
- How Dependabot treats `tag@sha256:` lines in every case is not spelled out on the docs pages read (checked
  2026-10-31). Check the first update pull request: the digest must change, and for a new version the tag too.
- The Dockerfile checker fails when a Dockerfile directory is missing from the updater config.

## Security releases of a language runtime

Official images are rebuilt after the upstream release, so a patched tag may not exist yet when the advisory is
published. With digest pins:

1. Keep the current digest until a patched official image exists, or build your own patched base from the
   upstream release tarball (checksum-verified) and pin that digest.
2. Name the advisory in the commit that moves the pin, with its link.
3. Move back to the official image once it carries the fix, and record that too.

## Sources

- https://docs.docker.com/build/building/best-practices/ (verified 2026-10)
- https://github.com/GoogleContainerTools/distroless (verified 2026-10)
- https://docs.renovatebot.com/docker/ (verified 2026-10)
- https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference (verified 2026-10)
