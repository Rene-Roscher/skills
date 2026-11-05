---
description: "A CI watch script that reports a Dependabot or older run instead of the pushed commit. Run with --scaffold --allow-tools Write Edit."
expected_outcome: "scripts/ci-watch.sh selects the run by the pushed commit's SHA (gh run list --commit with the workflow, compared on headSha), waits for it to appear, and watches that run with --exit-status; the reply explains why the newest run is the wrong one."
tags: [github-actions-hardening, output]
runs: 3
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

`scripts/ci-watch.sh` sometimes says CI is green although my push failed, and sometimes it waits on some Dependabot thing. Make it reliable.
