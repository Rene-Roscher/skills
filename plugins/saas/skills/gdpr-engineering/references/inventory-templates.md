# Inventory templates and their tests

## Contents
- Layout
- `privacy/inventory.yaml`
- `privacy/subprocessors.yaml`
- `privacy/claims.yaml`
- Coverage tests

Review-ready draft, not legal advice. The field names follow GDPR Art. 30(1)-(2) and 28(2)-(4),
https://eur-lex.europa.eu/eli/reg/2016/679/oj (verified 2026-10). The example is a booking system.

## Layout

```text
privacy/
  inventory.yaml        one entry per data category
  subprocessors.yaml    one entry per provider or outbound host
  claims.yaml           every number or promise that appears in a legal text
  dpia/                 triage notes, linked from inventory entries
```

Keep the files in the application repository, next to the code they describe. Route `privacy/**` and the legal
texts to the person who signs off (CODEOWNERS).

## `privacy/inventory.yaml`

```yaml
- id: guest-contact
  role: processor                 # processor | controller
  purpose: "Send booking confirmations to the venue's guests"
  legal_basis: "per customer instruction (AVV)"   # controller entries: Art. 6(1)(a)-(f)
  data_subjects: ["guests of the customer"]
  categories: ["name", "email", "phone"]
  special_categories: []          # Art. 9 or Art. 10, otherwise empty
  recipients: ["mail-provider", "sms-provider"]   # ids from subprocessors.yaml
  retention: "booking-data"       # key the retention resolver understands
  location: ["EU"]
  sources:                        # where the code holds it
    tables: ["guests.name", "guests.email", "guests.phone", "delivery_logs.recipient"]
    storage_prefixes: ["exports/", "imports/"]
  dpia: "privacy/dpia/guest-contact.md"
```

## `privacy/subprocessors.yaml`

```yaml
- id: sms-provider
  customer_directed: false        # true when the customer points us at their own endpoint
  entity: "[legal entity that signs the contract]"
  country: "DE"                   # where processing happens
  third_country_chain: []         # the provider's own subprocessors outside the EU/EEA
  transfer_basis: "none needed (EU)"   # or "adequacy (Art. 45)", "SCC (Art. 46)"
  data: ["guest-contact"]         # ids from inventory.yaml
  code: ["App\\Notifications\\Channels\\SmsChannel"]
  hosts: ["api.sms.example.com"]
  listed_in: ["avv-annex", "privacy-notice"]
```

## `privacy/claims.yaml`

```yaml
- id: log-retention-days
  sentence: "Access logs are deleted after 14 days."
  document: "privacy-notice"
  config: "logging.retention_days"
  expected: 14
- id: hosting-region
  sentence: "All servers are located in the EU."
  document: "tom"
  check: "every subprocessors.yaml entry with data has country in the EU/EEA"
```

## Coverage tests

Write them in the project's test framework. Each one fails with a message that names the missing entry.

1. Inventory coverage. Read the schema (all tables and columns). A column counts as personal data when it carries
   an annotation or matches a name list (`email`, `phone`, `name`, `ip`, `address`, `birth`, `iban`, free-text
   `note`, `comment`, `message`, `body`), minus an allowlist with a reason per entry. Every such column appears in
   some `sources.tables` list. Input: a migration that adds `bookings.guest_note`. Expected: the test fails until
   an inventory entry lists it.
2. Subprocessor coverage. Collect outbound integration classes (channel, client and SDK service providers),
   SDK packages from the lockfile and hosts from config. Each maps to a `subprocessors.yaml` entry through `code`
   or `hosts`. Input: a new push client. Expected: the test fails until the entry exists.
3. Claims match config. For each claim with `config`, the runtime value equals `expected`. For each claim with
   `check`, a dedicated assertion runs. Input: someone changes `logging.retention_days` to 30. Expected: the test
   fails until the legal text and the claim change together.
4. Inventory schema. Every entry has the required keys, every `recipients` id exists in `subprocessors.yaml`,
   and every `retention` key is known to the retention resolver.
