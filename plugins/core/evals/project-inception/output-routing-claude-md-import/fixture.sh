#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/product docs/business docs/specs docs/adr docs/plans
cat > docs/PROJECT-FACTS.md <<'MD'
# Project facts

- Stack: not decided yet; see the inception record.
MD
cat > docs/README.md <<'MD'
# Docs

| Path | Kind | Updated when |
|---|---|---|
| `docs/specs/` | binding | in the same change as the code it describes |
| `docs/plans/` | snapshot after delivery | never; a new plan supersedes |
MD
cat > docs/product/brief.md <<'MD'
# Brief

Status: Draft
Owner: Owner
Skills: none installed, area checklist used
Code: none yet
Checked against code: 2026-03-04

## Problem
Small venues sell tickets through spreadsheets and lose track of who paid.
MD
cat > docs/business/model.md <<'MD'
# Business model

Status: Draft
Owner: Owner
Skills: none installed, area checklist used
Code: none yet
Checked against code: 2026-03-04

## Price model
Open decision 1.
MD
cat > docs/specs/data.md <<'MD'
# Data

Status: Draft
Owner: Owner
Skills: none installed, area checklist used
Code: none yet
Checked against code: 2026-03-04

## Rules
Open decision 2.
MD
cat > docs/adr/0001-record-architecture-decisions.md <<'MD'
# 0001. Record architecture decisions

Status: Accepted
Date: 2026-03-04
Supersedes: none

## Context
Decisions get lost.
## Decision
We keep ADRs in docs/adr.
## Consequences
One file per decision.
MD
cat > docs/plans/2026-03-04-inception.md <<'MD'
# Inception: venue tickets

Status: Draft
Approved-by:
Mode: new
Date: 2026-03-04

## Open decisions
1. Price model: per venue or per ticket?
   - Options: A, per venue; B, per ticket.
   - Trade-offs: predictable revenue against fit to usage.
   - Recommendation: A, because venues budget monthly.
2. ID format: sequential or random public IDs?
   - Options: A, sequential; B, random.
   - Trade-offs: guessable URLs against simplicity.
   - Recommendation: B, because tickets are linked in mails.
MD
cat > AGENTS.md <<'MD'
# Venue tickets

## Read first

| Task | Read first | Skill |
|---|---|---|
| New feature or product change | `docs/product/brief.md`, then a plan | `feature-planning` |
| Migration, model, new table | `docs/specs/data.md` | `dual-key-identifiers` |
| Pricing or plan limits | `docs/business/model.md` | `pricing-and-unit-economics` |
| Commands, versions, providers | `docs/PROJECT-FACTS.md` | `evidence-before-claims` |
MD
cat > CLAUDE.md <<'MD'
# Venue tickets

Answer in English. Keep commits small.
MD
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'chore: initial commit'
