# Vendor boundaries

Load when integrating a payment, mail, SMS or storage vendor, or any service you might replace. Which vendors
to buy and which logic to build in-house is decided in `build-vs-buy`.

## Shape

```text
app/Domains/Billing/
├── Contracts/PaymentProvider.php        # interface in domain terms: charge, refund, mandate status
├── Adapters/AcmePayPaymentProvider.php  # the only place that imports the vendor SDK
├── Adapters/FakePaymentProvider.php     # test adapter: in memory, records calls, no network
└── DTOs/PaymentResult.php               # vendor response mapped into domain values
```

- The interface speaks the domain's language. No vendor types in signatures, no vendor status strings past the
  adapter. Map vendor states to a domain enum inside the adapter.
- Amounts cross the boundary as integers in minor units plus a currency code.
- The container binds the interface to the adapter named in config. Tests bind the fake.
- Webhooks from the vendor enter through one controller that stores the raw event and hands it to the adapter
  for parsing. Processing happens asynchronously and idempotently.

## Tests

- A container test: the interface resolves to the configured adapter.
- An arch fence per SDK namespace: `expect('Vendor\Sdk')->toOnlyBeUsedIn('App\Domains\Billing\Adapters')`.
- Domain tests run against the fake adapter. A small contract test suite runs against both the fake and,
  opt-in, the vendor's sandbox, so the fake cannot drift from the real behaviour unnoticed.
- `Http::preventStrayRequests()` in the test bootstrap, so a missed fake fails instead of calling out.

## Built in-house, not delegated to a package

Permissions and roles, tenant scoping, billing rules and plan limits, and the audit log. These carry the
product's invariants, and a package's defaults rarely match them. A package may still provide primitives (a
money library, an HTTP client), wrapped where the domain uses them.
