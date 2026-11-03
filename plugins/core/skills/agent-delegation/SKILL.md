---
name: agent-delegation
description: "Decides when an orchestrating agent hands work to subagents, how many run at once, what the brief holds and which model tier each gets by risk and difficulty: small for lookups, balanced for routine work, strong for planning and business-critical code, top tier only for the hardest problems. Use when planning a fan-out or picking a subagent model. Not for tool choice in one context."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Agent delegation

This skill decides whether work leaves the orchestrator's context, on which model, and at what cost. The
mechanics of one delegation (the brief template, checking a subagent's report) stay in `agent-toolbelt`; this
skill adds parallel work, model choice and the budget. The failure it prevents: a dozen agents spawned on the
most expensive model to grep a repository, while the one change that touches refunds goes to the cheapest.

## Applies when / does not apply

- Applies: a task could be split across subagents; you are about to spawn one; you choose or override a
  subagent's model; several agents are already running and you decide whether to keep them.
- Does not apply: which tool to use inside one context, and the brief template (`agent-toolbelt`); whether a
  claim from a subagent is verified (`evidence-before-claims`); staying on the goal (`goal-focus`).

## Rules

- [default] Delegate only separable work, and only for one of two reasons: its output would flood your context
  (the case `agent-toolbelt` covers), or it can run in parallel with other work and finish sooner. Otherwise
  do it inline. A subagent does not give a smarter answer than the same model inline; a reviewer helps because
  it has not seen your reasoning, which is a different reason. Trade-off: inline work fills your context and
  runs serially. Deviate only with an ADR that names this trade-off. Source:
  https://code.claude.com/docs/en/best-practices ("Know what subagents cost": parallel work, long output and
  a fresh reviewer pay off; a fresh subagent has to gather context again and can be slower; it gives no
  smarter answer; verified 2026-11-03).
- [default] Pick the model tier by the cost of a wrong result first and by difficulty second, as in the tier
  table below: small for lookups, balanced for routine work, strong as the default for planning and anything
  business-critical, top only for the hardest problems. Trade-off: the higher tiers cost more per token and the small tier misses nuance, so a wrong tier either
  wastes budget or produces a confident wrong answer. Deviate only with an ADR that names this trade-off.
  Source: https://code.claude.com/docs/en/model-config (alias descriptions: `haiku` for simple tasks,
  `sonnet` for daily coding, `opus` for complex reasoning, `fable` for the hardest and longest-running tasks)
  and https://code.claude.com/docs/en/best-practices (Haiku fits subagents doing simple jobs; Sonnet costs
  less on routine work), verified 2026-11-03.
- [invariant] Work where a wrong result costs money, access, another tenant's data, deleted data or legal
  standing does not go below the strong tier, and the orchestrator re-checks the decisive part itself. Why:
  these are the paths where a plausible but wrong change passes review and the damage shows up later, at the
  customer. Test: ask the orchestrator to delegate a fix to refund rounding in an invoicing app; the spawn
  names the strong tier or above, and the reply shows the orchestrator ran the refund tests itself. Source:
  none; design judgment, consistent with `test-strategy` (critical paths).
- [default] Use the top tier only for the problems in its row of the table, or after the strong tier failed
  on a good brief. Say why when you pick it. Trade-off: on the API price list (verified 2026-11-03), Fable 5.1
  costs 10 and 50 USD per million input and output tokens against 4 and 20 for Opus 5.5, and it can bill to
  usage credits outside a plan's included limits; reaching for it later means a first attempt was spent on a
  weaker model. Deviate only with an ADR that names this trade-off. Source:
  https://platform.claude.com/docs/en/about-claude/pricing and https://code.claude.com/docs/en/model-config
  (usage credits, Fable is never the default and must be selected explicitly), verified 2026-11-03.
- [invariant] Name the tier on every spawn instead of relying on inheritance. In Claude Code the per-call
  `model` parameter of the Agent tool wins over the agent definition's `model` frontmatter, which wins over the
  `CLAUDE_CODE_SUBAGENT_MODEL` default, which wins over the main conversation's model; the per-call parameter
  takes only the aliases `haiku`, `sonnet`, `opus` and `fable`, while frontmatter also takes a full model ID or
  `inherit`. Other tools have their own mechanism: Cursor reads a `model` field in the subagent file (default
  `inherit`), Codex an explicit spawn value or `agents.default_subagent_model`. Why: an unset model inherits
  the session's, so a session on the top tier runs its searches on the top tier too. Test: in a session on the
  strongest model, ask for a search across a repository; the spawn call carries the small tier. Source:
  https://code.claude.com/docs/en/sub-agents ("Choose a model", resolution order, verified 2026-11-03),
  https://cursor.com/docs/agent/subagents and
  https://learn.chatgpt.com/docs/agent-configuration/subagents (verified 2026-11-03).
- [default] Cap parallel agents at a handful, about three to five, and go above ten only with a stated reason.
  Before each spawn, write one line on what it returns and why that is worth a separate context. Prefer one
  well-briefed agent over several vague ones. Trade-off: fewer agents finish later on wide tasks. Deviate only
  with an ADR that names this trade-off. Source: https://code.claude.com/docs/en/sub-agents (each subagent
  sends its own requests against the same usage limits; many detailed results consume significant context; the
  harness refuses a new spawn at 20 running subagents by default, which is a ceiling, not a target; verified
  2026-11-03).
- [invariant] Never spawn dozens of agents, one per file or per item. Group the items into a few scopes. Why:
  each agent pays its own start-up context, and their summaries still land in yours. Test: ask for a review of
  forty changed files in a project tool; the agent spawns at most a handful, each with a named group of files.
  Source: https://code.claude.com/docs/en/sub-agents (verified 2026-11-03).
- [invariant] Stop an agent that no longer pays off: its question is answered elsewhere, the plan changed, or
  its scope was ruled out. Do not wait for its result out of politeness. Why: a running agent keeps spending
  against the shared limit. Test: two agents search for the cause of a failing booking export; one finds it;
  the orchestrator stops the other before reporting. Source: https://code.claude.com/docs/en/best-practices
  (background work keeps sending requests, verified 2026-11-03).
- [invariant] A brief carries the goal, what is already ruled out, the files to read first, the scope (in and
  out), what the agent may not do, and the result format. Use the template in `agent-toolbelt` and add the two
  fields it lacks: ruled out, and files to read. Its report is a lead: re-run the decisive check yourself, as
  `agent-toolbelt` describes. Why: the agent knows only the brief; without the ruled-out list it repeats your
  dead ends, and without a format you rebuild its answer. Test: every spawn prompt in the transcript names a
  goal, a scope and a result format.

## Model tiers

| Tier | Use for | Claude Code alias |
|---|---|---|
| Small, fast | Search, listing call sites, link checks, mechanical lookups with a cheap check | `haiku` |
| Balanced | Routine, well-specified implementation with tests as the check; review of low-risk code | `sonnet` |
| Strong | The default for planning, and for work touching money, auth, tenant isolation, data loss, legal or security | `opus` |
| Top | Novel architecture, deep multi-system debugging, high-stakes design the strong tier failed at | `fable` |

Other tools name their models differently; keep the tier, map the name.

## Decision table

| Situation | Do | Tier |
|---|---|---|
| One lookup you can run in a call or two | Inline | none |
| Wide search whose raw output you do not need | One agent | small |
| Three independent investigations | Up to three agents in parallel | by risk of each |
| Well-specified change with tests, low risk | Inline, or one agent if parallel | balanced |
| Plan for a feature; change to billing, auth, tenancy or deletion | Inline or one agent, re-checked | strong |
| Review of a diff you wrote | One reviewer agent that has not seen your reasoning | balanced, strong if critical |
| Strong tier failed on a hard multi-system bug | One agent with the failed attempts in the brief | top |

## Procedure

1. Decide inline or delegate with the first rule. If inline, stop here.
2. Split into a few scopes that do not overlap. Writers get disjoint files.
3. Pick a tier per scope from the table; name it on the spawn.
4. Write each brief. Note the expected value in one line.
5. While agents run, stop the ones that stop paying off.
6. Check each report as `agent-toolbelt` describes before it drives a decision.

## Traps

- A built-in search agent that runs on the main conversation's model, so on an expensive session every search
  is expensive. In Claude Code a project agent with the built-in's name and `model: haiku` overrides it
  (https://code.claude.com/docs/en/sub-agents, verified 2026-11-03).
- Passing a full model ID or `inherit` on the Agent tool call; it accepts aliases only.
- A fan-out whose summaries, added up, are longer than doing the work inline would have been.
- Delegating to get a second opinion on your own reasoning by pasting your reasoning into the brief.
- Two writer agents on overlapping files.

## Done when

- Every spawn had a reason (flood or parallel), a named tier and a brief with goal, ruled out, files, scope
  and format.
- Business-critical work ran on the strong tier or above and was re-checked by the orchestrator.
- No more than a handful ran at once without a stated reason, and none ran past its usefulness.

## Sources

- https://code.claude.com/docs/en/sub-agents: model resolution order, aliases on the Agent tool, shared usage
  limits, concurrent-subagent limit, built-in search agent model, verified 2026-11-03.
- https://code.claude.com/docs/en/model-config: alias descriptions, Fable selected explicitly and usage
  credits, verified 2026-11-03.
- https://code.claude.com/docs/en/best-practices: what subagents cost and when they pay off, verified
  2026-11-03.
- https://platform.claude.com/docs/en/about-claude/pricing: per-token prices for Fable 5.1, Opus 5.5,
  Sonnet 5.5 and Haiku 5.5, verified 2026-11-03.
- https://cursor.com/docs/agent/subagents and https://learn.chatgpt.com/docs/agent-configuration/subagents:
  subagent model configuration in Cursor and Codex, verified 2026-11-03.
