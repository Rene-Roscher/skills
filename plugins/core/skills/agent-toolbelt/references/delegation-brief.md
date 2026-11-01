# Delegation brief

Load when you consider handing work to a subagent, or when you receive its report.

## When to delegate

Delegate when all hold:

- the task is separable: it has a clear question and needs none of your running reasoning;
- its raw output would flood your context (wide searches, long logs, many files) while you need only a summary;
- you can check the answer cheaply afterwards.

Do not delegate a single lookup you can run yourself in one call, a decision, or a write that depends on what
you just read. Per the Claude Code docs (https://code.claude.com/docs/en/sub-agents, verified 2026-11-01), a
subagent runs in its own context window, returns only a summary, and its requests count toward the same usage
limits as the main conversation, so delegation costs.

## The brief

Write it so someone with no access to this conversation could do the job. Fields:

1. Question: one sentence. "Which call sites pass a currency string instead of the currency type?"
2. Scope: paths to search, paths to ignore, sources allowed (repository only, or also vendor docs).
3. Tools and limits: read-only; no installs; no network unless named; no commits.
4. Budget: a maximum number of files opened or commands run, or a time limit. State what to do on reaching it:
   report partial results and say what was not covered.
5. Result definition: the exact shape. For example, "a list of file:line with the one-line excerpt, then a
   count, then the commands you ran". A yes or no answer must come with the evidence that supports it.
6. Uncertainty: ask it to mark each item as seen (opened and read), or guessed.

Template:

```text
Question: [one sentence]
Scope: search [paths]; ignore [paths]; sources: repository only.
Rules: read-only; do not install, edit, commit or call external services.
Budget: at most [n] files opened. If you hit it, stop and say what is not covered.
Result: [list of file:line and excerpt] + [count] + [commands run].
Mark each item "seen" or "guessed".
```

## Checking the report

A subagent report is a lead (see `evidence-before-claims`: reported, not verified).

- Open two or three of the cited locations yourself, including one the report treats as typical and one at the
  edge.
- Re-run the decisive search with your own command. A claim of absence ("no callers", "never used") needs your
  own search, with the spelling variants and the generated code in mind.
- Compare its count with yours. A mismatch means its scope or your search is off; find out which.
- If it listed commands, repeat the key one.
- If it did not follow the result shape, ask again with a tighter brief rather than reconstructing.

Label what you pass on: "checked by me" for what you re-ran, "reported by the subagent" for the rest.

## Parallel subagents

Split by independent scope (one per directory or per question), never by overlapping files if they may write.
Keep them read-only unless the task is a disjoint set of edits and you will review each diff.
