# Image tests

## Smoke job

Runs the exact image the release will push, before any tag points at it. The push step `needs:` this job.

```bash
set -euo pipefail
img="[image]@[digest or local ID]"
docker run -d --name smoke \
  --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --cap-drop=ALL --security-opt=no-new-privileges \
  --user "[uid]:[gid]" -p 127.0.0.1:8080:8080 \
  "$img"
for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8080/healthz >/dev/null; then break; fi
  test "$i" -lt 30 || { docker logs smoke; exit 1; }
  sleep 1
done
curl -fsS "http://127.0.0.1:8080/api/bookings?limit=1" >/dev/null   # one real request
start=$(date +%s); docker stop -t 10 smoke >/dev/null; end=$(date +%s)
test $((end - start)) -lt 10 || { echo "::error::no graceful stop within 10s"; exit 1; }
```

curl runs on the CI runner, not in the image. Add one tmpfs per declared writable path, and nothing else: a write
anywhere else must fail the run.

Also in this job:

- the build-context canary (no `.env` or `.git` files in the image);
- the source-map check: `docker export` of a container created from the image, piped to `tar -t`, contains no
  `.map` files;
- the user check: `docker inspect -f '{{.Config.User}}'` is numeric and not 0;
- the entrypoint check: `docker inspect -f '{{json .Config.Entrypoint}}'` is a JSON array that does not start with
  `sh` or `bash`.

Seeded-bad image: a fixture Dockerfile whose app writes under its own directory at startup. The smoke job must
fail on it.

## Test suite inside the final image

After a base or runtime change, run the test suite with the final image's runtime and system files. For an
interpreted language, mount or copy the tests into a stage derived from the runtime stage and run them there. For
a compiled binary, run its integration tests against the running container. A suite that passes only in the build
image proves nothing about the runtime image.

## Reproducibility

Build the same commit twice, on clean builders, with `SOURCE_DATE_EPOCH` from the commit time and
`rewrite-timestamp=true`, and compare the digests. A difference points at an unpinned input: a floating toolchain,
a download without a checksum, a timestamp written into a file.

## Scan gate

- Pinned scanner version, installed by checksum or through a SHA-pinned action.
- `trivy image --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed [image]@[digest]`
- Ignores in `.trivyignore.yaml` with `statement` (the reason) and `expired_at` (the expiry date).
- The scan job is a `needs:` dependency of the tag step.
- A scheduled workflow re-scans the digests that are deployed, read from the deployment repository, and opens an
  issue or alerts on new findings.

## Sources

- https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/configuration/filtering.md (verified 2026-10)
- https://github.com/moby/buildkit/blob/master/docs/build-repro.md (verified 2026-10)
- https://docs.docker.com/build/ci/github-actions/reproducible-builds/ (verified 2026-10)
