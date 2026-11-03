# CI gates for Go services

## Contents
- Job list
- Workflow sketch
- Fuzz loop that can fail
- Reproducibility job
- Guard greps
- Proving each gate

Workflow permissions, action pinning and runner choice follow `github-actions-hardening`. Versions below are
placeholders: replace `X.Y.Z` with the exact version you pin and keep it in one place.

## Job list

| Job | Command | Fails on |
|---|---|---|
| test | `go test -race -count=1 ./...` (cgo on) | test failure, data race |
| leak | `goleak.VerifyTestMain` inside the test job | goroutine left behind |
| fuzz | one `go test -fuzz` per target, real `-fuzztime` | crash, zero targets found |
| lint | golangci-lint `vX.Y.Z`, config `version: "2"` | findings |
| vuln | `govulncheck ./...` per module, text mode | reachable vulnerable call |
| repro | two clean builds, compare SHA-256 | differing digests |
| tidy | `go mod tidy -diff` (Go 1.23 or later; otherwise run tidy and `git diff --exit-code`) | uncommitted module changes |

Local `make ci` runs the same list. A job that exists in CI but not locally, or the reverse, is drift.

## Workflow sketch

```yaml
env:
  GOTOOLCHAIN: local
jobs:
  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@[sha] # vN
      - uses: actions/setup-go@[sha] # vN
        with:
          go-version-file: go.mod
      - run: go test -race -count=1 ./...
  lint:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@[sha] # vN
      - uses: actions/setup-go@[sha] # vN
        with:
          go-version-file: go.mod
      - uses: golangci/golangci-lint-action@[sha] # vN
        with:
          version: vX.Y.Z
  vuln:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@[sha] # vN
      - uses: actions/setup-go@[sha] # vN
        with:
          go-version-file: go.mod
      - run: go install golang.org/x/vuln/cmd/govulncheck@vX.Y.Z
      - run: |
          set -euo pipefail
          for mod in $(git ls-files '*go.mod' | xargs -n1 dirname); do
            (cd "$mod" && govulncheck ./...)
          done
```

`go-version-file: go.mod` follows the `toolchain` line when present; check that against the setup action's docs
for the version you pin.

## Fuzz loop that can fail

```bash
set -euo pipefail
found=0
for pkg in $(go list ./...); do
  for target in $(go test -list '^Fuzz' "$pkg" | grep '^Fuzz' || true); do
    found=$((found + 1))
    go test -run='^$' -fuzz="^${target}\$" -fuzztime=60s "$pkg"
  done
done
test "$found" -ge "${MIN_FUZZ_TARGETS:-1}" || { echo "expected fuzz targets, found $found"; exit 1; }
```

The `|| true` above applies only to `grep` finding no match in one package; the fuzz run itself is never masked.
When a crash is found, the job uploads `testdata/fuzz/` as an artifact so the input can be committed as a
regression seed.

## Reproducibility job

```bash
set -euo pipefail
export CGO_ENABLED=0 GOWORK=off GOFLAGS=-mod=readonly GOTOOLCHAIN=local
build() { go build -trimpath -ldflags "-s -w -X example.com/svc/internal/version.Version=${VERSION}" -o "$1" ./cmd/svc; }
build /tmp/a/svc
go clean -cache
build /tmp/b/svc
sha256sum /tmp/a/svc /tmp/b/svc
cmp /tmp/a/svc /tmp/b/svc
```

For a stronger check, run the second build in a different directory or container. `go version -m [binary]` shows
the build settings embedded in the binary; compare them with the release job's.

## Guard greps

Run in CI; each prints nothing when clean.

```bash
grep -rnE 'promauto\.New|prometheus\.MustRegister\(' --include='*.go' --exclude='*_test.go' .
grep -rnE 'func Set[A-Za-z]*ForTest' --include='*.go' .
grep -rnE '@latest|version: latest|\|\| true' .github/workflows/
grep -rnE 'continue-on-error: true' .github/workflows/
```

A hit with a written reason goes on an allowlist file that the guard reads; an unexplained hit fails.

## Proving each gate

Each gate is turned red once on a scratch branch before it counts:

- race: a test with two goroutines writing one variable.
- leak: a test that starts a goroutine blocked on a channel nobody closes.
- fuzz: a seed that triggers a panic.
- vuln: a module pinned to a version with a known reachable vulnerability.
- repro: pass `$(date +%s%N)` as an `-X` value in one of the two builds; the digests differ.
- lint: an unchecked error return.
