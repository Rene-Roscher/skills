# Image tests

## Contents

- Smoke job
- Long-running processes
- Test suite inside the final image
- Reproducibility
- Scan gate

## Smoke job

Runs the exact image the release will push, before any tag points at it. The push step `needs:` this job.

```bash
set -euo pipefail
img="[image]@[digest or local ID]"
docker run -d --name smoke --restart=on-failure \
  --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m,uid=[uid],gid=[gid],mode=0700 \
  --cap-drop=ALL --security-opt=no-new-privileges \
  --user "[uid]:[gid]" -p 127.0.0.1:8080:8080 \
  "$img"
for i in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:8080/healthz >/dev/null; then break; fi
  test "$i" -lt 30 || { docker logs smoke; exit 1; }
  sleep 1
done
curl -fsS "http://127.0.0.1:8080/api/bookings?limit=1" >/dev/null   # one real request
# image HEALTHCHECK, if the image declares one
test "$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' smoke)" != unhealthy
# arguments reach the process: a wrapper that ignores "$@" starts the server here instead
docker run --rm --read-only --user "[uid]:[gid]" "$img" [binary] --version | grep -q '[expected version]'
# kill test: the host kills the main process, the restart policy brings it back
pid=$(docker inspect -f '{{.State.Pid}}' smoke); kill -9 "$pid"
for i in $(seq 1 30); do
  test "$(docker inspect -f '{{.RestartCount}}' smoke)" -ge 1 && curl -fsS http://127.0.0.1:8080/healthz >/dev/null && break
  test "$i" -lt 30 || { echo "::error::no recovery after kill"; exit 1; }
  sleep 1
done
start=$(date +%s); docker stop -t 10 smoke >/dev/null; end=$(date +%s)
test $((end - start)) -lt 10 || { echo "::error::no graceful stop within 10s"; exit 1; }
```

curl runs on the CI runner, not in the image. Add one tmpfs per declared writable path, owned by the runtime user,
and nothing else: a write anywhere else must fail the run. Use the same mount options as the deployment; the
default tmpfs is root-owned with mode 1777, which hides a mode or owner mismatch that production has. `kill -9`
of the host PID needs the same user as the Docker daemon or root on the runner; `docker kill` and `docker stop`
count as a manual stop and are never restarted, so they cannot stand in for it.

Also in this job:

- the build-context canary (no `.env` or `.git` files in the image);
- the source-map check: `docker export` of a container created from the image, piped to `tar -t`, contains no
  `.map` files;
- the user check: `docker inspect -f '{{.Config.User}}'` is numeric and not 0;
- the entrypoint check: `docker inspect -f '{{json .Config.Entrypoint}}'` is a JSON array that does not start with
  `sh` or `bash`;
- every documented mode (web, worker, scheduler, migrate) started once with its production arguments;
- the package inventory: copy the lock or manifest the image carries out of a created container
  (`docker create`, then `docker cp [id]:/app/vendor/composer/installed.json -`) and fail on any name from the
  committed denylist (REPLs, debuggers, test runners, fakers), or read `go version -m` of the binary.

Seeded-bad image: a fixture Dockerfile whose app writes under its own directory at startup. The smoke job must
fail on it.

## Long-running processes

Workers, schedulers and consumers get the same treatment as the web process: their own container, a restart
policy, a health signal and a kill test.

- Health for a process without a port is a heartbeat: the work loop writes a timestamp (a file on a tmpfs, a cache
  key) and the health command fails when it is older than the budget, for example twice the loop interval.
- A scheduler runs the way its framework documents for production (for Laravel, `schedule:run` every minute from
  cron or the orchestrator's scheduler; `schedule:work` is the local development command). The heartbeat proves
  that ticks arrive.
- Prove it: kill the main process from the host and watch it come back; then stop the loop (make the heartbeat
  write fail, or pause the work) and watch health turn unhealthy within the budget.
- A shell loop around the command is not supervision. It restarts nothing when the shell itself dies, it turns a
  crash into a silent retry, and its PID 1 shell does not forward SIGTERM.

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

- https://docs.docker.com/reference/cli/docker/container/run/ (`--tmpfs`, `--read-only`, verified 2026-11-05)
- https://docs.docker.com/engine/containers/start-containers-automatically/ (manual stop ignores the restart
  policy, verified 2026-11-05)
- https://laravel.com/docs/13.x/scheduling ("Running the Scheduler", "Running the Scheduler Locally", verified
  2026-11-05)

- https://github.com/aquasecurity/trivy/blob/v0.76.1/docs/guide/configuration/filtering.md (verified 2026-10)
- https://github.com/moby/buildkit/blob/master/docs/build-repro.md (verified 2026-10)
- https://docs.docker.com/build/ci/github-actions/reproducible-builds/ (verified 2026-10)
