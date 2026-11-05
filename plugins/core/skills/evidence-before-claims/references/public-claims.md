# Claims a project makes about itself

Load this before README, specs, ADRs or a changelog are pushed or published, or when `scripts/claim_scan.py`
reports findings. The scanner finds candidates by wording; it cannot see a claim phrased in another way, so read
the README and the security section yourself as well.

## Evidence per claim kind

| Claim kind | Examples | Evidence to open | Written form that holds |
|---|---|---|---|
| CI or test status | "CI is green", "never ran on CI", "all tests pass" | The run for the pushed commit: `gh run list --commit [sha]`, then `gh run view [id]` | A badge, or "CI passed for [sha] on [date]"; otherwise remove the line |
| Deploy or release status | "is live", "not yet deployed", "production-ready" | Deploy run, release entry, the version the live system reports | "Deployed [version] on [date]"; "production-ready" only with the checks that back it |
| Who decided | "the maintainer decided", "all decisions were made by a human" | ADR record (options, recommendation, who accepted, date), git history | "Options and a recommendation were prepared with [tool]; the maintainer accepted [n] of [m] recommendations and changed [x]" |
| Who wrote | "hand-written", "written without AI", "generated" | Git history, commit trailers, the project's disclosure policy | What the history shows, or nothing |
| Security property | "end-to-end encrypted", "zero-knowledge", "secure" | Design doc, threat model, the code that implements it | "Guarantees [property] against [attacker]. Does not claim [property], for example [forward secrecy]." |

## Rules for rewriting

- Date every status claim or replace it with a live source (a badge, a status page). A status sentence without a
  date is wrong from the day after it was written.
- Match the decision record exactly. "Proposed with a recommendation, accepted by the owner" is a full and
  honest sentence; "decided by the owner" is not the same claim, and neither is "generated".
- When the record is missing, write no authorship claim at all, and propose an ADR that records it.
- Name the security property, the attacker and the limit. A reader who checks one stated limit and finds it true
  trusts the rest; a reader who finds one inflated property trusts nothing.
- A claim you cannot check in this session is removed or marked as unverified, never kept as written.

## Before going public

Claims are half of the check. The other half is what the files leak: chat quotes, internal process notes, names,
home paths, internal hosts, secrets. `safe-actions` carries that audit and its scanner.
