#!/usr/bin/env bash
# An invoicing app whose invoices are scoped by organization.
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
mkdir -p src/invoices
cat > src/invoices/Invoice.ts <<'TS'
export interface Invoice {
  publicId: string;
  orgId: number;
  number: string;
  customerName: string;
  totalCents: number;
  issuedAt: string;
}
TS
cat > src/invoices/InvoiceRepository.ts <<'TS'
export class InvoiceRepository {
  forOrganization(orgId: number) {
    return db.invoices.where({ orgId });
  }
}
TS
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Product: invoicing app for small firms. Multi-tenant: yes, every table carries org_id.
- Plans: docs/plans/YYYY-MM-DD-slug.md, written from docs/templates/feature-plan.md.
- File storage: object storage bucket shared by all organizations, keys prefixed by org.
MD
