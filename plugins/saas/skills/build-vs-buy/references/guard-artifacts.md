# Guard artifacts

Load when adding the CI and test guards to a repository. Each guard turns one rule into a failing build. Add
the ones that match what the repository has.

| Guard | Rule it enforces | Fails when |
|---|---|---|
| Dependency register gate | admission, register | A manifest gains a direct dependency without a register entry, a license is outside the allowlist, or the vulnerability audit has unrecorded findings |
| Architecture test per vendor SDK | own interface | An SDK namespace is used outside the adapters namespace |
| Contract test suite | fake and contract | The fake or a real adapter breaks a contract case; the sandbox job has not been green for longer than the agreed period |
| Fixture provenance lint | no facts from memory | A recorded fixture lacks its source and date header |
| Unknown-channel test | fail loudly | Dispatch to an unregistered channel does not throw, through any entry point |
| Single dispatch path check | fail loudly | A class other than the dispatch service calls an adapter's send method |
| All-providers-down test | no success sink | The send does not fail, or no dead-letter record and alert appear, when every real transport throws |
| Chain mapping test | separate chains | A message class uses the wrong chain, or the alert chain contains a marketing stream |
| Downstream-outage test | off the write path | The core action fails or rolls back when a downstream adapter throws; the reconcile sweep misses the queued work |
| Cache validation test | validated caching | An invalid upstream response is stored, or the upstream is called inside the retry window |
| Cap tests | spend caps | A send exceeds a per-recipient, per-tenant or global cap, or top-up runs while frozen |
| Subprocessor inventory check | compliance event | A provider found in config or enums is missing from the subprocessor register |

## Fixture provenance header

Each recorded fixture starts with two fields, in whatever form the file type allows (a JSON key, a YAML
comment, a sidecar file):

```json
{
  "_source": "https://provider.example.com/docs/api/messages (recorded call to the sandbox)",
  "_recorded": "2026-10-31",
  "id": "msg_123",
  "status": "delivered"
}
```

A test walks the fixtures directory and fails on any file without both fields.

## Single dispatch path check

A structural test lists every call of the interface's send method in the application code and fails when a
caller other than the dispatch service appears. A text search over the source tree is enough to start; an
architecture rule is better where the test tool supports method-level checks.

## Staging drill

The failover metrics and alert are checked by a drill, not a unit test: force the primary to fail in staging,
send one message, and confirm the secondary delivered it, the per-provider metric moved and the alert fired.
Write the date into the provider ADR.
