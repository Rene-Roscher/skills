## Contents

- Beats and timings
- Transferring the structure to other topics
- Look rules
- What reviewers flag

## Beats and timings

Timings are for a 30-second vertical video; scale them for other lengths.

| Beat | Time (s) | What happens |
|---|---|---|
| Hook and cover | 0 to 2.5 | Frame 0 already shows the problem: a message, a number, a clock. The first word lands within half a second. |
| Pain | 0 to 4 | The problem gets loud and concrete: messages pile up, a phone buzzes. |
| Consequence | 4 to 7 | What it costs: an angry customer, a lost deal, a weekend gone. |
| Turn | about 7 | A rewind or a cut to "the same moment, with the product". Its own short scene of at least 0.6 s, so the viewer registers the jump. |
| Proof | 7 to 19 | The real product UI does the work, step by step, with real wording and real numbers. |
| Resolution | 19 to 26 | The state flips: open to paid, red to green, conflict to confirmed. |
| Payoff and end | 26 to 32 | One sentence that names the benefit, then the end card with logo and call to action. |

## Transferring the structure to other topics

| Product and topic | Pain (hook) | Proof with real UI |
|---|---|---|
| Invoicing app: missed payment reminder | A client's angry mail on Friday evening: nobody reminded them | Reminder schedule, the reminder mail on the client's phone, the invoice flipping to paid |
| Booking system: double booking | Two guests arrive at the same table at 8 pm | The second booking attempt blocked live, the guest offered the next free slot |
| Project tool: missed deadline | "Where is the release?" in the team chat on launch morning | The deadline warning two days earlier, the task reassigned, the checklist done |
| Support desk: same question 200 times | The support inbox fills with one question | One public status note, the inbox count falling |

## Look rules

The left column is what passed review; the right column is what came back as generic, fake or illogical.

| Layer | Use | Avoid |
|---|---|---|
| Background | A real-looking photographic plate of one place, with real optical depth of field: the subject plane sharp, the room falling off into round bokeh | Shaders, flat colour fields, gradients, paper textures, "dark with a colour shimmer", CSS `blur()` (reads as frosted glass, not as a lens) |
| Interface | Real platform UI (lock screen, notification stack, call screen, mail view, the product's own screens) built to the platform's published measurements, with the platform's order and wording | Invented glass cards, made-up tables, notes on paper |
| Colour of a scene | Carried by light: a red glow from the phone, a cool light at the resolution | Coloured overlays and washes on top of the picture (read as a collage) |
| Place and time | One location for the whole story, lit for the time the story says; a different time of day only on the end card | A daylight plate in a night scene |
| Type | A plain sans for captions, sized for phones, highlight as a solid block behind a word with checked contrast | Editorial serif display type, word-by-word karaoke colouring, poster typography |
| Motion | "100 %, not 120 %": fine, calm, springs without overshoot. Numbers in `video-production` | Shaking, white flashes, overshooting springs, large fly-ins |

## What reviewers flag

Give the image reviewer these as explicit criteria, with pixel positions in its answer:

- Text or UI outside the safe zone, or closer than about 40 px to a button.
- Captions under 4.5:1 contrast against the measured background behind them.
- A notification stack in the wrong order, a badge where the platform shows none, a time without "ago".
- Placeholder squares where an icon belongs.
- Light that does not match the plate (a subject lit from the left in a room lit from the right).
- An object floating: no contact shadow where it touches a surface.
