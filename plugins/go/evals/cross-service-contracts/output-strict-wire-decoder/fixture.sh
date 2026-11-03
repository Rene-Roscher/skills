#!/usr/bin/env bash
set -euo pipefail
mkdir -p internal/consume
cat > go.mod <<'EOF'
module example.com/ingest

go 1.24.0
EOF
cat > internal/consume/decode.go <<'EOF'
package consume

import (
	"bytes"
	"encoding/json"
)

type CheckResult struct {
	ServiceID  string `json:"service_id"`
	Status     string `json:"status"`
	ObservedAt string `json:"observed_at"`
}

func Decode(raw []byte) (CheckResult, error) {
	var r CheckResult
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.DisallowUnknownFields()
	err := dec.Decode(&r)
	return r, err
}
EOF
