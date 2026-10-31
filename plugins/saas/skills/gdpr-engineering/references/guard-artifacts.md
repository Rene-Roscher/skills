# Guard artifacts

## Contents
- Tests and checks
- Pull request template
- CODEOWNERS
- Path-scoped rule

Each guard turns a rule of this skill into something CI runs. Names are suggestions; use the project's test
layout. The inventory, subprocessor and claims templates are in the inventory-templates reference of this skill.

## Tests and checks

| Guard | Recipe: input, expected result |
|---|---|
| Inventory coverage | a migration adds a column named or annotated as personal data without an inventory entry: the test fails |
| Subprocessor coverage | a new outbound client, SDK package or configured host without a `subprocessors.yaml` entry: the test fails |
| Legal claims match config | a config value behind a claim changes: the test fails until claim and text change too |
| Erasure completeness | seed one person into every table and storage prefix the inventory lists, erase, search a database dump and the storage listing for email and name: zero hits |
| Person foreign keys | list foreign keys that reference people with `RESTRICT` or `NO ACTION`: the list is empty |
| Retention | per plan and account state, records one day inside the window survive and one day outside are gone; invoices survive account erasure with non-required fields cleared |
| Error-tracker scrubbing | a connection error on an authenticated HTTP client, captured through a fake transport: the event holds no token, cookie or request body |
| Production ini | inside the production image, `php -r 'exit(ini_get("zend.exception_ignore_args") ? 0 : 1);'` exits 0 (or the accepted SDK alternative is configured and tested) |
| Log redaction | a log call with an IP and a token: the line holds the masked IP and a short hash prefix only |
| Generic errors | a failing export or import: the stored and displayed message is the curated one, not the exception text |
| No third-party avatars | CSP `img-src` holds no third-party avatar host; a grep for an email hash inside an image URL finds nothing |
| Message purpose | a promotional send without consent or exception record throws; promotional mail has an opt-out link and `List-Unsubscribe` |
| Cookies before consent | a browser test lists cookies and storage keys before consent: every key is on the allowlist with a reason |
| Export isolation | tenant B requests tenant A's export: 404; the unzipped archive holds no integer `id` fields |
| Default locations | the default region or location selection holds only EU/EEA or adequacy entries |
| Legal URLs | a scheduled check requests every legal URL in every offered language: all return 200 |
| Synthetic fixtures | a lint over seeders and fixtures finds no email domains outside example.com, example.org, example.net |

A guard test that matches nothing passes silently. Run guard tests as a whole directory and assert a minimum
number of checked items (tables, classes, hosts), so an empty scan fails.

## Pull request template

```markdown
### Privacy
- [ ] No privacy trigger. Reason:
- [ ] Personal data added or changed: inventory entry
- [ ] New provider, SDK, host or channel: subprocessors.yaml, AVV annex, privacy notice, transfer check
- [ ] Retention or cleanup changed: retention schedule, VVT, claims.yaml
- [ ] Processing or access outside the EU/EEA: transfer basis
- [ ] Art. 9 or Art. 10 data, profiling, monitoring: DSFA triage note
- [ ] User content: privacy notice, DSA notice and statement of reasons
- [ ] Promotional or lifecycle mail: purpose and consent or exception record
- [ ] Cookies or device storage: allowlist entry with reason
```

## CODEOWNERS

```text
/privacy/            @your-org/privacy-signoff
/resources/legal/    @your-org/privacy-signoff
```

Replace the team and the legal-text path with your own.

## Path-scoped rule

Claude Code loads a rule in `.claude/rules/` with a `paths` list when it reads or edits a matching file, and it
supports brace expansion in the patterns (https://code.claude.com/docs/en/memory, verified 2026-10). The skill
itself sets no `paths`, so it stays available in planning. Copy this into `.claude/rules/privacy.md` and adjust
the globs:

```markdown
---
paths:
  - "database/migrations/**"
  - "**/*{Mail,Notification,Channel,Export,Delete,Erasure,Retention,Cleanup,Avatar}*"
  - "config/{logging,sentry,services,mail}*"
  - "**/privacy/**"
  - "**/legal/**"
---

This file touches personal data, a provider, retention or legal text. Load the gdpr-engineering skill and run
its trigger table before finishing the change.
```
