#!/usr/bin/env bash
set -euo pipefail
mkdir -p internal/update
cat > go.mod <<'EOF'
module example.com/agent

go 1.24.0
EOF
cat > internal/update/update.go <<'EOF'
package update

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"io"
	"net/http"
	"os"
	"strings"
)

const base = "https://downloads.example.com/agent/latest/"

func Apply(self string) error {
	bin, err := get(base + "agent_linux_amd64")
	if err != nil {
		return err
	}
	sum, err := get(base + "agent_linux_amd64.sha256")
	if err != nil {
		return err
	}
	h := sha256.Sum256(bin)
	if hex.EncodeToString(h[:]) != strings.TrimSpace(string(sum)) {
		return errors.New("checksum mismatch")
	}
	return os.WriteFile(self, bin, 0o755)
}

func get(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}
EOF
