---
type: llm
weight: 2
focus: trace
---

PASS if the final script picks the run whose head SHA equals the pushed commit (for example `gh run list --commit "$(git rev-parse HEAD)" --workflow ci.yml`), handles the delay until that run appears, watches it with a non-zero exit on failure, and the reply explains that updater, scheduled and older runs can be newer than the run of the push.
FAIL if the script still takes the newest run, filters only by branch, or sleeps longer instead of selecting by commit.
