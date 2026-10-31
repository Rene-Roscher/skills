# Build secrets

## The mechanism

- Secret mount as an environment variable for one `RUN`:
  `RUN --mount=type=secret,id=npm_token,env=NPM_TOKEN npm ci`
- Secret mount as a file, for tools that read a config file:
  `RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci` (use the build user's home if the stage is not
  root).
- SSH agent forwarding for private git dependencies: `RUN --mount=type=ssh ...` with `docker build --ssh default`.
- Locally: `docker build --secret id=npm_token,env=NPM_TOKEN .`
- In GitHub Actions with `docker/build-push-action`: the `secrets:` input (`id=value`) or `secret-envs:` input
  (`id=ENV_NAME`). Never `build-args:` for a credential.

The secret exists only while that `RUN` step runs. It is not written to a layer, and secret mounts are not
included in provenance attestations.

## Why build args and ENV leak

- `ARG` and `ENV` values persist in the final image's metadata and history.
- Provenance in `mode=max` records the values of build arguments. `docker/build-push-action` adds `mode=max`
  provenance automatically when the GitHub repository is public, and `mode=min` when it is private. A private
  repository that later goes public starts publishing build-argument values with every image.
- A value exported as `ENV` in a builder stage still reaches provenance through the build arguments that set it.

Inspect what a built image carries:

```bash
docker history --no-trunc [image]
docker inspect [image]
docker buildx imagetools inspect [image] --format '{{ json .Provenance.SLSA }}'
```

The last command's format string comes from Docker's provenance documentation. Search the output for anything
that looks like a token.

## Typical case: upload during build

A front-end build uploads source maps to an error tracker and needs an auth token:

1. Mount the token as a secret for the one `RUN` that uploads.
2. Delete the maps in the same `RUN` after the upload, or build them in a stage the runtime stage never copies.
3. The runtime stage contains no `.map` files (checked by the image tests).

## Runtime secrets

Inject them when the container starts: an orchestrator secret mounted as a file or environment variable, or a
secret store the app reads at startup. Nothing in the image, and nothing in compose files committed to the
repository.

## Sources

- https://docs.docker.com/build/building/secrets/ (verified 2026-10)
- https://docs.docker.com/build/metadata/attestations/slsa-provenance/ (verified 2026-10)
- https://docs.docker.com/build/ci/github-actions/attestations/ (verified 2026-10)
- https://docs.docker.com/reference/build-checks/secrets-used-in-arg-or-env/ (verified 2026-10)
- https://github.com/docker/build-push-action (verified 2026-10)
