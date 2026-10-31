---
description: "A plan for a multi-tenant invoice export must plan isolation per surface, a cross-tenant test, the delivery of the file and a rollback. Grant file tools: --allow-tools Write Edit --scaffold."
expected_outcome: "The plan at docs/plans/invoice-export.md has a tenant isolation section that covers the export surfaces, a cross-tenant test in the test plan, says how the file is delivered (signed, expiring download or storage), and has a rollback. The reply asks for approval."
tags: [feature-planning, output]
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
max_turns: 30
timeout_seconds: 900
---

Plan a CSV export of invoices for our multi-tenant app. Write the plan to docs/plans/invoice-export.md.
