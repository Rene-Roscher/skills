---
name: video-planning
description: "Plans a short product or explainer video and gets it approved before anything renders: briefing, platform specs, sourced claims, frame-0 cover, story beats, captions, look via style frames, a timing table as approval gate, posting and AI labelling. Use when asked for a video, reel, short, TikTok or product film. Not for rendering, voice or mixing an approved plan."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Video planning

This skill decides what a short product video says, shows and sounds like, and gets that signed off before a
single frame renders. Rendering, voice, sound and mastering belong to `video-production` (same plugin). Platform
syntax and upload screens stay in the platforms' own help pages. The failure it prevents: a finished video that
is rejected as generic, contradicts the product, or misses a platform rule, after the render budget is spent.

## Applies when / does not apply

- Applies: a new short video for TikTok, Instagram Reels, YouTube Shorts, LinkedIn or a website (product film,
  promo clip, explainer, loop); a new language version; a change to the story, script or look of a planned video.
- Does not apply: building, voicing, mixing or exporting a plan that is already approved (`video-production`),
  editing recorded camera footage, live streams, and written social posts without a video.

## Rules

- [invariant] Nothing renders before the plan is approved. The plan document holds the timing table
  (time, picture, speech, caption, sound per row), the script, the fact check, the chosen look and the posting
  package, and the owner signs it off. Why: every correction after rendering costs a render, a review round and
  often voice credits. Test: the plan file carries an approval line (who, date) that predates the first render
  command in the log.

- [invariant] Ask the briefing questions; do not guess the answers. Platform and format, goal and call to
  action, organic or paid, languages, voice and budget, length. Why: each answer changes the cut, the safe zone
  or the cost. Test: the plan header has all six fields filled, none "TBD" at approval.

- [invariant] Platform specs in the plan (aspect, resolution, length, safe zones, loudness, label rules) come
  from the platform's current documentation with the URL and the date read, or carry the word "unverified".
  Why: platform UIs and limits change without notice, and a remembered number is often a year old. Test: every
  spec line in the plan has a URL plus date or "unverified". Source:
  [references/posting.md](references/posting.md) lists the pages checked 2026-11-03.

- [invariant] Every number and product claim in picture or speech is sourced from the product's own specs,
  config or pricing, and checked word by word against what the source says. Dates, times and weekdays shown on
  screen are computed, not typed. Why: viewers screenshot wrong numbers, and "detected in 30 seconds" turns into
  "resolved within 30 seconds" in a script without anyone noticing. Test: the fact-check table in the plan has one row
  per claim with its source; a claim without a source is cut. See `evidence-before-claims` (core).

- [invariant] Frame 0 is the cover. It shows the hook (the first message, the first number, the face of the
  problem) and is never black, empty or mid-transition. Why: the first decoded frame is what players and feeds
  show before playback and the usual fallback cover; a black one reads as a broken upload. Test: the plan
  describes frame 0 in its own row; on the render, `contact-sheet.py --strict` from `video-production` passes
  the first-frame luma check.

- [default] Tell the story as pain, consequence, turn, proof with the real product UI, resolution, payoff.
  Trade-off: a fixed dramaturgy is predictable for longer films and for audiences who already know the product;
  it fits 15 to 75 seconds aimed at people who do not. Deviate only with an ADR that names this trade-off.
  Proof: the transfer table in [references/story-and-look.md](references/story-and-look.md) maps it onto other
  topics.

- [default] A new stimulus every 1.5 to 2.5 seconds (a message, a cut, a zoom, a caption change), and no still
  picture longer than 3 seconds. Trade-off: calm, long shots that suit a website film are ruled out. Deviate
  only with an ADR that names this trade-off. Proof: in the timing table, no row without a picture or caption
  change spans more than 3 seconds.

- [invariant] Captions are whole sentences in sync with the speech and say what the voice says. The video is
  understandable with the sound off. Why: most short video is watched muted at first, and a caption that differs
  from the voice reads as an error. Test: each caption row in the timing table matches its speech row (or is a
  faithful shortening of it) and starts with its first spoken word; a reviewer watching muted can retell the
  story.

- [invariant] Remove words that break the story's logic, even good jokes. Why: a punchline that blamed the
  viewer contradicted a story that promised to take the blame off them, and it was the line people remembered.
  Test: in the read-through, each line either raises the pain, turns it or proves the turn; a line that does
  none is cut.

- [default] Write each language as its own script with its own timing, never a translation of the first one.
  Trade-off: writing and checking each language costs extra. Deviate only with an ADR that names this
  trade-off. Proof: each language has its own timing table; caption lengths and beat times differ where the
  language needs it.

- [invariant] Decide the look with 4 or 5 style frames at the key beats before building the whole video, and
  have them reviewed by an independent image reviewer before the owner sees them. Why: a first draft in a
  default generated look was rejected as generic even though the story had been approved; a look change after a
  full build costs every scene. Test: the plan links the style-frame stills and the reviewer's verdict.

- [default] Use the look rules in [references/story-and-look.md](references/story-and-look.md): a real
  photographic plate with real optical depth of field, real platform UI built to the platform's measurements,
  colour carried by light, one location so time of day holds, restrained motion, no editorial serif and no
  karaoke highlight. Trade-off: more work per shot and heavier assets than flat shapes and stock motion
  templates. Deviate only with an ADR that names this trade-off. Proof: each rejected look in that table came
  back from a reviewer or the owner as generic, fake or illogical.

- [invariant] The posting package is part of the plan: per platform the description, hashtags, link
  placement, cover frame, sound choice and the AI-content label decision with the rule it rests on. Why: the
  label decision depends on what is generated (voice, plates, people), which the plan settles, and platforms
  may remove or restrict unlabelled realistic synthetic content. Test: the package names a label decision per
  platform with a URL and date. Source: https://support.google.com/youtube/answer/14328491 and the pages in
  [references/posting.md](references/posting.md), verified 2026-11-03.

- [invariant] Check the EU transparency duty for synthetic media when the video contains AI-generated or
  manipulated image, audio or video that resembles real persons, objects, places or events and would falsely
  appear authentic (a deep fake in the sense of the AI Act). Review-ready draft, not legal advice; scope EU.
  Why: Art. 50(4) of Regulation (EU) 2024/1689 requires deployers to disclose such content, in a lighter form
  for evidently artistic, creative, satirical or fictional works. Test: the plan states whether any element
  meets that definition and how it is disclosed. Source: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
  (Art. 3(60), Art. 50(4)), text read via https://artificialintelligenceact.eu/article/50/ on 2026-11-03. See
  `eu-de-legal-baseline` (saas) if installed.

## Procedure

1. Gate: read the lessons recorded after earlier videos (`learning-loop`, core). A video plan that repeats a
   recorded mistake is not ready.
2. Briefing: ask the six questions in [references/plan-template.md](references/plan-template.md). Write the
   answers into the plan header.
3. Specs: look up each target platform's current pages and copy the numbers with URL and date into the plan.
   Anything not found is written as "unverified".
4. Facts: list every claim, number, date and time the video will show or say. Source each from the product's
   specs or config. Cut what has no source.
5. Story: write the beats, the frame-0 row, the spoken script and the captions in the timing table. Check the
   stimulus rhythm and read the script aloud once against a timer.
6. Look: produce 4 or 5 style frames (`video-production` builds them), have them reviewed, fix, repeat until
   the reviewer passes them.
7. Posting: fill in the package per platform with [references/posting.md](references/posting.md), including
   the label decision.
8. Approval: send the plan to the owner with the open questions listed. Hand over to `video-production` only
   after sign-off.

## Traps

- The story was approved, the first draft used a default generated look (dark background with a colour
  shimmer, flat UI cards, bold word-by-word karaoke captions, pop-in motion) and was rejected as generic. The
  style-frame gate exists because of it.
- Three synthetic backgrounds (a shader, flat colour fields, a paper texture) were all rejected; a photograph of
  a real room with depth of field was accepted at the first try.
- A daylight plate was used for a scene set at night. A reviewer caught the broken time logic; viewers do too.
- Invented UI details read as fake: the newest notification at the bottom of a stack, a badge on a lock-screen
  card, a relative time without "ago". Copy the platform's real order and wording.
- An on-screen date had the wrong weekday, a four-digit number lacked its thousands separator, and a line break
  split a number from its unit. Each was noticed before anything else.
- A script line said a problem was "fixed" within a time the product only guarantees for detection.
- Links in YouTube Shorts descriptions are not clickable, so a "click below" call to action leads nowhere.

## Done when

- The plan has an approval line, a filled header, a timing table with frame 0 in its own row, a fact-check
  table with a source per claim, the reviewed style frames and the posting package with label decisions.
- Every platform number in the plan has a URL and date or says "unverified".
- Open questions are answered or explicitly deferred by the owner.

## References

- [references/plan-template.md](references/plan-template.md): load when writing the plan document; it holds
  the briefing questions, the header, the timing table and a worked example.
- [references/story-and-look.md](references/story-and-look.md): load when writing the beats or choosing the
  look; it holds the beat timings, the transfer table and the look table.
- [references/posting.md](references/posting.md): load when writing the posting package or looking up platform
  specs; it lists the platform pages checked, with dates.

## Sources

- https://support.google.com/youtube/answer/15424877: Shorts up to three minutes, square or vertical aspect
  ratio, verified 2026-11-03.
- https://support.google.com/youtube/answer/13748639: URLs in Shorts descriptions and comments are not
  clickable, verified 2026-11-03.
- https://support.google.com/youtube/answer/14328491: disclosure of realistic altered or synthetic content and
  its exemptions, verified 2026-11-03.
- https://ads.tiktok.com/help/article/video-ads-specifications?lang=en: 9:16 at 540 x 960 or more, ads up to 10
  minutes, safe zone files per dimension, verified 2026-11-03.
- https://www.tiktok.com/community-guidelines/en-GB/integrity-authenticity?cgversion=2025H2update: label
  AI-generated content that shows realistic scenes or people, verified 2026-11-03.
- https://www.facebook.com/business/ads-guide/update/image/instagram-reels: Reels ads keep about 14 % top, 35 %
  bottom and 6 % per side free, verified 2026-11-03.
- https://eur-lex.europa.eu/eli/reg/2024/1689/oj: AI Act, Art. 3(60) deep fake, Art. 50(4) disclosure; wording
  read via https://artificialintelligenceact.eu/article/50/, verified 2026-11-03.
