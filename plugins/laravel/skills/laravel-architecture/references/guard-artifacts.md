# Guard artifacts

Load when setting up the guard tests in a project, or checking which ones exist. Each artifact starts with a
one-line `Why:` comment and gets one recorded red run. Paths are suggestions; follow the project's test layout.

| Artifact | Proves | Rule |
|---|---|---|
| `tests/Support/IdLeakGuard/*` and the base `TestCase` hook | no internal ID in any feature-test response | ID-leak guard |
| `tests/Feature/Architecture/IdLeakGuardTest.php` | the guard catches a planted body, prop, cursor and redirect leak | ID-leak guard |
| One egress test per channel (broadcast, mail, webhook, export, notification) | payloads outside HTTP carry no internal ID | egress channels |
| `tests/Feature/Architecture/PublicIdTraitCoverageTest.php` | every domain model uses the ID trait, allowlist with reasons | one trait |
| A cross-tenant 404 test per tenant-owned route | a foreign ID answers like a missing one | resolution by external ID |
| `tests/Feature/Security/MassAssignmentTest.php` | privilege flags and tenant pointers survive `fill()` and `create()` unchanged | mass assignment |
| Scoped-exists tests per FormRequest with referenced IDs | another tenant's ID fails validation like an unknown one | scoped validation |
| `tests/Arch/LayersTest.php` | suffixes, base classes, final readonly DTOs, enums, strict types, no debug helpers | layering, enforcement |
| `tests/Arch/BoundariesTest.php` | fenced domains and vendor SDKs stay where they belong | fences, vendor boundaries |
| `tests/Feature/Architecture/NoInlineValidationTest.php` | controllers do not validate inline | FormRequests |
| `tests/Feature/Architecture/NoModelWritesInApiControllersTest.php` | API controllers write through services | one write path |
| `tests/Feature/Api/*ParityTest.php` | web and API store the same state for the same input | one write path |
| `tests/Feature/Architecture/ServiceEntryMethodTest.php` | each service has one public entry method with the chosen name | one use case |
| `scripts/size-ratchet` with `size-baseline.json`, run in CI | controllers and providers don't grow past their baseline | size ratchet |
| CI step: PHPStan with Larastan at a fixed level, committed baseline | the baseline never grows | static analysis |

## Size ratchet in a few lines

Any language the project already uses works. The logic:

1. Read `size-baseline.json` (`{"app/Domains/Billing/Controllers/InvoiceController.php": 412, ...}`).
2. Count lines of every file matching the watched globs.
3. Fail if a listed file exceeds its baseline, or an unlisted file exceeds the soft cap.
4. With `--update`, write the new counts, but only lower values. Raising one needs an ADR.

## Sweeps outside the suite

`python3 ${CLAUDE_SKILL_DIR}/scripts/id-leak-check.py source app/` lists array entries in PHP that put an internal
key into output. Use it when reviewing a codebase that has no guard yet, then install the in-suite guard.
