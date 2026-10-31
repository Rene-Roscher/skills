# When not to extract

An extraction adds a deploy unit, a wire contract, a failure domain, a second toolchain with its own
vulnerability stream, and an on-call surface. Each point below is a reason to keep the work in the monolith.
The ADR answers every one of them.

## Keep it in the monolith when

| Situation | Why it argues against extraction |
|---|---|
| The code is a business decision: billing, permissions, tenancy, pricing or scheduling rules, notifications | decisions spread across separately deployed binaries drift and cannot be corrected in one release |
| The bottleneck is the database | a new service queries the same database, or needs a copy that must be kept consistent |
| The boundary would need a distributed transaction | two commits that must both happen turn into a saga, compensation logic and reconciliation jobs |
| Nobody owns on-call, patching and release signing for the new runtime | the service ages without updates and fails without a responder |
| Measured traffic is below what a tuned monolith handles | the cost is paid now, the benefit never arrives |
| The only argument is language speed | most slow endpoints wait on I/O; see the runtime-fit reference |

## Questions for the proposer

1. Which measured number fails which target, and by how much?
2. Which in-runtime fixes were tried, with what result?
3. What does the Little's-law calculation with the real worker counts say?
4. Which business decisions would the new service take? (The right answer is none.)
5. Which data does it need, and does it get it over the wire or from a database? (Over the wire.)
6. Who is on call for it, and who patches its dependencies?
7. Under which measured condition would you move it back?

## Smaller steps that often solve it

- A queue job instead of a synchronous call.
- A separate queue and worker pool for the slow work.
- A native binary invoked per job (image or PDF tooling) without a long-running service.
- A read model or cache for the hot query.
- Moving a public page to its own deployment (`web-architecture`), which is a separate decision.

## Revert criterion

Write it before the first deploy: "If p95 of X does not drop below Y within Z weeks of rollout, or the service
needs more than N hours of maintenance per month, fold it back." Without one, a failed extraction stays forever.
