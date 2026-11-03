# Voice files: how a product's copy learns from its owner

## Contents

- What the files are for
- Where they live
- The files
- Before drafting
- After an owner correction
- From correction to lint rule
- Privacy
- Sources

## What the files are for

A model writes the choice that fits the widest range of readers. A product's owner chooses for one reader, and
those choices are invisible in any single text: "Termin", never "Slot"; "Rechnung", never "Faktura"; du, not
Sie; no "Ups". The only reliable evidence of them is the owner's own corrections and the texts the owner has
already approved. These files keep both, so the next draft starts from them instead of from the model's
default.

Two findings decide the design:
- Real examples of the same kind of text steer tone and structure better than a description of the tone.
  Anthropic's prompting guide calls examples "one of the most reliable ways" to steer output and recommends
  3 to 5 relevant, varied ones; a 2025 study found models can approximate a person's style from samples in
  structured formats such as news and email (Wang et al., EMNLP 2025 Findings, https://arxiv.org/abs/2509.14543).
- Naming a forbidden word in the drafting prompt can make it more likely to appear (Rana, arXiv 2601.08070,
  one 7B model, single-word bans). So the glossary's forbidden variants are checked by the linter after the
  draft, and the drafting step reads the preferred terms and the examples, not the ban list.

## Where they live

Default: `docs/voice/` in the product repository. If the project facts (for example `docs/PROJECT-FACTS.md`,
AGENTS.md or CLAUDE.md) name another path, use that. They are team files, committed and reviewed like code,
not personal agent memory. Start from the templates in this skill's `assets/voice/`.

## The files

| File | Holds | Read by |
|---|---|---|
| `voice.md` | reader, address form, tone per surface, house choices (number grouping, dates, gender approach, legal register) | the agent before drafting |
| `glossary.md` | a table with the columns lang, preferred, avoid, note | the agent (preferred column) before drafting; `copy_lint.py --glossary` after |
| `corrections.jsonl` | one owner correction per line | the agent before drafting (same surface and language); `copy_lint.py --voice-check` |
| `examples/[surface].[lang].md` | 3 to 5 approved, shipped texts per surface and language | the agent before drafting |

A correction line has these fields. The first six are required.

| Field | Content |
|---|---|
| `date` | YYYY-MM-DD |
| `surface` | ui-error, empty-state, button, toast, confirmation, settings, mail, notice, docs, marketing, website, changelog, legal, support |
| `lang` | de or en |
| `before` | the sentence as drafted (one sentence, not the whole text) |
| `after` | the sentence as the owner corrected it |
| `reason` | the owner's reason, verbatim or close; "owner did not say" is allowed |
| `class` | terminology, register, unidiomatic, awkward, inconsistent, locale, accuracy (after the MQM error typology, https://themqm.org/the-mqm-typology/) |
| `rule` | the rule the correction implies, in the same words each time it recurs, so recurrences can be counted |
| `promoted` | empty, or where the rule now lives (glossary row, lint rule, `voice.md` line) |

## Before drafting

1. Read `voice.md` and the `preferred` column of the glossary.
2. Load 3 to 5 texts from `examples/` for the same surface and language. If there are none, say so in the
   report and mark the draft "unreviewed voice". Do not write examples to fill the gap, and do not present a
   draft as matching the house voice when there was nothing to match.
3. Read the corrections for the same surface and language, newest first. Apply each `rule`.

## After an owner correction

When the owner changes your wording, or says what is wrong with it, offer to record it before you continue:
show the `corrections.jsonl` line you would add, and write it after the owner agrees. Record the sentence,
not the paragraph. One correction can produce several lines when it fixes several things.

Do not record:
- a change that only fits this one text ("move this sentence up");
- a factual correction about the product. That goes into the product facts, not the voice;
- anything the owner asks to keep private.

## From correction to lint rule

A rule that recurs gets enforced. The general mechanism (record, check before acting, promote on the second
occurrence) is in the `learning-loop` skill; this is the copy-specific part:

- When the same `rule` appears twice, or the owner says "always" or "never", promote it:
  - a term or phrase goes into `glossary.md` (`avoid` column). `copy_lint.py --glossary` then flags it as GLO01;
  - a pattern the glossary cannot express (a sentence shape, a punctuation habit) goes into the project's
    own lint configuration or into `voice.md` with a test sentence;
  - set `promoted` on the correction lines.
- `copy_lint.py --voice-check docs/voice` reports a rule seen twice and not promoted (VOI02), malformed
  lines (VOI01), missing files or examples (VOI03) and personal data in a correction (VOI04).
- When a correction contradicts an earlier one, ask which holds, then mark the older line in its `reason`
  ("superseded YYYY-MM-DD") instead of keeping both as rules.

## Privacy

Corrections and examples are committed and read by every agent session. Keep customer names, personal data,
private mail and support conversations out of them. From a customer case, keep only the sentence
shape. The voice check flags email addresses and phone numbers (VOI04), and it cannot catch anything else.

## Sources

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices:
  examples steer tone and structure; 3 to 5; tell the model what to do instead of what not to do (verified
  2026-11-03 in the research).
- https://arxiv.org/abs/2509.14543: style from user samples works for news and email (verified 2026-11-03).
- https://arxiv.org/abs/2601.08070: naming a forbidden word primes it (one model; verified 2026-11-03).
- https://arxiv.org/abs/2404.15269: learning a preference from user edits, retrieved by similar context
  (verified 2026-11-03).
- https://themqm.org/the-mqm-typology/: error classes for corrections (verified 2026-11-03).
- https://docs.vale.sh/keys/vocabularies: accept and reject vocabularies as a lint model for a glossary
  (verified 2026-11-03).
