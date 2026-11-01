# Keeping specs true

## The rule in practice

A change that alters behaviour under a spec's `Code:` paths updates that spec in the same change, or its
description states "spec unaffected: [reason]". Renames and moves update the `Code:` line and every routing row
that names the file.

## CI step

Copy the script into the repository (for example `tools/check_docs.py`) so CI does not depend on a plugin being
installed. Run it on every pull request:

```yaml
# in a pull_request job whose checkout step sets fetch-depth: 0
- name: Docs check
  run: |
    git diff --name-only "origin/$GITHUB_BASE_REF"...HEAD > changed.txt
    python3 tools/check_docs.py --changed changed.txt --strict
```

The three-dot diff needs the merge base. The checkout action fetches one commit by default; `fetch-depth: 0`
fetches "all history for all branches and tags" (https://github.com/actions/checkout, verified 2026-10-31). Pin
the action and set job permissions as `github-actions-hardening` describes.

`--strict` turns C06 (spec not routed) and C15 (code changed without its spec) into errors. When a change truly
leaves the spec untouched, the reviewer accepts the stated reason and the author updates `Checked against code:`
in the spec, which is a spec change and clears C15.

## PR template lines

```markdown
- [ ] Specs touched by this change are updated, or: spec unaffected because ...
- [ ] Routing table still resolves (`check_docs.py` passes)
- [ ] New decisions recorded as ADRs
```

## Periodic re-check

- Sort specs by `Checked against code:`; re-read the oldest against the code and update the date or the spec.
- A spec whose `Status` says Draft or Approved for a feature that has shipped: read the code, set Implemented or
  record the drift.
- Superseded ADRs keep their file; the routing table points at the current one.

## When an agent finds drift mid-task

Report it with both locations, as `evidence-before-claims` describes. If the task is to change that area, fix the
spec in the same change after the owner confirms which side is intended; otherwise open an issue and continue on
the behaviour that runs.
