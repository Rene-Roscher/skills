---
name: audience-gate
description: "Keeps team-facing text out of what customers read: provenance notes (according to the code), roadmap talk (coming in phase 3, in a later version), internal names, placeholders, unrendered keys and build leftovers, checked on the rendered output with a scanner and a full read. Use when writing or reviewing UI strings, locale files, landing or docs pages, mails, before a launch or deploy, or after a release. Not for tone or grammar."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Audience gate

Text a customer reads is written for that customer only. This skill keeps everything written for the team out
of it: notes on how a sentence was sourced, how the product works inside, what is planned, which release
introduced what, and the debris of templates and builds. The failure it prevents is an audience leak: a public
page that says "Instead of [Version] it shows the version of the measuring service. Since version 0.1.5 every
HTTP request carries it", or "this page lists the plan as it is configured in the code". Each leak looks
harmless to its author and unfinished to every reader.

## Applies when / does not apply

- Applies: writing or reviewing any text a customer or visitor sees (UI strings, locale files, landing,
  pricing, docs and help pages, FAQ, mails, notifications, API error messages, status texts, meta and
  structured data); preparing a launch, a deploy or a release; after a release that changes versions or
  feature lists; when an agent wrote text while implementing code.
- Does not apply: tone, grammar and native phrasing (`human-copy`), plural forms and placeholders in locale
  files (`localization`), code comments, commit messages, pull request descriptions, internal docs and
  runbooks. Those are written for the team and may say all of the above.

## Rules

- [invariant] Reader text states what the reader can do or will see today, in the reader's words. It never
  says how the text was produced or checked (according to the code, source: the plan configuration, checked
  against the source), how the product is built inside (internally a service of type X, class names, flags,
  queue names, code names), or what the team plans (phase 3, in a later version, not built yet, backlog, MVP,
  TBD). Why: each of these reached a live page and read as unfinished work to every visitor. Test:
  `audience_scan.py --self-test` reports P01, I01, I02 and R01 for the seeded sentences. Source:
  https://www.nngroup.com/articles/match-system-real-world/ ("speak the users' language ... rather than
  system-oriented terms"), https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
  ("Avoid ... jargon"), both verified 2026-11.
- [invariant] No future features in reader text. Rewrite the sentence to what holds today ("claude.ai cannot
  be connected, because it requires an OAuth sign-in"), or delete it. Plans appear only on a surface the owner
  approved as a roadmap. Why: a promise in a FAQ or a feature page becomes a commitment nobody tracks, and it
  stays after the plan changes. Test: asked to add "coming in phase 3" to a pricing FAQ, the reply refuses that
  sentence and offers a present-tense one (eval `adversarial-phase-three-teaser`). Source:
  https://developers.google.com/style/future ("Avoid documenting future features or products, even in
  innocuous ways"), verified 2026-11.
- [invariant] No placeholder reaches a reader, not even inside an instruction. "Replace [Version] in angle
  brackets with the number in your logs" shows the real value instead and says that it changes ("The version
  changes with every update; filter on the product name"), or names where the reader finds it. A placeholder in
  angle brackets also disappears when the string is rendered as HTML. Why: exactly this sentence reached a live
  page, and a review that read it as "an instruction to the customer" kept it. Test: in a locale file with
  "Replace [Version] with the number in your logs" (angle brackets), the line is rewritten with a real value or
  removed, never kept (eval `output-locale-file-review`).
- [invariant] Evidence lives next to the text, never inside it: a code comment, the commit message or the pull
  request names the file, the config key or the date you checked. Why: an author who wants a sentence to be
  traceable writes the trace into the sentence, and it ships. Test: the scanner reports P01 for "Source: the
  plan configuration" in a table caption.
- [invariant] Review the rendered output, not the source: the production build or the live pages, including
  alt, title, aria-label and placeholder attributes, the title tag, description and Open Graph meta, every
  string in structured data, HTML comments, and pages the sitemap does not list (legal pages, error pages).
  Why: reused blocks, unrendered locale keys, server-rendered start values and build leftovers exist only
  there; a source review passed all of them. Test: the scanner reports K01 for a breadcrumb named
  `nav.pricing` in JSON-LD and B01 for bytes after the closing html tag.
- [invariant] Gate the deploy: run `audience_scan.py` on the production build in CI and fail on errors. A gate
  proves it can fail: `--self-test` is red when one pattern is removed, and `--min-html` stops a build that
  produced fewer pages than expected, so an empty output cannot pass. Why: without a gate, every launch depends
  on someone remembering to look, and a scan of zero pages reports zero findings. Test: remove one pattern from
  the script; `--self-test` names the seeded sentence it missed and exits 1; `--min-html 3` on a folder with
  two pages exits 2.
- [invariant] A scanner is not a review. Before calling a launch done, read every rendered document in full;
  above about 20 documents, split the extract into reading lists and give each reader the same brief. Verify
  each reported finding in the source before changing it. Why: a pattern search found 2 leaks on two sites
  where a full read of the same pages found more than 20, among them sentences no pattern describes. Test: the
  report says "read N of N documents in full" and lists findings as confirmed or rejected.
- [invariant] A shared block (call to action, notice, FAQ template, price note) makes sense on every page that
  renders it. Check each instance, not the template. Why: "In the second group?" pointed at a group order that
  differed per page, and recruited exactly the readers the page told to stay with the competitor. Test: the
  scanner reports D01 for the sentence; the full read decides per page.
- [invariant] A version shown to readers belongs to an artifact they install (an SDK, a provider, a CLI),
  comes from the release source at build time, and is re-read after every release. Release history of your own
  services ("since version 0.1.5") never appears. Why: a provider page named a version one release behind for a
  day, and a tools page explained which internal release added a header. Test: the scanner reports V01; compare
  each shown version with the registry or release feed.
- [invariant] Every page is in its own language, structured data and meta included. A deliberately foreign
  sample (a language showcase, a bilingual boilerplate) goes on the allow list with its reason. Why: a site-wide
  organisation description in one language appeared in the structured data of every page in the other. Test:
  the scanner reports L01 for a German sentence in the JSON-LD of an English page.
- [invariant] Render the real value on the server. A counter that animates from zero, a list that says
  "Loading locations" or a cell that shows "0,00 %" next to "Met" is what crawlers, link previews and readers
  without scripts get. Why: an SLA card read "Met, achieved 0.00 %" in the delivered HTML. Test: the scanner
  reports S01 for a lone "0,00 %" text node.
- [default] When public facts are generated from code (endpoint lists, tool lists, plan limits), a "hidden
  until launch" list in the exporter is reviewed at every launch. Trade-off: one more launch step. Deviate only
  with an ADR that names this trade-off. Test: after a launch, the generated count equals the count the
  product reports.
- [default] Warnings are read by a person and either fixed or allowed with a reason in the allow file; errors
  are fixed. Trade-off: an allow file to maintain. Deviate only with an ADR that names this trade-off. Test:
  an allow line without "# reason" stops the scan.

## Procedure

1. Name the surfaces in scope (site, docs, app strings, mails, API errors) and their languages.
2. While writing, put evidence in comments and the commit message. Read
   [references/leak-taxonomy.md](references/leak-taxonomy.md) for the categories, examples in English and
   German, rewrites and the cases that are allowed.
3. Early check on sources:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/audience_scan.py [locale and content dirs]`.
4. Build for production. Scan the output:
   `python3 ${CLAUDE_SKILL_DIR}/scripts/audience_scan.py [build dir] --locale-keys [locale files] --deny [file] --allow [file]`.
   For a single-page app, save the rendered HTML of each screen with a headless browser
   (`browser-verification`) and scan those files.
5. Full read: add `--extract [dir] --chunks [n]` and hand each reading list to one reader with the brief in
   [references/full-read.md](references/full-read.md). Confirm or reject every finding in the source.
6. Fix, rebuild, rescan. Wire the scan into CI before the deploy step; read
   [references/ci-gate.md](references/ci-gate.md) for the gate, the allow and deny files and the editor hook.
7. After the deploy, scan the live site: `audience_scan.py --site https://example.com`. It reads the sitemap
   and the same-host pages those pages link to.
8. Report: documents scanned, documents read in full, findings fixed, findings allowed and why.

## Traps

- A development server keeps template comments and dev-only text that the production build strips, and the
  reverse holds for some start states. Scan the production build.
- Two prerender routes for one page (with and without a trailing slash) write the same file at the same time;
  the shorter write leaves the tail of the longer one after the closing html tag.
- A locale key that does not exist renders as the key itself, often only in structured data.
- A sentence written as the explanation for a reviewer ("this list comes straight from the code") reads like
  reassurance to its author and like a build note to a customer.
- "Currently still" and "derzeit noch" announce a change the reader cannot plan with. State the current
  behaviour.
- Third-party versions ("Terraform 1.5 or newer") are fine; the scanner warns on them anyway. Allow them with a
  reason instead of deleting the pattern.
- Legal texts that exist in one language only show up as language warnings on the other locale. That is the
  owner's decision, not a text fix.

## Done when

- The production build scans without errors, and every warning is fixed or allowed with a reason.
- Every rendered document was read in full, and the report says how many.
- No reader text describes provenance, internals or plans.
- Shown versions match the release source.
- The live scan after the deploy is clean, and every page ends with one closing html tag.

## References

- [references/leak-taxonomy.md](references/leak-taxonomy.md): read while writing or reviewing reader text,
  for categories, examples, rewrites and allowed cases.
- [references/full-read.md](references/full-read.md): read before a launch review, for the reader brief, the
  split into reading lists and the report.
- [references/ci-gate.md](references/ci-gate.md): read when wiring the scan into CI or an editor hook, or when
  maintaining allow and deny files.
- `${CLAUDE_SKILL_DIR}/scripts/audience_scan.py`: the scanner. `--self-test` checks it against seeded leaks
  and clean fixtures.

## Sources

- https://www.nngroup.com/articles/match-system-real-world/: usability heuristic 2, the system speaks the
  users' language rather than system-oriented terms (published 2018-07-01), verified 2026-11.
- https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/:
  avoid jargon, use the language users are familiar with and use themselves, verified 2026-11.
- https://developers.google.com/style/future: avoid documenting future features, do not pre-announce without
  approval, verified 2026-11.
- `audience_scan.py --self-test`: reproducible check of every scanner rule named above.
