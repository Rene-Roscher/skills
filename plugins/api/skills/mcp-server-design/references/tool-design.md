# Tool design

Load when writing or reviewing a single tool: effect class, name, schema, description, result and error shape,
input normalization, time and money, guard keys and toolsets. Examples use a booking system.

## Contents

- Effect classes
- Build rules
- Names
- Descriptions and server instructions
- Duplicate guards
- Result shape
- Error shape
- Tolerant input
- Language, time and money
- Toolsets for small models

## Effect classes

Every tool has exactly one class. Hint, rate bucket, preview duty and the switch on the connection follow from it.
A tool that spans two classes is split.

| Class | Meaning | Preview | Hints |
|---|---|---|---|
| read | cheap lookup | no | read-only |
| expensive read | aggregations, reports, external sources | no | read-only |
| silent write | changes data, nobody is told | no | write; destructive only when it overwrites |
| notify | mail, SMS, outbound webhook, or anything customers see | yes | through `confirm_action` |
| wake | pages or calls a person | yes | through `confirm_action` |
| alerting | mutes, pauses or reroutes alerts and policies | yes | through `confirm_action` |
| delete | removes for good | yes | through `confirm_action` |

Derive the class from the code path, not the name: walk the service call for events, listeners, observers, jobs and
mails. Raising a priority can wake the next escalation level, which makes `change_booking_priority` a different tool
from `update_booking`. Systems with legal or financial effect add two classes: commit (legally binding, no longer
editable) and move-money; both always use the product UI for approval.

## Build rules

1. Every create has an update; messages have an edit. Edit tools have no notify parameter, so they cannot notify.
2. One tool, one effect. Wake a person through its own tool, not a flag on create.
3. Clear verbs: `create` makes a new object, `update` changes fields, `post` adds a new message, `edit` changes the
   text of an existing one, `publish` or `send` makes public and notifies, `resolve` or `cancel` ends.
4. The server prevents duplicates by a business key, see below.
5. Replay-safe: absolute values (`until`, not "+30 minutes") so the tool can carry `idempotentHint`; replay
   protection on every silent write; check everything before the effect, and when something minor fails afterwards
   return success with a warning, never an error that invites a retry.
6. Read before write: objects and messages carry a `version`; updates require it.
7. Typed handles with a kind prefix. Console links and bare public IDs are accepted as input.
8. Effects only on explicit input: no default on an effect parameter. If the user did not say, ask, in the server
   instructions and in the description.
9. Results lead on: fixed shape with `next_steps` as exact calls.
10. Errors lead on: `Error:` first, cause, fix, the right tool.
11. Fewer, stronger read tools: bundle reads with the same annotation. Do not bundle writes, because hint and
    confirmation apply per tool. No `manage_x(action=...)` catch-alls.
12. Batches need explicit handles, or a filter plus a required `expected_count`.
13. A `list_recent_changes` tool shows what this connection created or changed.
14. Preview before every outward effect.
15. Read input tolerantly, check meaning strictly; never fuzzy-match on a write.
16. Brake loops: the third identical failing call answers "stop, ask the user" and blocks that tool for the token.
17. One text, two lengths: the first paragraph, at most 300 characters, is the whole description in a core set.

## Names

- Short server name. Claude Code shows tools as `mcp__server__tool`, and the whole name is limited to 64
  characters.
- Verb first, object after, plural for batches: `find_bookings`, `get_booking`, `cancel_bookings`.
- `find_` searches with filters, `list_` returns a short full list, `get_` returns one object with everything.
- The dangerous effect is in the name, not in a parameter: `send_booking_confirmation`, `page_oncall`.
- Test confusable pairs on purpose: `post_` and `edit_`, `create_` and `update_`.

## Descriptions and server instructions

English, with the user's domain term in parentheses so search finds it: "maintenance window (Wartung)". Pattern, most
important first:

1. First sentence: what and when, with search terms. Clients search the start.
2. What the tool does not do, as a fact, plus the sibling tool.
3. Effect: who is notified, state afterwards.
4. Parameters: meaning, required decisions, format.
5. One or two short JSON examples in the text; MCP has no input examples field.

Tools with a preview get this appended: "Step 1 of 2: returns a preview and a confirm token; nothing happens until
`confirm_action`."

Server instructions: under 4,096 characters with the core in the first 512, because Claude Code cuts at 4,096. They
say what the server is (one tenant), call `whoami` first, give four rules, two or three workflows, the time and
language rules, handles and the error shape. They add to descriptions and do not replace them; every critical rule
also sits in the description and the result, because several clients drop the instructions. Prompts are a bonus for
guided flows, never a safety mechanism: some clients do not show them.

## Duplicate guards

One business key per create tool, answered with an error that names the existing handle and the right next tool.
Examples: an open booking for the same customer and slot; identical normalized message text within 10 minutes; an
overlapping maintenance window; the same type and normalized target for a resource; the same name ignoring case
within its scope. Creating anyway needs an explicit flag and a reason. A second publish or close is rejected
because it would notify twice; a harmless no-op edit answers `changed: false`. Guards read synchronous columns, not
a queued audit log: a log written asynchronously passes tests with a sync queue and fails in production.

## Result shape

One shape for every tool; text and `structuredContent` carry the same JSON.

```json
{
  "summary": "Booking for Ada Lovelace created as an internal draft. Nobody was notified.",
  "booking": { "id": "bkg_V1StGXR8Z5jdHi6B", "version": "v7", "state": "draft" },
  "notified": { "customers": 0, "oncall": false },
  "warnings": ["Customer language is German; no German text was given."],
  "next_steps": ["Send the confirmation (reaches 1 customer once confirmed): send_booking_confirmation(booking_id=\"bkg_V1StGXR8Z5jdHi6B\")"]
}
```

`summary` is one sentence with state and who was notified. Write tools always carry `notified`, even when zero.
`warnings` hold what the agent should tell the user, including coercion notes. `next_steps` are exact calls with real
handles, each tested verbatim. `replayed: true` marks a replayed result and its summary begins "REPEAT". One-time
values (an API key, an access link) appear only in the first response and never in the replay cache. Compute the
reach of a draft as "if published", so the model can tell the user whom publishing reaches.

## Error shape

```
Error: A booking for this customer and slot already exists (bkg_V1St..., draft, created 4 min ago by this
connection). To change it use update_booking. Only if this is a separate booking: create_booking again with
separate=true and a reason.
{"existing":{"id":"bkg_V1St...","state":"draft"}}
```

First line `Error:` with cause and fix; second line the details as JSON, because some clients read only the text.
`structuredContent.error` carries `code`, `message`, `fix` and the details. Codes: `invalid_input`, `not_found`,
`ambiguous`, `duplicate`, `conflict`, `forbidden`, `not_available`, `unknown_tool`, `rate_limited`, `busy`,
`loop_blocked`, `changed_since_preview`, `awaiting_approval`, `rejected`, `expired`, `internal`. `internal` carries a
reference and says nothing was changed unless the result said otherwise.

## Tolerant input

Normalize against the tool's own schema before validation: `"true"`, `"yes"`, `"1"` to true; `"5"` to 5 for
integers; an array sent as a JSON string to an array; a single value to a one-item array; enum synonyms from a
per-tool table; a handle without prefix, a bare public ID or a console link to a handle; an exact name with one
match to its handle, named in the answer. Several matches return up to five candidates. An unknown field is an
error that lists the allowed fields. Every coercion becomes a note in `warnings`. Writes never fuzzy-match.

## Language, time and money

- Languages: customer-facing languages appear as flat fields in the schema (`title_de`, `title_en`), generated per
  tenant, all required. No nested objects, which small models break. The server never translates; it rejects
  identical text in two languages (short product names excepted) and warns when a text does not look like its
  language. Edits require every required language.
- Time: local time plus an IANA zone, or ISO 8601 with offset, never without. Without a zone the tenant's zone
  applies and the answer says so. The server handles daylight saving. Reject nonexistent local times, give both
  options for ambiguous ones, reject a start in the past unless `start_now` is set, reject an end before the start.
  Every time in a result shows weekday, date, local time with zone, UTC and distance from now. `whoami` returns the
  current time. Call `->utc()` before a model write, or the framework stores only the wall clock.
- Money: the server computes sums, tax and rounding. The model supplies quantity, unit price and a tax code. Amounts
  are decimal strings or integer minor units, never floats.

## Toolsets for small models

| Set | Size | For | Content |
|---|---|---|---|
| Core | about 20 plus `confirm_action` | small and local models, context from 16k | the three or four main flows, `whoami`, `list_recent_changes`, first paragraphs only, at most 5k tokens measured |
| Standard | about 80 | large hosted models in coding tools | everyday work |
| Full | about 120 | admins | plus configuration |

The toolset belongs to the connection. Preload about five tools (`whoami`, the main `find_` tools,
`list_recent_changes`). VS Code allows 128 tools across all servers. A weak model may fail but must never cause
damage: at worst it reads the wrong thing, creates an internal draft that can be discarded, or edits a text that is
versioned and restorable. Everything else needs a confirmation.
