# Vacuous green

Load when you write or review CI gates, scanners or filtered test runs.

A check is vacuous when it passes without having tested anything. Every check must prove that it ran.

## Filtered test runs

Runners differ when a filter matches nothing:

- `go test -run NoSuchTest ./...` prints `[no tests to run]` and exits 0 (go1.27.3, run 2026-10-31).
- pytest exits with code 5 when no tests were collected
  (https://docs.pytest.org/en/stable/reference/exit-codes.html, verified 2026-10).

Check what yours does with a filter that matches nothing before you rely on it. For guard suites, parse the
JUnit report and fail below a minimum test count.

## Scanners and guards

A scanner that reports zero findings may have matched nothing at all. Ship a known-positive fixture with every
scanner and fail the job when the scanner finds nothing in it.

## Ignored exit codes

- `|| true`, `continue-on-error: true` and similar settings need a reason comment on the same or the previous
  line.
- In bash, a pipeline returns the exit status of its last command unless `set -o pipefail` is on, so
  `run-tests | tee log` succeeds when the tests fail.
- A step that skips itself when a tool is missing reports success. Fail instead.

## Globs that match nothing

- In POSIX `sh`, a loop over `*.json` with no matching file runs once with the literal string `*.json`.
  Check that the file exists inside the loop, or count the matches first.
- `actions/upload-artifact` only warns when no file matches, because `if-no-files-found` defaults to `warn`.
  Set it to `error` where the artifact is required.

Source: https://github.com/actions/upload-artifact (README for v7, verified 2026-10).

## Local and CI parity

The local "run CI" command runs the same job list as CI. A job that runs only in CI, or only locally, drifts
until one of them is green for the wrong reason.

## Proving a gate

For every new gate, show one input it rejects: rename the guarded test, plant the forbidden pattern in a
fixture, delete the artifact. Report the red run next to the green one.
