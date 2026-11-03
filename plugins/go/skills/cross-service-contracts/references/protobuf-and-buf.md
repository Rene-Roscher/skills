# Protobuf and buf

## Contents
- Message discipline
- Field-number pin test
- buf configuration
- CI step

Check flags against the installed buf version (`buf --version`) before copying.

## Message discipline

```proto
syntax = "proto3";

message CheckResult {
  reserved 4, 9 to 11;
  reserved "latency_ms_legacy";

  string service_id = 1;
  Status status = 2;
  int64 observed_at_unix_ms = 3;
  uint32 schema_version = 5;
}

enum Status {
  STATUS_UNSPECIFIED = 0;
  STATUS_UP = 1;
  STATUS_DOWN = 2;
}
```

- Deleted fields go into `reserved` by number and by name in the same change.
- Reserve a range for future internal use if the team wants one, and pin it in the test.
- `*_UNSPECIFIED = 0` is never a meaningful state. Receivers count it and unknown values, then drop or quarantine.
- Control-plane-only states are not in the wire enum.

## Field-number pin test

Go, using the generated descriptors:

```go
func TestCheckResultFieldNumbers(t *testing.T) {
	want := map[string]protoreflect.FieldNumber{
		"service_id": 1, "status": 2, "observed_at_unix_ms": 3, "schema_version": 5,
	}
	fields := (&wirepb.CheckResult{}).ProtoReflect().Descriptor().Fields()
	if fields.Len() != len(want) {
		t.Fatalf("field count %d, want %d: update this test and the contract together", fields.Len(), len(want))
	}
	for name, num := range want {
		f := fields.ByName(protoreflect.Name(name))
		if f == nil || f.Number() != num {
			t.Errorf("%s: number changed or field missing", name)
		}
	}
	reserved := (&wirepb.CheckResult{}).ProtoReflect().Descriptor().ReservedRanges()
	if reserved.Len() == 0 {
		t.Error("reserved ranges disappeared")
	}
}
```

Consumers in other languages pin the same table against their generated code.

## buf configuration

```yaml
version: v2
modules:
  - path: proto
lint:
  use:
    - STANDARD
breaking:
  use:
    - WIRE_JSON
```

`WIRE_JSON` when any consumer reads protobuf JSON; the default `FILE` when other repos import the generated code.

## CI step

```yaml
- uses: actions/checkout@[sha] # vN
  with:
    fetch-depth: 0
- run: buf lint
- run: buf breaking --against '.git#branch=main,subdir=proto'
```

With a shallow clone, use the remote form instead: `buf breaking --against 'https://github.com/[org]/[repo].git'`.
The job is a required status check and has no `continue-on-error`. On the main branch itself, compare against the
previous release tag (`.git#tag=[last-tag],subdir=proto`) so a direct push cannot skip the check.
