# Guard artifacts

Checks that make the plan gate hold in a project without relying on the agent. Add them to the target repository
with the owner's approval.

## Plan template in the repository

Copy the template from `references/plan-template.md` of this skill to `docs/templates/feature-plan.md` (or the
project's path) and adapt it: add the project's stack-specific sections, remove the optional one if unused. Point
the project facts file at it.

## Plan linter in the repository

Copy `scripts/lint_plan.py` of this skill into the repository, for example as `scripts/lint-plan`, and run it:

- locally before handing a plan over;
- in CI on every changed file under the plans folder, with `--template docs/templates/feature-plan.md` so the
  required sections follow the project's template;
- with `--multi-tenant` when the project is multi-tenant, or let each plan declare `Multi-tenant: yes`.

Run `--self-test` in CI once after copying, so a broken copy fails loudly.

## Pull request field and CI check

- The pull request template has a field "Plan:" with the path of the plan file.
- A CI job on pull requests labelled as features reads that path and fails unless the file exists and its header
  says `Status: Approved` with `Approved-by:` filled. `feature-delivery` uses the same check as its entry gate.

## Project overlay flag

The project facts file states whether the product is multi-tenant. The linter flag and the plan header follow it,
so the isolation section can't be skipped on a multi-tenant product.

## Decision records

A `docs/adr/` folder with the ADR template. Plans link the ADRs they rely on in Prior art, and answered open
decisions become ADRs.
