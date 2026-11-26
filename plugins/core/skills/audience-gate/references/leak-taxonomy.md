# Leak taxonomy

## Contents

- Provenance notes
- Implementation language
- Roadmap and process
- Release history and versions
- Placeholders and unrendered values
- Text about the text
- Blocks that point at structure
- Wrong language
- Build leftovers
- Allowed cases

Each category lists what leaked, why a reader stumbles, and the rewrite. Scanner codes are in brackets.

## Provenance notes [P01]

The author wanted the sentence to be traceable and wrote the trace into it.

| Leaked | Rewrite |
|---|---|
| This page lists the plan as it is configured in the code. | The values below are the limits the product enforces. |
| Source: the plan configuration. | (delete; cite the pricing page if a source is needed) |
| Checked against the source code of the self-hosted edition, as of 10 November. | Features of the self-hosted edition, as of 10 November: |
| Diese Liste kommt direkt aus dem Code des Servers. | Alle Werkzeuge des Servers, nach Bereichen geordnet. |
| Quelle: die Feldliste des Produkts. | Alle Bedingungsfelder, vollständig. |

The trace goes into a code comment or the commit message.

## Implementation language [I01, I02, I03]

The reader sees screens and results, not models, queues or switches.

| Leaked | Rewrite |
|---|---|
| A monitored server is internally a service of type server agent. | A monitored server uses the same incidents and channels as your checks. |
| Group bookings are behind a feature flag. | (delete until it ships) |
| The BookingExportService writes one file per day. | You get one export file per day. |
| Ein Kunde ist intern ein Kontakt vom Typ Debitor. | Kunden findest du unter Kontakte. |

## Roadmap and process [R01, R02]

A plan in reader text is a promise nobody tracks.

| Leaked | Rewrite |
|---|---|
| SSO is coming in phase 3. | Sign-in works with email and password, and with passkeys. |
| claude.ai support follows in a later release. | claude.ai cannot be connected, because it requires an OAuth sign-in. |
| Der Export ist noch nicht gebaut. | (delete, or say what the reader can do instead) |
| Overrides currently still count towards the planned person. | Overrides count towards the person originally planned. |
| Rebuilding the workers in Rust goes into the backlog for now. | (delete from product pages; a founder's story is the owner's call) |

Words that signal it: phase, milestone, sprint, roadmap, backlog, MVP, TBD, later version, coming soon, not yet
built, currently still, derzeit noch, folgt später, kommt mit.

## Release history and versions [V01]

| Leaked | Rewrite |
|---|---|
| Since version 0.1.5 every HTTP request carries this header. | Every HTTP request carries this header. |
| The current provider version is 0.3.0 (one release old). | Read the version from the registry at build time. |
| Statt [Version] steht dort die Versionsnummer. | Show the real value and say that it changes: "The version changes with every update; filter on the product name." |

## Placeholders and unrendered values [X01, X02, K01, S01]

`<Version>`, `{count}`, `{{ name }}`, `undefined`, `NaN`, `[object Object]`, lorem ipsum, `%s`, TODO, a locale key
such as `nav.abuse` in a breadcrumb, a counter that renders 0,00 % before scripts run, "Loading locations" in
the delivered HTML.

## Text about the text [M01]

"This page lists", "this list comes straight from", "the only reason this page describes". Tell the reader
what the content gives them. A sentence that helps the reader choose ("this page compares the free plans") can
stay; a sentence that explains how the page was built goes.

## Blocks that point at structure [D01]

"In the second group?", "the last point", "see above", "wie oben". Correct in one place, wrong in every other
place that reuses the block. Write the block so it stands alone ("Does the product fit your case?"), or check
each page that renders it.

## Wrong language [L01]

A sentence in the other language: structured data from a site-wide config, a mock that names "Datenbank" on the
English page, a placeholder like `status.deine-firma.de` in an English form, German number formats on English
pages ("99,9 %"), English severity names on a German page.

## Build leftovers [B01, C01]

Bytes after the closing html tag, two closing html tags, HTML comments with sentences in them. Production builds
of most frameworks strip template comments; hand-written HTML and some static generators keep them.

## Allowed cases

- Versions of third-party software the reader runs: "Terraform 1.5 or newer", "Uptime Kuma 2".
- The current version of an artifact the reader installs, generated at build time.
- Dated changelog entries describing what shipped.
- An honest limit stated as today's behaviour: "Overrides count towards the planned person."
- Code examples inside code or pre elements: `<token>`, `{{ name }}`.
- API paths with parameters: `/v2/invoices/{id}/timeline`.
- Escalation levels: "stage 2", "Stufe 1 und 2".
- Topic words in their own domain: a guide on incident processes may say "backlog of action items".
- A deliberately foreign sample: a language showcase, a boilerplate offered in two languages.
- A roadmap page the owner approved as such.
