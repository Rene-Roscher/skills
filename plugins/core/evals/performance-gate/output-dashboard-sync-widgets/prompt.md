---
description: "A dashboard that computes every widget, two external APIs among them, synchronously and uncached in one request; the gate must ask for per-widget loading, per-tenant caching with freshness TTL and stampede protection or precomputation, and state the cost per view. Run with --scaffold."
expected_outcome: "Reports that all five widgets run in the one Inertia request, so the page waits for the slowest source (about 1.5 s plus 0.8 s plus two aggregates over 1.2 million rows) and fails when one API fails; computes calls and cost per view and per day for the largest workspace (40 users times 25 views); proposes loading the expensive widgets independently, caching each per workspace with a TTL from the needed freshness and stale-while-revalidate with one refresh at a time, precomputing the monthly revenue, and a cold and warm measurement; states which numbers are estimates."
tags: [performance-gate, output]
runs: 3
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

The dashboard works fine on my machine. Is app/Http/Controllers/DashboardController.php ready to hand over for our big customers? Don't change files, just tell me.
