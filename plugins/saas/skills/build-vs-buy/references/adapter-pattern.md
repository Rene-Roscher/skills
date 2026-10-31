# Adapter pattern

Load when integrating a provider. The example is a project tool that stores file attachments in object storage
and wants to be able to change the storage provider.

## Interface and types

- One interface per capability, named after the capability, not the vendor: `ObjectStore`, not `S3Client`.
- Own request and result types. A result carries a provider-neutral status enum (`Stored`, `NotFound`,
  `Rejected`, `Unavailable`) and the provider's own reference as an opaque string.
- Errors are typed: a transient failure (`Unavailable`, timeouts) is distinct from a permanent one
  (`Rejected`), because callers retry one and not the other.
- Capability flags describe real differences between providers, for example `supportsPresignedUploads()` or,
  for payments, `managesSubscriptionCycle()`. The domain branches on a flag, never on the adapter class.
- Vendor SDK classes, exceptions and constants stay inside the adapter namespace. An adapter maps vendor
  exceptions to the interface's error types before they leave it.

```php
interface ObjectStore
{
    public function put(StoreRequest $request): StoreResult;

    public function get(ObjectRef $ref): FetchResult;

    public function delete(ObjectRef $ref): DeleteResult;

    public function supportsPresignedUploads(): bool;
}
```

## The fake

- Lives with the tests and implements the same interface.
- Behaves like the contract, including failure: it can be told to time out, reject, return "not found" or
  return the same event twice. A fake that only succeeds leaves the domain's error handling untested.
- Records what it was asked to do, so tests can assert calls without inspecting HTTP.

## Contract tests

- One suite per interface, parameterised over every registered implementation: the fake and each real adapter.
- The fake runs on every build. Real adapters run against the provider's sandbox in a scheduled or opt-in job,
  with credentials only in that job.
- Each case states the contract, not the vendor behaviour: "get on a deleted ref returns NotFound", "a
  duplicate put with the same idempotency key stores once".
- Fixtures for real adapters come from recorded responses. Each fixture file starts with its source (docs URL
  or the recorded endpoint) and the recording date.

## Provider per resource

- Every provider-backed row stores the provider that handled it (`provider` column holding an enum value).
- A resolver maps the stored value to an adapter. An unknown value throws; it never falls back to a default.
- New work goes to the provider in config; existing resources keep using the provider stored on them until
  they are migrated. Webhooks route by the stored provider.

## Exit path

Write it when the adapter is added, not when the provider is already failing:

1. Export: which data the provider holds and how to get it out (API, bulk export, support request).
2. Dual run: new resources to the new provider, old ones stay, both adapters active.
3. Cut-over flag: a config value that moves new work, reversible without a deploy.
4. What cannot move: check the provider's docs for stored payment credentials, mandates and customer objects.
   Where the docs say nothing, assume customers enter payment details again and plan the communication.
5. Rehearsal: run the switch once in a test environment and write the date into the ADR.
