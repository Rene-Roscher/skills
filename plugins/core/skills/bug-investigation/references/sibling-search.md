# Sibling search

## What to search for

Describe the cause as a pattern, not as the one line you fixed:

- The same API misuse: a call without its scope, a comparison of money as floats, a date parsed without a zone.
- The same omission: a missing import or type reference on a branch tests never run, a missing tenant filter, a
  missing authorization check on a sibling action.
- The same shape in neighbouring modules: the controller next door, the other export, the job that copies this
  one.
- The same assumption: code that expects a relation to be loaded, a list to be non-empty, a value to be set.

## How to search

| Strategy | Good for | Tools, as examples |
|---|---|---|
| Text search | Names, calls, literals | ripgrep, grep |
| Structural search | Call shapes, missing arguments, code inside a certain construct | Semgrep, ast-grep, the language's own analysers |
| Token or reference scan | Every class or function referenced in a file, checked against its imports or definitions | A small script over the language's tokenizer |
| Type and static checks | Undefined names, wrong types on untested branches | The project's static analyser at a stricter level for one run |

Record the exact query, the directories searched and the number of hits checked.

## Report

```text
Siblings: searched [query or rule] in [paths]; [n] sites checked, [m] with the same cause
Fixed here: [list, path:line]   Left open: [list with reason, or issue link]
Guard: [test or rule name], fails on [known-positive fixture]
```

## Turn a scan into a guard

- Keep the scan as a test or CI rule when it can run on the whole codebase in seconds.
- Give it a known-positive fixture: a small file with the pattern that the guard must flag. Without it, a guard
  that silently stopped matching looks the same as a clean codebase.
- Allow exceptions only with an inline marker and a reason, so each one is reviewable.
- If the scan has many false positives, narrow it or drop it; a noisy guard gets switched off.
