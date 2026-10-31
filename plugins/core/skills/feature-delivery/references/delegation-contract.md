# Delegation contract

## Before the first subagent starts

Write down the interfaces between the packages. Each subagent gets the parts it produces or consumes:

- DTO and service signatures, with field names and types.
- Event names and payload shapes, including which IDs they carry (external IDs only).
- Route names, URL patterns and API request and response shapes, including error codes.
- Database tables and columns the package may create or change.

A subagent that has to guess an interface builds a different one from its neighbour.

## Brief for each package

```text
Goal: [one sentence, the plan step it covers]
Contract: [the signatures and shapes above that this package must match]
Paths: [files and directories it may create or edit; everything else is read-only]
Read first: [specs, plan sections, existing artifacts of the same type]
Do not: commit, push, tag, deploy, contact production, send mail or messages, change the contract
Return: results only - what was built (paths), tests run with their result, open questions, contract problems.
        No file contents, no step-by-step narrative.
```

## Fan-out budget

- About four subagents in parallel. More saves little wall-clock time and costs review time in the main session.
- Packages that touch the same files run one after another.

## Never delegate

- Decisions the plan left open, and any assumption break.
- Commits, pushes, tags, deploys, and any contact with production or real recipients.
- Approval requests to the user.
- The final report and the definition-of-done answers.

## When results come back

- Check file and line claims by opening the files. A summary is a claim.
- Run the tests yourself; do not copy a subagent's "all green".
- Compare each package against its contract before integrating the next one.
- A contract problem a subagent reports goes into the deviation rule: small or assumption-breaking.
