# Architecture tests per stack

Load when writing or extending the boundary test. Each example is a starting point; check the option names
against the docs for the installed version with a documentation index tool, such as Context7, before copying.

## Contents

- What every stack's test must do
- PHP with Pest
- Go
- TypeScript with dependency-cruiser
- TypeScript with eslint-plugin-boundaries
- Map diff, naming and table checks
- Seeing it fail

## What every stack's test must do

1. Keep each context's interior private: only its own code imports it.
2. Allow only the edges in `docs/CONTEXT-MAP.md`, downstream importing the upstream's public surface.
3. Fail on a context-level cycle.
4. Fail when it matches nothing (a renamed folder must not turn the test green).

## PHP with Pest

Arch expectations `toOnlyBeUsedIn`, `not->toUse`, `ignoring` and namespace wildcards are documented at
https://pestphp.com/docs/arch-testing (checked via Context7, 2026-11-04). The three rules below were run on Pest
4.7.8 on 2026-11-04: green on the clean tree, the first two red after planting an `Invoicing` class that takes a
`Booking\Models\Booking`. `laravel-architecture` covers the domain folder layout and the presets that do not fit
it.

```php
// tests/Arch/ContextsTest.php
arch('booking interior stays in booking')
    ->expect('App\Domains\Booking\Models')
    ->toOnlyBeUsedIn('App\Domains\Booking');

arch('invoicing reaches booking only through contracts and events')
    ->expect('App\Domains\Invoicing')
    ->not->toUse(['App\Domains\Booking\Models', 'App\Domains\Booking\Services', 'App\Domains\Booking\Policies']);

arch('booking does not depend on its downstreams')
    ->expect('App\Domains\Booking')
    ->not->toUse(['App\Domains\Invoicing', 'App\Domains\Notifications']);
```

One `not->toUse` per forbidden direction keeps the edge list readable next to the map. A raw `DB::table('...')`
on another context's table is invisible to `arch()`; the table check below covers it.

## Go

Two layers. The compiler enforces `internal/`: "Code in or below a directory named "internal" is importable only
by code that shares the same import path above the internal directory" (https://pkg.go.dev/cmd/go, 2026-11-04).
Edges between contexts' public packages need a test over `go list`. The test below was run on go1.27.3 on
2026-11-04: it passed on the allowed graph and failed on a planted `booking -> payments` import.

```go
// archtest/contexts_test.go — run with: go test -count=1 ./archtest/...
package archtest

import (
	"os/exec"
	"strings"
	"testing"
)

const prefix = "example.com/app/contexts/"

// allowed[from] lists the contexts from may import. Same set as docs/CONTEXT-MAP.md.
var allowed = map[string][]string{
	"availability": {},
	"booking":      {"availability"},
	"invoicing":    {"booking"},
}

func contextOf(path string) string {
	if !strings.HasPrefix(path, prefix) {
		return ""
	}
	return strings.SplitN(strings.TrimPrefix(path, prefix), "/", 2)[0]
}

func TestContextEdges(t *testing.T) {
	out, err := exec.Command("go", "list", "-f", `{{.ImportPath}} {{join .Imports " "}}`, "../...").Output()
	if err != nil {
		t.Fatal(err)
	}
	seen := 0
	for _, line := range strings.Split(strings.TrimSpace(string(out)), "\n") {
		fields := strings.Fields(line)
		from := contextOf(fields[0])
		if from == "" {
			continue
		}
		seen++
		ok, known := allowed[from]
		if !known {
			t.Errorf("context %q is not in the allowed map", from)
		}
		for _, imp := range fields[1:] {
			to := contextOf(imp)
			if to == "" || to == from {
				continue
			}
			permitted := false
			for _, a := range ok {
				permitted = permitted || a == to
			}
			if !permitted {
				t.Errorf("%s imports %s: edge %s -> %s is not in the context map", fields[0], imp, from, to)
			}
		}
	}
	if seen == 0 {
		t.Fatal("no context packages found; the prefix is wrong")
	}
}
```

`-count=1` matters: `go test` caches the result, and the cache does not see the `go list` output, so a planted
violation stays green on a cached run. Go rejects import cycles between packages at build time; the allowed map
being acyclic covers cycles at context level.

## TypeScript with dependency-cruiser

Rules live in `.dependency-cruiser.js` under `forbidden`; `from.path` groups can be referenced as `$1` in `to`
(https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md, 2026-11-04).

```js
module.exports = {
  forbidden: [
    {
      name: "no-foreign-internals",
      severity: "error",
      from: { path: "^src/contexts/([^/]+)/" },
      to: { path: "^src/contexts/[^/]+/internal/", pathNot: "^src/contexts/$1/" },
    },
    {
      name: "booking-not-to-downstreams",
      severity: "error",
      from: { path: "^src/contexts/booking/" },
      to: { path: "^src/contexts/(invoicing|notifications)/" },
    },
    {
      name: "no-context-cycles",
      severity: "error",
      from: { path: "^src/contexts/([^/]+)/" },
      to: { circular: true, via: { pathNot: "^src/contexts/$1/" } },
    },
  ],
};
```

Run `npx dependency-cruiser src` in CI. The exit code is the number of `error`-severity violations; rules default
to `warn`, so every rule here sets `severity: "error"`. This config was run on dependency-cruiser 18.7.2 on
2026-11-04: clean tree exit 0; a planted foreign-internal import and a booking-to-invoicing import each reported,
exit 2; a planted booking-invoicing-booking cycle reported by `no-context-cycles`.

## TypeScript with eslint-plugin-boundaries

Declare one element type per context in `boundaries/elements` (capturing the context name), then set
`boundaries/dependencies` with `default: "disallow"` and one allow policy per map row. Version notes from the
plugin's migration guides (checked via Context7, 2026-11-04): v6 renamed `boundaries/element-types` to
`boundaries/dependencies` (the old name stays as a deprecated alias); v7 renamed the rule's `rules` option to
`policies` and added file and module selectors. Unverified: the exact selector syntax for your installed major;
read its docs before writing the config.

## Map diff, naming and table checks

- Map diff: a small script parses the `upstream | downstream` columns of `docs/CONTEXT-MAP.md` and compares the
  pairs with the allowed edges in the arch config (the `allowed` map, the `not->toUse` lists or the forbidden
  rules). Any difference fails.
- Event names: list event classes or schema names; fail on `^{Aggregate}(Updated|Changed|Saved|Modified)$` where
  `{Aggregate}` is any aggregate root name, and on names that start with an imperative verb (`Create`, `Send`,
  `Process`).
- Tables: a map of table name to owning context; a token scan over each context's code for the other contexts'
  table names in query builders, raw SQL and model `$table` properties. Allowlist entries carry a reason and an
  owner decision.
- Glossary aliases: for each alias in `docs/GLOSSARY.md`, a whole-word, case-insensitive search over code
  identifiers, excluding locale files, the glossary and anti-corruption layer folders, returns nothing. Aliases
  include translations and abbreviations, so translated UI text is out of scope; the `glossary` skill's checker
  covers the file's format.

## Seeing it fail

For each new rule, add one violating import or query, run the check, see it fail with a message that names the
edge, then remove the violation. Record the red run in the change description.
