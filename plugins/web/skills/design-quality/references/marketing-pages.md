# Marketing pages

## Contents

- Show the product in the first viewport
- Mock-ups speak the product's language
- Hero: one headline, one sentence, at most two actions
- Claims: every number is true and traceable
- Social proof
- Page weight and layout shift
- Copy

Applies to landing, pricing and feature pages. The words themselves (headlines, voice, formulas) belong to a
copywriting skill; this file covers structure, evidence and the checks.

## Show the product in the first viewport

Real product UI, as DOM built from the product's components or as a current screenshot, with realistic data, in
or just below the first viewport. Unverified this session: how far down the page each studied site starts its product UI; an
earlier measurement put it at roughly 530 to 560 px of a 900 px viewport on two sites.

An abstract hero works for a brand that people already know. For a product that people still have to understand,
the frontend-design skill's guidance applies: open with "the most characteristic thing in the subject's world"
(https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md, verified 2026-11-01).

Check: mark the product UI with `data-testid="product-ui"`; the audit with `--marketing` fails when no such
element exists or when its top edge is below 1.3 viewport heights.

## Mock-ups speak the product's language

- Build mock-ups from the product's own components, or reuse the strongest mock-up the site already has. A generic
  browser frame with grey bars reads as a wireframe.
- Data is realistic: plausible IDs, durations, amounts, log lines, warnings. No "John Doe", lorem ipsum or round
  placeholder numbers; the audit warns on the first two.
- Text inside a DOM mock-up is still text. Either it meets 4.5:1, or the mock-up is exposed as an image with a text
  alternative. Screen readers and search engines read DOM text. WCAG exempts text that is "part of a picture that
  contains significant other visual content" (1.4.3); whether a DOM-rendered mock counts as a picture is a
  judgement call, so decide it and write it down.
- Small uppercase captions on metrics are fine when they label data; compute them against the muted foreground in
  both themes.

## Hero: one headline, one sentence, at most two actions

- One headline, one supporting sentence, at most two buttons. This is a design default, not a measured law.
- Sentence case on marketing pages. The Web Interface Guidelines use Title Case for the vendor's own product and
  say: "On marketing pages, use sentence case." (https://github.com/vercel-labs/web-interface-guidelines, verified
  2026-11-01).
- A button says what happens: "Create your first invoice", not "Continue" or "Submit". The guidelines' example:
  "Save API Key" instead of "Continue"; the frontend-design skill: "A CTA says exactly what happens when it is
  used".
- One accent hue for actions and highlighted data; a neutral primary button is a valid choice.
- Check: the audit fails when the hero holds more than two buttons. The hero is the nearest `section`, `header` or
  `[data-hero]` ancestor of the first `h1`.

## Claims: every number is true and traceable

Keep a claims file in the repository, one entry per figure on the page:

```yaml
- id: invoices-sent
  text: "[count] invoices sent in [month, year]"
  value: "[count]"
  unit: invoices
  period: "[month, year]"
  source: "internal report name or public URL"
  checked: "[YYYY-MM-DD]"
  owner: "role, not a person"
```

- Each figure names subject, unit and period ("in 2025"), or a named customer. A number that stands
  alone, without subject or period, cannot be checked.
- No invented customer counts, uptime figures, ratings or growth rates. An invented figure is a false statement to
  buyers.
- Mock-up data is not a claim, but it must not look like one: a chart titled "Revenue" with a precise percentage
  reads as a result.
- CI: extract every sentence with a digit from marketing pages and fail when no claims entry matches. Dates, plan
  names and prices from the pricing config are exempt through an allowlist, not through silence.
- Numerals for counts, a non-breaking space between number and unit, and one currency convention per context (0 or
  2 decimals, never both) come from the guidelines' content rules.

## Social proof

Logos, quotes and case studies only from real customers who agreed, with the permission recorded in the claims
file. Attribute quotes to a real person and role. Do not buy reviews on condition of their sentiment, do not post
reviews from insiders without disclosure, do not show fake follower or view counts.

The US Federal Trade Commission's Consumer Reviews and Testimonials Rule has been in effect since 21 October 2024
and covers: fake or false reviews and testimonials (section 465.2), buying reviews conditioned on sentiment
(465.4), undisclosed insider reviews (465.5), company-controlled review sites that claim independence (465.6),
review suppression (465.7) and fake indicators of social media influence (465.8). Staff guidance:
https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers (verified
2026-11-01). The same guidance says it is not definitive or complete and gives no safe harbour. Not legal
advice; this is the US rule only, other jurisdictions add their own, and an EU or German review is the user's
responsibility to commission. Unverified: EU consumer-law provisions on fake reviews were not checked for this
file.

One detail from the staff guidance that matters for marketing pages: when a business features consumer reviews in
its own advertising or marketing materials, they count as testimonials, and the exemption for merely hosting
reviews does not apply.

## Page weight and layout shift

From the guidelines' performance section: explicit image dimensions, preloaded critical fonts, subset fonts, video
instead of animated GIF with a still fallback that honours reduced motion, and preload only above-the-fold images.
Measure layout shift with the performance tooling of the project; this skill does not set budgets.

## Copy

Words are design content. Describe what something is or does in plain terms rather than selling it (the
frontend-design skill's wording). Headline formulas and vocabulary are a copywriting concern and are not covered
here.
