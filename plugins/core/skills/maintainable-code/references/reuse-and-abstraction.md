# Reuse and abstraction

Load when you are about to write a helper, or when two blocks look alike and you must decide whether to extract.

## Search before you write

Run the cheapest searches first and record the queries so the report can say what was searched.

1. By name: the verb and the noun you would use (`format_date`, `parseAmount`, `slugify`), and two synonyms.
2. By behaviour: a distinctive literal the helper would contain (a format string, a regex, an error message, a
   constant such as a tax rate).
3. By call shape: how existing code does the same job, for example every place that builds the same kind of
   HTTP client or response. A structural search tool helps here when installed (see `agent-toolbelt`).
4. By location: the shared, common or support directories and the module that owns the domain.
5. By history: `git log -S'name'` finds helpers that were deleted or renamed.
6. By dependency: the framework and the libraries already installed often provide it. Check their docs before
   writing your own.

If you find a near match, extend it with the smallest change that serves both callers, or wrap it. If the near
match needs a new parameter and a new conditional for your case, see below before touching it.

## Extract or duplicate

| Signal | Action |
|---|---|
| First occurrence | write it inline |
| Second occurrence, same reason to change | note it, still inline |
| Third occurrence, same reason to change | extract, name it after the concept |
| Two occurrences that look alike but serve different rules | leave both |
| Copies diverge in a bug fix that must be applied to each | extract now, the reason to change is shared |
| A shared function with a flag or mode parameter per caller | the abstraction is wrong; unwind it |

"Same reason to change" is the test: if one product rule change would force edits in every copy, they are one
concept. If a tax rule changes one copy and a display rule changes another, they are two.

The three-occurrence rule is a heuristic, not a law. The post that argues for duplication over the wrong
abstraction (https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction, verified 2026-11-01) does not give a
number; its test is whether callers need parameters and conditional paths.

## Unwinding a wrong abstraction

Steps from the same post:

1. Inline the shared code back into each caller.
2. In each caller, use the parameters it passed to decide which part of the inlined code it runs.
3. Delete the parts it does not need.
4. Look at what repeats now, and extract from that.

Do this in its own change, with tests passing before and after, so the review is only about structure.

## Seams for testing

When the code to reuse or write calls out, the seam is the interface at that call:

- Pass the dependency in (constructor argument or parameter), typed as a small interface owned by the caller.
- The production adapter implements it with the real client. A fake implements it for tests.
- One adapter per third party, in the application's own types. Provider field names stay inside the adapter.

Check that the seam is real: the unit test constructs the code with the fake and runs without network access,
without patching module globals, and without touching the clock. Ports and adapters are described at
https://alistair.cockburn.us/hexagonal-architecture/ (verified 2026-11-01).

## Reporting

In the hand-over, one line each: what was searched, what was reused, what was left duplicated and why, and which
seams were added.
