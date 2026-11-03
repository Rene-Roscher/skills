# Schema and resolver

Load when declaring keys, writing the resolver, storing overrides or building the admin editor. The example is an
invoicing app. Code is pseudocode in a typed style; port it to the project's language.

## Contents

- Declaring keys
- Where values live
- Resolution order
- Override records
- Caching
- Admin editor

## Declaring keys

One declaration per key. Everything else (plans, editors, tests, UI labels) is derived from it.

```text
key: seats                     kind: count     unit: members (owner excluded)
  unlimited: null              zero: no extra members
  usage: activeNonOwnerMembers(tenant)
  enforcement: hard            downgrade: pause_excess (deactivate newest, reason=plan_limit)

key: invoices_per_month        kind: count     unit: invoices issued in the billing period
  usage: invoicesIssued(tenant, currentPeriod)
  enforcement: hard            downgrade: block_new

key: data_retention_days       kind: value     unit: days
  floor: 30                    zero: not allowed (below floor)
  downgrade: lossy (grace 30 days, preview, owner notice)

key: api_access                kind: feature   downgrade: block_new (existing tokens refuse calls, kept)

key: einvoice_formats          kind: set       values: [pdf, xrechnung, zugferd]
  downgrade: block_new (existing documents stay downloadable)

key: reminder_sms_monthly      kind: allowance unit: messages, resets per billing cycle
  packs: separate balance, persist
```

Rules for the declaration:

- `kind` decides the merge: counts and values are replaced by overrides and increased by add-ons; features and
  sets are replaced by overrides and never changed by add-ons unless the add-on is itself declared for that key.
- A `floor` exists when the rest of the system breaks or loses data below it (a database check constraint, a
  retention cleanup that cannot be undone). The editor enforces the floor; the resolver clamps to it as well.
- Rate and abuse keys (creates per minute) are declared in their own class and skip add-ons.

## Where values live

- Standard plans: versioned configuration or seeded rows, reviewed like code.
- Custom plans: rows in a plans table with the same key set; a key absent from a custom plan inherits from a
  named parent plan or from the baseline, decided once and documented.
- Overrides: a table, one row per (tenant, key), never a JSON blob on the tenant row.
- Add-ons: subscription-owned rows keyed by entitlement key with quantity, unit price snapshot and pending
  reduction (pricing in `billing-eu-b2b`).

```sql
CREATE TABLE entitlement_overrides (
    id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id       bigint NOT NULL REFERENCES organizations (id),
    key             text NOT NULL,
    value           jsonb,                      -- typed by the schema; null means unlimited for count keys
    reason          text NOT NULL CHECK (length(reason) > 0),
    reference       text,                       -- contract or ticket
    created_by      bigint NOT NULL REFERENCES users (id),
    starts_at       timestamptz NOT NULL DEFAULT now(),
    expires_at      timestamptz,                -- null only with permanent = true
    permanent       boolean NOT NULL DEFAULT false,
    CHECK (permanent OR expires_at IS NOT NULL),
    UNIQUE (tenant_id, key)
);
```

## Resolution order

```text
resolve(tenant, now):
  sub   = activeSubscription(tenant)                 # none → baseline plan
  base  = sub.customPlan ?? catalog[sub.planKey]     # a custom plan replaces, it does not stack
  ents  = schema.defaults() ⊕ base                   # every key present
  for o in overrides(tenant) where o.starts_at <= now and (o.permanent or now < o.expires_at):
      ents[o.key] = validate(schema[o.key], o.value) # replace
  for a in addons(sub) where schema[a.key].addable and allowsBase(ents[a.key]):
      ents[a.key] += a.quantity                      # add on top of the overridden value
  for r in restrictions(tenant):                     # suspension, unpaid, abuse hold
      ents = r.cap(ents); ents.restriction = r.reason
  return clampFloors(ents)
```

`allowsBase` is false for a count of 0 or a feature that is off: add-ons cannot open a closed resource.
Applying add-ons after overrides keeps purchased quantity visible when sales sets an absolute value.

The resolver exposes `can(tenant, key)`, `limit(tenant, key)`, `usage(tenant, key)`, `remaining(tenant, key)`,
`has(tenant, feature)` and `restriction(tenant)`. Nothing else reads plan definitions, override rows or add-on
rows.

## Override records

- Writing an override requires a staff permission and writes an audit row with before and after values.
- Expiry is checked at read time; a cleanup job may archive expired rows but correctness never depends on it.
- The admin view lists overrides expiring in the next 30 days so the account owner can renew or let them lapse.
- An override that lowers a value is allowed (for example a hold) but is shown as such in the tenant's billing
  view, so the customer is not left guessing.

## Caching

- Cache the resolved result per tenant under the tenant's tags, with a TTL no longer than the earliest active
  override expiry.
- Invalidate on: plan edit (all tenants on the plan, via a plan tag), override write, add-on change, subscription
  state change, restriction change, ownership transfer when allowances are per owner.
- Put a shape version in the key (`ents:v3:{tenant}`) and bump it when the cached object changes shape.
- Long-lived workers keep no resolved entitlements between requests.

## Admin editor

- Generate the form from the schema: one field per key, typed, with floor and the "unlimited" control.
- Blank means inherit; an explicit 0 means none. Show the inherited value as placeholder.
- Validate cross-key rules in the schema (for example a per-minute rate may not exceed the per-hour rate).
- A public plan with a price of zero is a second free tier; require it to be hidden or priced.
