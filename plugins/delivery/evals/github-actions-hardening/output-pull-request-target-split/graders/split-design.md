---
type: llm
weight: 3
focus: trace
---

Judge the workflow files the session wrote or changed (visible in the trace) and the final reply.

PASS if: no workflow triggered by `pull_request_target`, `workflow_run` or `issue_comment` checks out the pull-request head and then runs `npm`, a build or a test step; the tests run in a workflow triggered by `pull_request` that uploads its result as an artifact; a separate privileged workflow (for example `workflow_run`) downloads that artifact, treats it as data (parses or validates it, never executes it) and posts the comment; the commenting job grants only `pull-requests: write` (plus `actions: read` if needed to download the artifact); no write scope sits at workflow level.
FAIL if the privileged workflow still builds or tests pull-request code, or if the fix only adds permissions or secrets.
