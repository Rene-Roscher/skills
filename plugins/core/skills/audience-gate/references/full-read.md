# Full read

A pattern list finds what someone already imagined. A full read finds the rest: a sentence written for a
reviewer, a block that contradicts its page, a claim that no longer holds. On two sites with about 150 pages,
the scanner's patterns of the time found 2 leaks; eight readers who read every page found more than 20.

## Extract

```bash
python3 scripts/audience_scan.py [build dir or --site URL] --extract review/ --chunks 8
```

Each document becomes one text file: the location, the language, the visible text, then attributes, meta,
structured data and comments. `chunk-N.list` files split them into reading lists of similar length. Aim for
about 40,000 words per reader.

## Brief for each reader

Give every reader the same brief, with only the list path changed:

> You review public text of [product], written for [audience]. Read every file in [list] in full, to the last
> line, including the attribute and structured-data block. Report every place that is not written for that
> audience or looks broken:
> notes for the team (how a text was sourced or checked, how the page is built, design terms, instructions to
> an editor); plans and process (phases, later versions, not built yet, backlog); release history of the
> product's own parts; internal names, class names, file paths, flags; placeholders and unrendered values; text
> in the wrong language for the page; blocks that point at structure the page does not have; sentences that are
> unfinished, doubled or cut off.
> Do not report: normal technical terms, competitor names, code examples, example domains and addresses, API
> paths with parameters, legally required statements.
> Change nothing. Answer: "Read N of N files to the end" (name any you did not finish), then findings as
> location · exact quote · reason, certain ones first, borderline ones separately.

## Verify

- Look up every finding in the source before changing it. Readers misread order (a sentence that refers to a
  list rendered after it), mistake extraction artefacts (merged lines, dropped duplicates) for page errors, and
  report deliberate content (a language showcase) as a leak.
- Factual contradictions between pages are a separate list; fix the ones the code settles, and give the owner
  the rest.

## Report

- Documents scanned and documents read in full, per site.
- Findings fixed, each with the page and the old sentence.
- Findings allowed, each with the reason.
- Open decisions for the owner (legal texts in one language, founder statements about plans).
