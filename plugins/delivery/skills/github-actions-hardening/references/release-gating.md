# Release gating

## The chain

Every job that pushes an artifact, signs, attests or deploys needs the gate jobs of the same run.

Same workflow:

```yaml
jobs:
  test:
    # ...
  publish:
    needs: [test]
```

Separate test workflow, called as a reusable workflow so it runs on the same commit:

```yaml
jobs:
  gates:
    uses: ./.github/workflows/ci.yml
  publish:
    needs: [gates]
```

Not a gate:

- a test workflow triggered by the same push and running in parallel;
- "main was green when we tagged": a tag release re-runs or calls the gates;
- a required status check on the branch, for a job triggered by a tag push. Branch rules don't apply to tags.

## What counts as a gate

The project's test suite, the workflow lint, and for images the image smoke test and the scan (see
`container-images`). Put the gate job names in one list that the workflow checker and the ruleset both use, so
the two can't drift.

## Order inside a release job

For an image release the order is: build, smoke test the built image, push by digest, sign the digest, attest,
create the tags, verify the signature with the anchored identity. A tag that points at an unsigned digest is
pullable as soon as it exists; if the job fails after tagging and before signing, it stays unsigned. The image
side of this order is in `container-images`.

## Concurrency for releases

```yaml
concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false
  queue: max
```

- With the default `queue: single`, a newly queued run cancels the pending one, so an intermediate release is
  dropped without notice.
- `queue: max` holds up to 100 pending runs. It cannot be combined with `cancel-in-progress: true`; that is a
  validation error.
- CI workflows use `cancel-in-progress: true` and group by workflow and ref.

## Preflight guards

Before the first push step, assert what the release needs and fail with a message that names the fix:

```bash
set -euo pipefail
: "${PUBLIC_API_URL:?set PUBLIC_API_URL in repository variables}"
command -v cosign >/dev/null || { echo "::error::cosign is not installed on this runner"; exit 1; }
if [ "${ASSET_CDN_ENABLED:-false}" = true ] && [ -z "${ASSET_BUCKET:-}" ]; then
  echo "::error::ASSET_CDN_ENABLED needs ASSET_BUCKET"; exit 1
fi
```

Typical failures these catch: a front-end build that inlines an empty variable and ships a broken bundle, and a
feature flag switched on without the resource it depends on.

Test each guard: run the job with the variable unset, or in a dry-run mode, and confirm it fails before anything
is pushed.

## Sources

- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax (verified 2026-10)
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency (verified 2026-10)
