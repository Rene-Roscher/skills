# Golden fixtures across languages

## Contents
- Layout
- Producer side (Go example)
- Distribution
- Consumer tests: PHP, Go, Rust, Node
- What the fixtures must cover

## Layout

```text
contract/fixtures/
  v6/check_result.json
  v7/check_result.json
  v7/check_result.large_id.json
  v7/check_result.minimal.json
  MANIFEST.sha256
```

One file per message type and case, one directory per accepted version. `MANIFEST.sha256` lists every fixture
with its digest so consumers can tell they have the full, unmodified set.

## Producer side (Go example)

```go
var update = flag.Bool("update", false, "rewrite golden files")

func TestGoldenCheckResult(t *testing.T) {
	for name, msg := range fixtureCases() { // built from typed values, not strings
		got, err := wire.Encode(msg) // the encoder production uses
		if err != nil {
			t.Fatal(err)
		}
		path := filepath.Join("contract", "fixtures", "v7", name+".json")
		if *update {
			if err := os.WriteFile(path, got, 0o644); err != nil {
				t.Fatal(err)
			}
			continue
		}
		want, err := os.ReadFile(path)
		if err != nil {
			t.Fatal(err)
		}
		if !bytes.Equal(got, want) {
			t.Errorf("%s: encoder output changed; run with -update and review the diff", name)
		}
	}
}
```

CI never passes `-update`. A regenerated fixture shows up in review as a diff, which is where a breaking change
becomes visible.

## Distribution

Pick one and write it in the contract:

| Option | How consumers get fixtures | Pin |
|---|---|---|
| Release asset | a tarball attached to each contract tag, with its checksum | tag |
| Separate contract module or package | consumers depend on it by version | package version |
| Vendored copy | a script copies the fixture directory at a tag into the consumer repo | tag recorded in a file |

The consumer verifies `MANIFEST.sha256` after fetching.

## Consumer tests

PHP (Pest):

```php
it('decodes every v7 check_result fixture', function (string $file) {
    $result = CheckResultData::fromJson(file_get_contents($file));
    expect($result->serviceId)->toBeString()->not->toBeEmpty();
})->with(fn () => glob(base_path('tests/Contract/fixtures/v7/check_result*.json')));
```

Go:

```go
func TestDecodeProducerFixtures(t *testing.T) {
	files, _ := filepath.Glob("testdata/contract/v7/check_result*.json")
	if len(files) == 0 {
		t.Fatal("no fixtures found")
	}
	for _, f := range files {
		raw, _ := os.ReadFile(f)
		var m CheckResult
		if err := json.Unmarshal(raw, &m); err != nil {
			t.Errorf("%s: %v", f, err)
		}
	}
}
```

Rust:

```rust
#[test]
fn decodes_producer_fixtures() {
    let mut n = 0;
    for entry in std::fs::read_dir("tests/contract/v7").unwrap() {
        let path = entry.unwrap().path();
        let raw = std::fs::read_to_string(&path).unwrap();
        let _: CheckResult = serde_json::from_str(&raw).unwrap_or_else(|e| panic!("{path:?}: {e}"));
        n += 1;
    }
    assert!(n > 0, "no fixtures found");
}
```

Do not put `#[serde(deny_unknown_fields)]` on wire types.

Node:

```js
import { readdirSync, readFileSync } from 'node:fs';
import { test } from 'node:test';
import assert from 'node:assert/strict';

test('decodes producer fixtures', () => {
  const dir = 'test/contract/v7';
  const files = readdirSync(dir).filter((f) => f.endsWith('.json'));
  assert.ok(files.length > 0, 'no fixtures found');
  for (const f of files) {
    const msg = parseCheckResult(readFileSync(`${dir}/${f}`, 'utf8'));
    assert.equal(typeof msg.serviceId, 'string');
  }
});
```

Each test asserts that it found at least one fixture, so a wrong path cannot pass with zero cases.

## What the fixtures must cover

- An ID above 2^53 − 1, encoded as a string.
- A timestamp produced from a non-UTC time, normalised to UTC.
- Empty map and empty list versus absent optional field.
- Every enum value, plus one value the consumer does not know.
- The largest message the shared limit allows, and one byte over it (consumer rejects).
- One fixture per still-accepted older version.
