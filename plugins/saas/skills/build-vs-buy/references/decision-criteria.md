# Decision criteria

Load when deciding whether to build or buy, or when writing the ADR for a dependency or a provider.

## The six questions

1. Does it encode a rule that customers, auditors or regulators hold you to? Then own it.
2. Do several substitutable providers offer it behind a comparable protocol (SMTP or an HTTP API, the S3 API,
   HTTP webhooks)? Then depend on it, behind an adapter.
3. If it is down, what stops, and is that acceptable?
4. What does leaving cost: data gravity, proprietary formats, tokens or mandates that cannot be moved?
5. Does it process personal data? Then the vendor is a processor (AVV) and possibly a third-country transfer.
6. Can the team maintain it for years, including security fixes?

Questions 1 and 2 decide own or depend. Questions 3 to 6 decide how carefully to depend: adapter or not,
failover or not, and how much exit work to do up front.

## Typical outcomes

| Capability | Usual answer | Reason |
|---|---|---|
| Authorization, roles, tenancy | own | Product rules; a package's defaults become your security model |
| Plan and limit logic, billing rules, invoice content | own | Customers and tax law hold you to them |
| Audit trail, retention and deletion | own | Auditors ask what happened and why |
| Payment processing | depend, behind an adapter | Card and bank networks; a provider carries most of the compliance scope |
| Mail delivery, SMS, voice | depend, behind an adapter, with failover where messages matter | Interchangeable protocols, many providers |
| Object storage | depend, behind an adapter | The S3 API is offered by many providers |
| DNS | depend | Commodity; several providers can serve the same zone |
| Error tracking, metrics | depend, or self-host an open-source option | Commodity; question 5 often decides vendor versus self-hosted |
| Document rendering (PDF) | depend, behind an adapter | Commodity; question 6 decides between a library and a service |

A row is a starting point. The ADR records the answers for the actual case.

## Worked example: SMS reminders in a booking system

- Q1: no. The reminder rule (when, to whom) is product logic and stays in-house; delivering the text is not.
- Q2: yes. Several SMS providers offer HTTP APIs with delivery reports.
- Q3: missed reminders cost no-shows. Acceptable for minutes, not for days, so add a second provider.
- Q4: low. Phone numbers and message history are yours; the provider keeps only delivery logs.
- Q5: yes. Phone numbers are personal data: AVV, subprocessor entry, check where the provider processes data.
- Q6: an adapter of a few hundred lines is maintainable; a self-run SMS gateway is not.
- Decision: depend, behind `SmsGateway`, two providers, spend caps per recipient and per tenant.

## ADR template

```markdown
# ADR-NNN: [capability], build or buy

Status: proposed | accepted | superseded by ADR-NNN
Date: YYYY-MM-DD

## Context
What the product needs and why now.

## Answers to the six questions
1. Rule we are held to:
2. Substitutable providers and protocol:
3. What stops when it is down:
4. Cost of leaving:
5. Personal data and processor role:
6. Maintenance over years:

## Decision
Own, or depend behind [interface], with providers [list].

## Failure behaviour (providers only)
- Where the dead-provider state lives:
- Fail-back behaviour:
- Timeouts on the primary:
- Metric and alert when traffic moves:

## Exit path
- Data export:
- Dual run:
- Cut-over flag:
- What cannot move:
- Last rehearsal: YYYY-MM-DD
```
