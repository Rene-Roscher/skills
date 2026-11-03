# English copy: patterns, calibrated markers, rewrites, genres

## Contents

- Calibration
- Where the word lists live
- Patterns and what to do about each
- The native pass (English)
- Calibrated markers (last reviewed 2026-11-01)
- Rewrite examples (constructed)
- Genre notes: landing page, feature page, changelog, mail, docs
- Review checklist

## Calibration

- No single marker proves who wrote a text. The field guide this skill leans on calls its own list "descriptive,
  not prescriptive", and warns that fixing the signs alone "could just make detection harder"
  (https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing, verified 2026-11-01). It also reports a 2025
  study in which people did no better than chance at telling model text from human text.
- A separate study found that annotators who use LLMs for writing every week were accurate: the majority vote of
  five such annotators misclassified 1 of 300 articles (abstract at
  https://aclanthology.org/2025.acl-long.267/, verified 2026-11-01). Treat that as a reason to expect readers to
  notice generic text, not as a license to guess authorship.
- The problem the markers point at is content that fits any product: the field guide describes models replacing
  "specific, unusual, nuanced facts" with "more generic, positive descriptions" (same page). A sentence that
  fails the substitution test is bad copy whoever typed it.
- Word-level excess is real but era-bound. A study of more than 15 million PubMed abstracts found excess style
  words after 2022 and a lower bound of 13.5 % of 2024 abstracts processed with an LLM
  (https://arxiv.org/abs/2406.07016, verified 2026-11-01). The field guide shows the word lists moving every
  model generation and names one verb as famously overused in 2023 and early 2024, then rare in 2025.
- Marketing buzzspeak is older than language models, and human copy has used "not just X but also Y" for decades.
  Flag position and density, not presence.
- Readers care most in emotional copy. Unverified in this session: a 2025 set of experiments reported that
  believing an emotional marketing message was machine-written lowered word of mouth, with a weaker effect for
  factual messages. Whether or not that holds, factual and specific copy is the safe default.

## Where the word lists live

The tell words, tell phrases and sentence templates are in `scripts/copy_lint.py`, with a last-reviewed date in the
file header. They are kept out of this markdown on purpose: one place to update, and one date to trust. Run the
script; read each hit as "find the fact behind this sentence". The categories:

| Category | Code | Rule of thumb |
|---|---|---|
| Core tell words from 2023 to 2025 output | TEL01 | Any hit in product copy: rewrite. Literal senses (a character called underscore, an identity-provider realm) are fine. |
| Soft tell words | TEL02 | Allowed at about one per 500 words, none in a headline, subject line or button. Delete the word; if the sentence says the same, keep it deleted. |
| Marketing filler | TEL03 | Replace with the proof (the award, the measured lead) or delete. |
| Phrases and templates | TEL04 | Participle tails, significance puffery, importance flags, tradeoff denial, corrective framing, vague attribution, hedges, audience sweeps, summary openers. |
| Connectors | CON01 | Sentence-initial transitions in clusters. Normal in docs when they carry logic. |

## Patterns and what to do about each

1. Negative parallelism ("not just X, but Y", "It's not X, it's Y"). Say Y and drop X. Keep a contrast only when
   readers hold the rejected view and you can cite where (support tickets, forum threads). At most one per page,
   never in a headline or first sentence. Human copy uses it too, so density and position matter, not presence.
2. Corrective framing ("rather than merely", "not simply", "less like X and more like Y"). Delete the straw man.
   Plain "rather than" in a precise changelog line ("labelled Migrated rather than Imported") is fine.
3. Tradeoff denial ("without sacrificing", "without compromising"). Either name the tradeoff and show the
   measurement or state the fact that removes it ("SSO is included on every plan"). Concrete objects ("return to
   the draft without losing changes") are fine.
4. Importance flags ("matters because", "here's why this matters"). Delete the flag; the fact that follows has to
   carry itself.
5. Rule of three. Each item must be concrete (something the reader can click, configure or see), distinct and
   true. If one item is filler, cut to two. No adjective triads as headlines unless each word is proved below.
6. Trailing participle that only comments (", highlighting ...", ", ensuring ..."). Make a real consequence its own
   sentence with a subject and a number; cut the rest.
7. Significance puffery ("a pivotal milestone", "sets the stage"). A changelog says what changed; a feature page
   says what it does.
8. Summary closers and scene-setting openers. Start with what it does; end on the last useful fact or the next
   action. A short functional question is fine: Microsoft's own example is "Ready to buy? Contact us."
   (https://learn.microsoft.com/en-us/style-guide/top-10-tips-style-voice, verified 2026-11-01).
9. Audience and scope sweeps ("Whether you're a X or a Y", "From A to B"). Name the real audience and the real
   scope.
10. Vague attribution ("experts agree", "studies show", "teams tell us"). Name the source with link and date, or
    delete. A quote needs a consenting, real person (see the claims reference of this skill).
11. Category nouns instead of the thing ("solution", "platform", "experience"). Say what it is and does: "Invoices,
    payment reminders and a list of who owes what, in one account."
12. Hedging and chat politeness ("it's important to note", "feel free to reach out", "I hope this helps"). State
    the condition precisely or remove the hedge; answer first.
13. Copula avoidance ("serves as", "boasts", "features" for "has"). Prefer is, has, uses.
14. Headings per paragraph. Add a heading only where a reader navigates. Human READMEs and changelogs are
    heading-dense, so check structure, not count.
15. Formatting residue: emoji at line starts, bold lead-in labels on every list item, markdown in a plain-text
    channel, title-case headings. Style guides agree on sentence case: Microsoft ("don't use title-style
    capitalization"), GOV.UK ("always use sentence case"), Google developer style (see the sources in SKILL.md,
    verified 2026-11-01). The field guide's style page reports that chatbots "strongly tend to capitalize all
    main words" in headings (https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing/Style, verified
    2026-11-01).
16. Em dashes. The field guide moved "overuse of em dashes" to historical indicators for 2022 to September 2026,
    because newer models reportedly avoid them. Treat dashes as a style choice: use a period or colon where the
    dash only adds punch, and never a dash followed by a comma. The linter flags density above 2 per 1,000
    words as a style prompt, not a tell.
17. Exclamation marks. At most one per marketing page; none in docs, notices or errors (Google developer style:
    "In general, avoid exclamation points", verified 2026-11-01).

## The native pass (English)

After the draft, reread only the English, as an editor who writes English natively and has never seen a German
or machine draft of it. For each sentence ask: would a native writer produce this without a source text in
front of them? If not, rewrite the sentence from the fact, do not patch words.

Why a separate pass: asking for natural text up front does not work. In a 2025 study a naturalness instruction
left the translationese rate of GPT-4 output where it was (0.50 against 0.53), while a pass in which the model
polished its own finished output cut it from 43 % to 25 % (Li et al., https://arxiv.org/html/2503.04369,
verified 2026-11-03 in the research). Instruction-tuned models also use nominalisations at 1.5 to 2 times and
present participial clauses at 2 to 5 times the human rate (Reinhart et al., PNAS 2025,
https://pmc.ncbi.nlm.nih.gov/articles/PMC11874169/), which is what the pass removes.

| Pattern | Spot it | Rewrite |
|---|---|---|
| Corporate abstraction | a noun where a person does something: "enablement", "visibility", "alignment", "value delivery" | name who does what: "Your team sees every open invoice on one page." |
| Nominalisation chain | "the creation of", "the management of", "provides the ability to" | the verb: "create", "manage", "lets you" |
| Stacked hedges | two softeners in one sentence: "may potentially", "can help to reduce in some cases" | one condition stated plainly, or the fact |
| Triplets | three adjectives or three abstract nouns in a row | keep the one you can prove; delete the rest |
| Participle tail | ", ensuring ...", ", making it ..." at the end of a sentence | its own sentence with a subject, or delete |
| Calque from German | "since three years", "explain me", "you will become an email" | the corpus list in the collocations reference (CAL01) |
| Wrong register for the surface | brochure words in an error, chat words in a contract | the register table in the register reference |

Then run `copy_lint.py --lang en`.

## Calibrated markers (last reviewed 2026-11-01)

| Marker | Strength | Why it is not proof |
|---|---|---|
| Core tell words (TEL01) | Strong in 2023 to 2025 text, weaker now | Era-bound; literal senses exist; a word overused by models does not mean its synonyms are (field guide). |
| Soft tell words (TEL02) | Weak alone | Appear in human READMEs and landing pages. Use density. |
| Participle tails, significance puffery | Strong in the field guide | A concrete tail ("..., ensuring you can view the value later") is acceptable. |
| "Not X but Y" (NXY01) | Medium | Common in human writing, especially myth-busting. |
| Rule of three (TRI01) | Weak | Concrete triads are normal. Check whether the items are things or adjectives. |
| Em dash density (DSH01) | Weak, historical | Newer models avoid them; typeset human prose uses them. |
| Title-case headings (TTL01) | Medium | House styles for page titles and navigation sometimes use title case; product names stay capitalised. |
| Chat residue, placeholders (RES01) | Decisive | Nobody meant to publish it. |
| Transition openers (CON01) | Weak | The field guide calls transition words in isolation a weak sign and says style guides accept them. |
| Uniform sentence length | Do not gate | No reliable separator between human and model text; split sentences over 25 words for clarity instead (GOV.UK, verified 2026-11-01). |

Domain vocabulary is not a tell. For a booking system "reliable" and "no-show" are core words. Lint the claim
around the word: "98 % of reminders arrived before the appointment in March" is a claim; "reliable reminders" is a
hope.

## Rewrite examples (constructed)

All pairs below are constructed for this skill. Numbers in curly braces stand for real, sourced values and must be
replaced from the facts file; never ship them filled with invented numbers.

Hero line

- Draft: "It's not just scheduling. It's peace of mind for modern practices."
- Rewrite: "Patients book online, get a text reminder {24} hours before, and can move the appointment
  themselves up to {12} hours ahead."
- What changed: the straw-man contrast is gone; the reminder time and the rule are stated; each number comes
  from the product settings.

Feature item

- Draft: "Our vibrant ecosystem of integrations showcases our commitment to your success."
- Rewrite: "Posts task changes to Slack, Microsoft Teams and email. Each integration takes one form to set up."
- What changed: named objects replace the category noun; the second sentence tells the reader what to expect.

Participle tail

- Draft: "We rebuilt the dashboard, ensuring a better experience for every team."
- Rewrite: "The dashboard now loads in {N} s instead of {M} s for accounts with {500} projects."
- What changed: a measured before and after with the condition under which it holds.

Unsourced superlative

- Draft: "The fastest invoicing tool on the market."
- Rewrite A (with proof): "Median time from new invoice to sent PDF: {N} s in our {month year} test of {five}
  tools (method: {link})."
- Rewrite B (no proof available): "The customer gets the PDF within {N} seconds of sending."
- What changed: the claim is either benchmarked with a basis the reader can check or reduced to the product's own
  measured behaviour.

Changelog entry

- Draft: "Improved the flexibility of booking management, further enhancing the guest experience."
- Rewrite: "Bookings can now be moved to another slot. The guest gets an email with the new time."
- What changed: says what the user can now do and what happens to the guest.

Mail opener

- Draft: "I hope this email finds you well! We're thrilled to share some exciting news."
- Rewrite: "Subject: Move a booking without cancelling it. First line: You can now move a booking to another
  slot from the calendar."
- What changed: the subject and first line carry the news; no greeting padding.

## Genre notes

Landing page

- First sentence: what it does and for whom. At least one figure with unit and baseline above the fold, taken from
  the facts file. No contrast headline, no adjective triad, no "solution" as the noun.
- Sentence case for headings and buttons. Buttons say verb plus object ("Create invoice"), not "Get started".
  WCAG asks that link purpose be determinable from the link text where possible
  (https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html, verified 2026-11-01).
- Show real UI, real configuration or real sample output next to claims. Source: none; design judgment.

Feature page

- Each feature: what it does, one concrete example or number, where to find it in the product. Source: none;
  design judgment, consistent with the Microsoft rewrite examples in the page cited above.
- Screenshots and sample output beat adjectives. Name the plan that includes the feature.
- Numbers in digits: NN/g reports that numerals attract fixations while the eye skips words
  (https://www.nngroup.com/articles/web-writing-show-numbers-as-numerals/, verified 2026-11-01).

Changelog and release notes

- Group by Added, Changed, Deprecated, Removed, Fixed, Security; newest first; ISO dates; never a pasted commit
  log ("Changelogs are for humans, not machines", https://keepachangelog.com/en/1.1.0/, verified 2026-11-01).
- Each line names the object, what changed and, for a fix, the failure and the condition. Only changes a customer
  can see or use. No benefit that has not shipped.
- Heading, intro and item titles must not repeat each other.

Mail

- Subject says what is inside, in sentence case. First line answers or announces; no greeting padding. One
  action. Plain text mail carries no markdown. Source: none; design judgment.
- Cold outreach: spell the recipient's company as the company writes it, and use one fact about them you have
  verified, or none.

Docs

- No marketing words, no exclamation marks, no "simply" or "quickly" in procedures, no "please". Start steps with
  a verb. Bold only for interface labels (GOV.UK: bold only for interface elements; verified 2026-11-01).
- Errors and incident notices: what is affected, since when (time and zone), what the reader can do, when the next
  update comes. No hedging stacks.

## Review checklist

- Every number, customer, quote, award and comparison has a source or `{TODO: source}`.
- Substitution test passed: the sentences are false for a competitor.
- Nothing describes a benefit that has not shipped.
- First sentence says what it does; last sentence is a fact or an action.
- At most one contrast per page; triads concrete; no participle tails.
- One term per concept; sentence-case headings; no emoji at line starts; markdown only where it renders.
- No chat residue or placeholder.
- Read aloud.
