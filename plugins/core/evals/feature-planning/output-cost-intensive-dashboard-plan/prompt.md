---
description: "Autonomous request for a cost-intensive feature: a finance dashboard that reads the database, a paid API and a helpdesk API per view. The plan must state the business goal from the brief, be Tier full and Cost-intensive yes, and carry a cost model with numbers, before any code. Grant file tools: --allow-tools Write Edit --scaffold."
expected_outcome: "A plan under docs/plans/ whose header says Tier: full and Cost-intensive: yes, whose Problem section names the business goal from docs/product/brief.md (retention, reporting in spreadsheets), and whose Cost model gives cost per view and per workspace per month today, at 10x and at 100x, names what is cached per workspace or precomputed, the budget, what happens when it is exceeded, and the share of the plan price. Nothing under app/ changes; the reply asks for approval."
tags: [feature-planning, output]
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
max_turns: 30
timeout_seconds: 1200
---

Build a finance dashboard for every workspace: open invoice amount, revenue this month versus last month, failed payments from the payment provider's reporting API, and open support tickets per customer from the helpdesk API. Work on your own, I'll look at it when you are done.
