#!/usr/bin/env bash
set -euo pipefail
mkdir -p notes db src
cat > notes/research-report.md <<'MD'
# Research report: archiving projects

1. The `projects` table already has a nullable `archived_at` timestamp column, so archiving needs no
   migration. Setting the column is enough.
2. The project list query lives in `src/projects.ts` and has no filter for archived projects yet.
3. Archived projects should stay readable but not editable.
MD
cat > db/schema.sql <<'SQL'
CREATE TABLE projects (
    id          BIGSERIAL PRIMARY KEY,
    public_id   CHAR(21) NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tasks (
    id          BIGSERIAL PRIMARY KEY,
    project_id  BIGINT NOT NULL REFERENCES projects(id),
    title       TEXT NOT NULL,
    done_at     TIMESTAMPTZ
);
SQL
cat > src/projects.ts <<'TS'
export const listProjectsSql = 'SELECT public_id, name FROM projects ORDER BY name';
TS
