# Failover

Load when designing provider failover for mail, SMS or payments. Library facts below carry the version they
were read at. Re-read the source or docs at your lockfile version before relying on them.

## Questions the ADR answers

1. Where does the "dead provider" mark live: in the transport object (per process), or in shared state?
2. Does traffic return to the primary on its own, and when?
3. How long does a failing primary delay each send before the next provider is tried?
4. What happens when every provider fails: exception, retry, dead letter, alert?
5. Which metric shows traffic moving to the secondary, and who gets the alert?

## Symfony Mailer (used by Laravel's mail)

Read in symfony/mailer v7.4.6 source, 2026-10-31:

- `RoundRobinTransport::send()` tries transports in turn. A transport that throws is marked dead in an
  in-memory `SplObjectStorage` on that transport instance, with a timestamp. When no transport succeeds, it
  throws `TransportException('All transports failed.')`.
- A dead transport becomes eligible again once `retryPeriod` seconds have passed since it was marked.
- `FailoverTransport` extends it and keeps a current transport. It moves on only when the current one is dead.
  Once traffic is on the secondary, it stays there while the secondary works; the primary is tried again only
  after the secondary fails too.
- The dead marks live in the PHP process. Each worker learns about a failing primary on its own, and keeps
  what it learned for as long as it keeps the transport object.

Read in laravel/framework v12.53.0 source, 2026-10-31:

- `MailManager` caches resolved mailers in a per-instance array; `forgetMailers()` clears it. Check whether
  your runtime (long-lived HTTP workers, queue workers) rebuilds or flushes mailers between requests or jobs.
  If it does not, the failover state of the first failure persists until the worker restarts.
- `createRoundrobinTransportOfClass()` reassigns `$config` while looping over the sub-mailers and then reads
  `$config['retry_after']`. At this version the retry period therefore comes from the last listed sub-mailer's
  config, not from the failover mailer's own entry, and defaults to 60 seconds. Confirm this at your version
  before relying on a non-default `retry_after`.
- `LogTransport::send()` writes the message to the log at debug level and returns a `SentMessage`. As the last
  entry of a failover chain it turns a total outage into reported success.

## Mail and SMS

- Tight connect and request timeouts on the primary, so a hanging provider costs seconds, not the queue
  worker's whole timeout.
- One metric per provider for successes and failures, and an alert when the secondary carries traffic.
- Separate chains for alerts, transactional and marketing messages. A reputation problem on the marketing
  stream must not delay a password reset.
- The last step of a chain that matters is a visible failure: the job fails, retries on the queue's schedule,
  lands in a dead-letter table after the last try, and an operator is alerted.

## Payments

- Do not fail a charge over to a second payment provider on a timeout. The first provider may have charged
  the customer; a second charge is a double charge. Resolve the first attempt (reconcile against the provider)
  before trying anything else.
- Failover for payments means routing new checkouts to another provider, with the provider stored on each
  resource, not retrying the same charge elsewhere.

## Drill

Once per chain, in staging: make the primary fail (wrong credentials or a blocked host), send a message, and
check that the secondary delivered it, the metric moved and the alert fired. Then make every provider fail and
check that the job failed visibly. Record the date in the ADR.
