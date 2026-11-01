# DNS and mail failover

## Contents

- DNS: delegation and the two-provider model
- DNS: octoDNS sync safety
- DNS: what differs between providers
- Mail: chain design
- Mail: sender identity and failure visibility
- Review checklist

## DNS: delegation and the two-provider model

Two providers only help when both are authoritative. The registrar's NS set must list nameservers of both
providers, and each provider must hold the full zone. Publishing to a second provider that nobody delegates to is a
copy, not a failover.

octoDNS reads records from one or more sources (usually a YAML directory in Git) and pushes the same records to
every provider listed under the zone's `targets`. Example shape, with provider classes left to the vendor docs:

```yaml
zones:
  example.com.:
    sources:
      - config
    targets:
      - provider_a
      - provider_b
```

Source: https://octodns.readthedocs.io/en/latest/getting-started.html (verified 2026-11-01).

Checks:

- The zone has two entries under `targets`, from different vendors and different accounts.
- The registrar delegation lists nameservers of both. Check with `dig NS example.com` against the parent, not
  against one provider.
- Credentials for each provider are separate and are not both held in the system that can fail (for example, both
  only inside the cluster that hosts the product).
- The registrar and the DNS-provider accounts have MFA and a second named owner.
- The zone source lives in Git, so a lost provider account can be rebuilt by pointing the config at a new target.
- Apex and mail records (MX, SPF, DKIM, DMARC, CAA) are in the source of truth, not hand-edited at one provider.

## DNS: octoDNS sync safety

- `octodns-sync` without `--doit` is a dry run. The getting-started guide states that octoDNS assumes ownership of the
  zone and will delete records it does not know about.
- The plan object refuses updates or deletes above 30 percent of existing records when the zone has at least 10
  records, and always refuses a change to the root NS record without `--force`. Zone-level
  `update_pcent_threshold` and `delete_pcent_threshold` settings can change the limits; a provider-level value is
  overridden by the zone-level one.
- `--checksum` lets an apply continue only when the plan's checksum matches the one that was reviewed.

Sources: https://github.com/octodns/octodns/blob/main/octodns/provider/plan.py,
https://github.com/octodns/octodns/blob/main/octodns/cmds/sync.py,
https://github.com/octodns/octodns/blob/main/octodns/manager.py (verified 2026-11-01).

Procedure for a change: run the plan, read every create, update and delete for both providers, compare the two
plans (they should match unless a provider-specific record exists), have the plan reviewed, apply with `--doit`,
then query both providers' nameservers directly. Do not raise the thresholds to make a plan pass.

## DNS: what differs between providers

- Dynamic (geo, weighted, health-checked) records are supported by some providers only. octoDNS pushes the plain
  top-level `values` to providers without dynamic support. Keep those values valid for the whole traffic.
  Source: https://octodns.readthedocs.io/en/latest/dynamic_records.html (verified 2026-11-01).
- Health-check flags such as `status: up|down` are supported by a subset of providers.
- Record limits, TTL minimums and supported types differ. Run the plan against both providers and read the
  validation messages.
- DNSSEC needs a plan of its own: both providers must sign with keys the registrar's DS record accepts. Unverified:
  provider support for multi-signer DNSSEC differs; check each vendor's docs before enabling it on two providers.

## Mail: chain design

A failover transport tries its members in order and moves on when one fails. Laravel configures it as a mailer with
`transport` set to `failover` and a `mailers` list. Symfony uses `failover(a b)` in the DSN. Both also have
`roundrobin`, which spreads load and is not an availability design.

Rules of thumb:

- Members are real sending transports: SMTP or API, from two vendors, on separate credentials.
- Never include `log`, `array` or `null://null` in the chain. Keep them for local and test environments by
  switching the default mailer there, not by adding them as a last resort in production config.
- Production config must not be able to inherit a development default. Add a boot check or a CI check that fails
  when the production default mailer is not the failover mailer; `scripts/ha_check.py` only inspects the chain
  members, not the environment default.
- The retry period after a failed member decides how long traffic sticks to the secondary; set it deliberately.
  Symfony documents a default of 60 seconds, and the Laravel example sets `retry_after` to 60.

Sources: https://laravel.com/docs/12.x/mail, https://symfony.com/doc/current/mailer.html (verified 2026-11-01).

## Mail: sender identity and failure visibility

- Both providers send from the same domain. Publish SPF include entries and DKIM keys for both before an incident, and
  keep DMARC aligned. A secondary that fails DMARC delivers to spam.
- Send in a queue job so a failed send is a failed job with a retry and a count. Alert on the failed-job count and
  on mail queue age through a channel that does not use the mail path.
- Critical alarms (outage, security, backup failure) also go over a path that is independent of product mail.
- Send a test mail through each provider on a schedule, so a revoked key is found on a quiet day.

## Review checklist

- Two providers in DNS, delegated at the registrar, separate accounts, MFA.
- Plan reviewed, no `--force` habit, thresholds untouched.
- No provider-only record type without a static fallback.
- Mail chain of two real transports, no `log`, `array` or `null`.
- Same sender domain authenticated at both mail providers.
- Failure of all providers is loud and reaches a human by another channel.
