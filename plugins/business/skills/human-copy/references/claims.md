# Sourcing claims: numbers, superlatives, testimonials, awards, and the law

## Contents

- The claims register
- Numbers
- Superlatives, "only" and "first"
- Comparisons with competitors
- Testimonials, reviews, logos and awards
- Features that are not built yet
- Legal pointers (verified primary sources, with jurisdiction)
- What was not verified

This is a review-ready draft for writers, not legal advice. Legal pointers name their jurisdiction. When a claim
carries legal risk, a person with the right qualification reviews it; the agent's job is to find the claim, mark
its basis or its absence, and stop.

## The claims register

Keep one small file next to the copy (a table or a list) with one row per claim:

| Field | Content |
|---|---|
| Claim | The sentence as published |
| Fact | The number, name or behaviour behind it |
| Source | A link, an internal measurement query, an invoice, a signed consent, with who and when |
| Scope | What it covers: product, plan, region, period, conditions |
| Owner | The person who confirms it is still true |
| Review date | When it was last confirmed |

Rules:

- A claim that is not in the register is not published. The agent never creates a register row from its own
  imagination; a missing source becomes `{TODO: source}` in the draft and an open question in the report.
- The scope is part of the claim. "Check interval from 30 seconds" and "a check every 30 seconds" are different
  claims when 30 seconds is the minimum and not the default.
- Re-confirm figures that age (customer counts, uptime, prices, benchmarks) at each release of the text, and
  write the period in the sentence ("in March 2026").

## Numbers

- Write a number with its unit, its baseline and what it counts. "7x faster" is a claim about something measured
  against something; say both: "starts {N} s instead of {M} s for accounts with {500} services".
- Use digits for numbers in running web text. NN/g reports that numerals stop the wandering eye and attract
  fixations (https://www.nngroup.com/articles/web-writing-show-numbers-as-numerals/, verified 2026-11-01).
- A number in a sentence reads as proof whether or not it is. The linter does not verify numbers; it only notices
  benefit verbs with no digit (CLM01) and superlatives with no source marker (SUP01). A digit placed only to
  silence the linter is a fabricated claim.
- Usage figures belong to the product and the period that produced them. Do not reuse a figure from another
  product, plan or year.
- Round honestly. Say "about 1,200" only when the exact value is near it.

## Superlatives, "only" and "first"

Words covered by SUP01: best, fastest, easiest, cheapest, safest, biggest, most [adjective], leading, number one,
unmatched, "the only ... that", "the first ... to", "world's first", "100 %", "guaranteed", "risk-free".
German: die beste / schnellste / einfachste ... Lösung, Nr. 1, marktführend, einzigartig, unübertroffen, "der
einzige", garantiert, risikofrei.

How to handle one:

1. Ask: compared with what, measured how, when? If you have those answers, write them into the sentence or the
   line directly after it, with a link.
2. If you only have the product's own measurement, write that and drop the comparison: "Updates appear within {N}
   seconds of posting."
3. If you have neither, delete the claim. A softer superlative ("one of the best") does not fix a missing basis.
4. For "only" and "first": check the full field at the date of writing, name the feature precisely ("the only
   invoicing tool that {specific}"), and keep the evidence in the register. A false "first" is a false statement.
5. A claim about all customers ("customers love it") needs real, representative evidence; one friendly quote does
   not support it.

The linter treats a link, "according to", "source", "benchmark" or "measured" (German: "laut", "Quelle",
"gemessen", "Umfrage") in the same sentence as a source marker. A bare digit does not count, because an invented
figure would otherwise hide an unsourced superlative. The marker is still a heuristic: a human checks that the
basis supports the claim. Customer and user counts ("trusted by over N teams") are flagged separately (CNT01)
because the figure itself needs a dated record.

## Comparisons with competitors

- Compare features that exist on both sides, measured the same way, on a date, with a method a reader can follow.
- Do not describe a competitor's product from memory. Check their current page, and record the URL and date.
- Do not claim to beat competitors on a topic you have not tested end to end. A feature count is not evidence of
  quality.
- Do not use a competitor's name or mark in a way that suggests a connection that does not exist.

## Testimonials, reviews, logos and awards

- Every quote, rating, logo and award has a record: who said it, in which words, when, in what role, and written
  consent to publish. Without that record, do not publish it.
- An agent never invents a customer, a person, a quote, a rating or an award, and never writes a "typical
  customer" quote. Use `{TODO: source}` and flag it.
- Quotes are published as given. Shortening needs the speaker's agreement if the meaning could change.
- Staff, owners and their relatives writing reviews or testimonials is a disclosure issue; ask a human.
- Logos mean "uses the product" in the reader's mind; show only current customers who agreed.
- An award is named (who gave it, which category, which year), not described as "award-winning".
- The linter flags quoted blocks with an attribution line (TST01) so a human checks the record. It cannot verify
  that the person exists.

## Features that are not built yet

Describe what ships today. If a capability is planned, leave it out or state it as the basis for later work
without a date ("This is the groundwork for faster escalation"). Do not describe a planned benefit in the present
tense. German statement on the legal side: § 5 UWG lists availability, advantages and expected results among the
features about which a statement can be misleading (see below).

## Legal pointers (verified primary sources, with jurisdiction)

Each pointer below was read at the primary source on 2026-11-01. They are orientation for a writer, not a
statement that a given sentence is lawful or unlawful.

Germany (UWG, Gesetz gegen den unlauteren Wettbewerb)

- § 5 UWG, misleading commercial practices (https://www.gesetze-im-internet.de/uwg_2004/__5.html). A commercial
  practice is misleading if it contains untrue statements or statements likely to deceive about listed
  circumstances, including the essential features of the goods or services (listed examples: availability, kind,
  advantages, risks, expected results, results of tests) and the person, qualities or rights of the business
  (including awards and honours). Section 5(1) refers to the consumer or another market participant, so the rule
  reaches business-to-business copy as well.
- § 6 UWG, comparative advertising (https://www.gesetze-im-internet.de/uwg_2004/__6.html). Under § 6(2) a
  comparison is unfair, among other things, if it is not objectively related to one or more essential, relevant,
  verifiable and typical features or the price, or if it disparages a competitor.
- Annex to § 3(3) UWG, practices always unlawful towards consumers (https://www.gesetze-im-internet.de/uwg_2004/anhang.html).
  Nr. 23b: claiming that reviews come from consumers who actually bought or used the product, without reasonable
  and proportionate checks that they do. Nr. 23c: submitting or commissioning fake consumer reviews or
  recommendations, and misrepresenting reviews or recommendations on social media for sales promotion. Nr. 4:
  untrue claims that a business or product has been confirmed, approved or authorised by a public or private
  body. The annex covers dealings with consumers; for business-to-business pages the general rule in § 5 is
  the one to check.
- Not verified here: how German courts treat unspecific superlatives (the "Spitzenstellungswerbung" case law).
  Unverified: whether a particular "beste" sentence is acceptable. Treat every superlative as needing a basis, and
  ask a lawyer for a specific wording.

United States (federal)

- 16 CFR Part 465, rule on the use of consumer reviews and testimonials
  (https://www.ecfr.gov/current/title-16/part-465; text read through the eCFR renderer endpoint, which returned
  the current text of the part). Section 465.2 makes it an unfair or deceptive practice for a business to write,
  create or sell a consumer review, consumer testimonial or celebrity testimonial that materially misrepresents
  that the reviewer or testimonialist exists, that they used or had experience with the product, or what their
  experience was; section 465.2(b) reaches a business that disseminates such a testimonial that it knew or
  should have known was misrepresented. Section 465.4 covers buying positive or negative reviews, section 465.5
  insider reviews and testimonials without a clear disclosure of the material relationship, and section 465.6
  company-controlled review sites presented as independent. The definitions in section 465.1 are written around
  consumers; whether a business-to-business testimonial falls under a given paragraph is a question for counsel.
- Not verified here: the penalty amounts and the effective date of the rule; consult the Federal Trade Commission
  or the Federal Register. The press release URL that the research notes name returned 404 at the time of
  writing, so it is not cited.

European Union and other jurisdictions

- Unverified: any EU-level rule text, any national rule outside Germany and the United States. Do not cite them
  from memory. For copy aimed at another country, find the national statute and ask a local reviewer.

## What was not verified

- Behaviour and thresholds of the linter are design judgment (marked as such in SKILL.md rules), not legal tests.
- The reader-penalty finding for text believed to be machine-written is not cited as a rule.
- Anything not listed under "Legal pointers" is not a legal claim of this skill.
