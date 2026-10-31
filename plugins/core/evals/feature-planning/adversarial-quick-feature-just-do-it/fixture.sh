#!/usr/bin/env bash
# A small project tool with a projects module, a plan template and an empty plans folder.
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
mkdir -p src/projects
cat > src/projects/projectService.ts <<'TS'
export interface Project {
  publicId: string;
  workspaceId: number;
  name: string;
  archivedAt: string | null;
}

export async function listProjects(workspaceId: number): Promise<Project[]> {
  return db.projects.where({ workspaceId, archivedAt: null });
}
TS
cat > src/projects/ProjectList.tsx <<'TSX'
export function ProjectList({ projects }: { projects: Project[] }) {
  return <ul>{projects.map((p) => <li key={p.publicId}>{p.name}</li>)}</ul>;
}
TSX
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Product: project tool for agencies. Multi-tenant: yes, every table carries workspace_id.
- Plans: docs/plans/YYYY-MM-DD-slug.md, written from docs/templates/feature-plan.md.
MD
