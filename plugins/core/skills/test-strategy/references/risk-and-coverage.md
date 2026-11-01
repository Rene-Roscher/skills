# Risk map and coverage gate

Load when you build the risk map, pick levels for the tests, or set a coverage gate.

## The risk map

One table per change, written before the tests. Rows are behaviours, not files.

| Behaviour | Impact if wrong | Changes how often | Critical path | Lowest useful level |
|---|---|---|---|---|
| Refund amount capped at amount paid | money loss | rarely | money | unit on the rule, integration on the stored refund |
| Invoice list only shows own tenant | data leak | often | tenant isolation | integration with two tenants in the database |
| Delete account removes exports | legal, data loss | rarely | deletion | integration plus a check of the storage backend |
| Export button label | cosmetic | often | no | none, or a component test |

Impact comes from the product, not from code size. Ask who is hurt and whether the damage can be undone. A
behaviour is critical when the answer is money, access, another tenant's data, or something that cannot be
undone.

## Allowed and refused cases

For each critical row, write a pair:

- the actor who may do it succeeds, and the stored result is exactly what was asked for;
- the actor who may not (other tenant, lower role, expired session, amount too high) is refused, and nothing
  was stored, sent or charged.

The refused case checks the side effect, not only the status code. A 403 with a row written is a failing test.

## Choosing the level

1. Logic with many branches and no I/O: a fast test on the function.
2. Code that reads or writes through a boundary (database, queue, file, HTTP client): an integration test that
   runs the real boundary or a contract-tested fake. See `verify-before-done` for why the engine must match
   production.
3. Wiring between framework, routes, permissions and views: an integration test through the public entry point
   (HTTP request, CLI command, job dispatch).
4. A journey a customer would call "the product is down" if it broke: one browser test, named in a short list.

A higher-level test that finds a bug no lower one saw means a lower test is missing. Write it, then keep or
drop the higher one.

## Coverage as a map

Use the report to find what no test executes. Read the uncovered lines of every critical module in review. The
report cannot tell whether the executed lines were checked: a test without an assertion covers a line fully.
Mutation testing on the critical modules answers that question: each surviving mutant is a behaviour the tests
do not pin down.

## The gate

- Critical modules: a threshold the team chose, enforced in CI per module or per directory, plus a list of
  excluded generated files with a reason.
- Changed lines: a threshold on the lines a pull request touches, so the suite does not get worse. The Google
  article names 90% as a good lower bound per commit and 99% as reasonable; treat those as examples, since the
  same article says no single number fits every product.
- Global percentage: shown, not enforced.
- A threshold that was never red once proves nothing. After setting it, lower a critical module's tests on a
  scratch branch and confirm the job fails.

## What not to measure

- Number of tests. Duplicated tests across levels cost run time and make behaviour changes expensive.
- Coverage of getters, setters and constructors without logic.
- Percentage of end-to-end tests as a target. The Fowler article and the trophy article both warn against
  fixating on ratios.
