# Safety

Load before the first write tool: preview and confirmation, approval modes, replay protection, limits, loop
brake, kill switch, threat model and privacy. No protective rule depends on the model or the client.

## Contents

- Seven layers
- Preview and confirmation
- Replay protection and idempotency
- Limits
- Threat model
- Privacy

## Seven layers

| Layer | Catches | How |
|---|---|---|
| Shape | wrong tool, crowded context | toolsets, clear verbs, flat schemas of at most about six simple fields, short first paragraph |
| Tolerant input, strict meaning | form mistakes of small models | normalization, see `tool-design.md` |
| Domain rules | duplicates, overwrites, wrong time or language, mass damage | guards, replay protection, versions, state checks, `expected_count` |
| Preview then confirm | unwanted outward effect | one-time token, optional approval in the product UI |
| Limits | loops, spam, overloaded workers | buckets per effect and object, loop brake, reserved write slot |
| Way back | damage that happens anyway | silent correction, stored versions with restore, withdraw, discard own drafts, audit with channel |
| Measure | regressions | evals, telemetry per client and model |

## Preview and confirmation

1. A tool with outward effect never executes itself. It calls a side-effect-free `prepare()`, stores the call as a
   pending action and answers with `summary` starting "PREVIEW - nothing has been done yet.", a `preview` of the exact
   effect (recipients per channel and language, texts, amounts, times, affected objects), a `confirm_token`, a
   server-written `confirm_summary` ("Send booking confirmation for bkg_... to ada@example.com") and `next_steps`
   telling the agent to show the preview and wait for the user's go.
2. A person sees the preview and agrees.
3. `confirm_action(confirm_token, confirm_summary)` executes. Only this tool carries the destructive hint and the
   client metadata that forces a prompt (`anthropic/requiresUserInteraction`, `cursor/requiresConfirmation`), so the
   client asks exactly once and the dialog shows the server's own summary.

One `confirm_action` beats a confirm parameter on each tool: preparing tools stay read-only and run without
prompts, so the person confirms once, and a server-wide approval in the client does not skip the confirmation.

`confirm_action` checks, in order: token exists in this tenant and belongs to this connection; not already
executed; not rejected; not expired (10 minutes); browser approval granted if required; `confirm_summary` identical;
lock against parallel confirmation; rights and switches live again; content unchanged since the preview. A changed
content hash returns `changed_since_preview` with a new preview and the old token dead. After executing, mark the
action executed with a status condition and release the lock in a `finally` block.

Content the arguments do not carry needs a hash: when publishing sends text already stored on the object, a
colleague may edit it between preview and confirmation. The preview stores a hash and `confirm_action` prepares
again immediately before executing and compares.

Previews are never served from the replay cache; a repeated preview call makes a second token. The action itself
is protected by the status of the pending action.

Approval modes per connection: in the client (clients that prompt per call) or through an approval URL in the
product (clients that never prompt, local models). Only someone holding the right for the action may approve, and
approve and reject are audited. Honest limit: with in-client approval a client that has prompts switched off can
pass the token through itself. Only product-UI approval guarantees a person, so steps that move money or bind
legally require it.

Pending actions table: public ID (the token), tenant, token and creator of the connection, tool, effect class,
normalized arguments without secrets and their digest, preview including summary and object state version,
approval flag, status (pending, approved, rejected, executed, expired), decider and times. Keep 30 days.

## Replay protection and idempotency

- Fingerprint = token ID + tool + SHA-256 of the canonical JSON of the normalized arguments, keys sorted at every
  level. Window 10 minutes. A hit returns the first result with `replayed: true` and runs nothing.
- Optional `idempotency_key`, 24 hours, bound to the argument digest. The same key with other arguments is a
  `conflict`. Models create a new key when they retry, so the key is an extra, not the protection.
- The cache holds presenter output only, never one-time secrets.
- Applies to silent writes. Notify, wake, alerting and delete run through `confirm_action`.
- Reason: clients must re-send after a broken stream, and in most duplicate cases the agent still reports success.

## Limits

| Bucket | Per token | Per tenant |
|---|---|---|
| Before auth, per address | none | 600 per minute |
| Read | 60 per minute | 240 per minute |
| Expensive read | 20 per minute | 40 per minute |
| Silent write | 20 per minute | 60 per minute and 500 per day |
| Notify | one per object and 60 seconds | 60 per hour |
| Wake | none | 3 per 10 minutes |

Limits sit where damage happens: duplicate mails about one object, not a flat per-minute cap that would break
"create and publish". Raise the buckets in the eval environment and test the 429 answer separately. Concurrency:
two calls per token; per worker one read slot and one slot reserved for writes, so a flood of reports cannot block a
write in an incident; use lock-based slots released in `finally`.

Loop brake: the same failing call (tool plus argument digest, 5-minute window) three times gets "stop, explain the
error and ask the user" on the third failure and the tool is blocked for that token for 5 minutes. Failures that are
not model errors (`duplicate`, `conflict`, `expired`, `awaiting_approval`) do not count.

Kill switch, two levels: a global flag with a CLI command and an admin toggle, both audited, answering every call
with 503 and `Retry-After`; and a per-tenant switch whose default is defined in exactly one place, so a form toggle
cannot silently save false.

## Threat model

| Threat | Countermeasure |
|---|---|
| Prompt injection through third-party text (error messages of probed servers, certificate fields, notes, mail bodies, OCR) | untrusted-text wrapper: truncate, strip control characters, mark as untrusted, leave raw bodies out |
| Injection steers a write tool (changes a target, stored credentials go along) | no default on effect parameters, preview duty, credentials dropped on a target change unless kept explicitly |
| Secrets in output (encrypted casts without hidden decrypt in the array form, masks let fields through) | own presenters with explicit field lists; canary test with bait values |
| Validation bypassed (SSRF, limits, XSS in URLs checked only in a form request) | check in the service, or run the same form requests |
| Privilege escalation (rights frozen into the token, owner shortcut) | live intersection, no ambient user, arch test |
| Tenant break (tenant ID fillable, foreign IDs resolved without scope) | field allowlists, resolve every foreign ID inside the context tenant, per-tool tests with a foreign ID |
| Broadcast before commit | no extra transaction around service calls that dispatch events themselves |
| Arguments and secrets in error trackers and logs | no argument capture, sensitive-parameter attributes, logs with tool name and public IDs only |
| Starved workers | concurrency caps, deadlines, circuit breaker |
| False truth (data source outage cached as "no data") | do not cache, answer `source_unavailable` |

The three biggest risks: third-party text steering tools with outward effect; a service layer that trusts its
caller, which a thin adapter inherits in one move; shared workers that one token can block.

## Privacy

Every tool result goes to the user's model provider, often in a third country. That is the customer's choice and
belongs in the privacy notice, the processing agreement note and the customer docs. Keep presenters lean: only
fields the model needs, for example counts per channel instead of subscriber addresses. Store no IP on connections
and no call log with arguments. Never return special-category data. Connection metadata belongs in the data export.
A new data category, recipient or retention period means updating the processing record and the deletion concept.
