#!/usr/bin/env bash
set -euo pipefail
mkdir -p proto/worker/v1
cat > buf.yaml <<'EOF'
version: v2
modules:
  - path: proto
EOF
cat > proto/worker/v1/result.proto <<'EOF'
syntax = "proto3";

package worker.v1;

message CheckResult {
  string service_id = 1;
  Status status = 2;
  int64 observed_at_unix_ms = 3;
  int32 legacy_code = 4;
  uint32 latency_ms = 5;
}

enum Status {
  STATUS_UNSPECIFIED = 0;
  STATUS_UP = 1;
  STATUS_DOWN = 2;
}
EOF
