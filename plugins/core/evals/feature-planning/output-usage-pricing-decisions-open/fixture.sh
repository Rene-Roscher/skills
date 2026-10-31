#!/usr/bin/env bash
# A booking platform with fixed plans in a billing config and a public API.
set -euo pipefail
write_template() {
  mkdir -p docs/templates docs/plans
  cat > docs/templates/feature-plan.md <<'MD'
# Plan: [feature name]

Status: Draft
Approved-by:
Date: [YYYY-MM-DD]
Multi-tenant: [yes or no]

## 1. Problem
- Problem:
- Personas:
- Today:
- Success moment:
- Success metric:
- Non-goals:
- Stress moment:
## 2. Prior art
## 4. UX and states
## 5. Data model
## 6. Reuse
## 7. API and automation
## 8. Events, jobs and caching
## 9. Permissions, limits and audit
## 10. Tenant isolation
## 11. Data protection
## 12. Dependencies
## 13. Performance budget
## 14. Failure modes
| Failure | Impact | Detection | Reaction |
|---|---|---|---|
## 15. Test plan
## 16. Rollout and rollback
- Rollout:
- Rollback:
## 17. Implementation steps
| Step | Location | Done criterion | Depends on |
|---|---|---|---|
## 18. Self-review
## 19. Open decisions
MD
}
write_template
mkdir -p config src/api
cat > config/billing.json <<'JSON'
{
  "currency": "EUR",
  "plans": {
    "starter": { "monthly_net_cents": 2900, "api_access": false },
    "growth": { "monthly_net_cents": 7900, "api_access": true, "api_requests_per_minute": 120 }
  }
}
JSON
cat > src/api/rateLimiter.ts <<'TS'
export function limitFor(plan: { api_requests_per_minute?: number }): number {
  return plan.api_requests_per_minute ?? 0;
}
TS
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Product: booking platform for venues. Multi-tenant: yes, every table carries venue_group_id.
- Plans: docs/plans/YYYY-MM-DD-slug.md, written from docs/templates/feature-plan.md.
- Billing config: config/billing.json. Prices are net, in cents. Changes need the owner.
MD
