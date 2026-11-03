#!/usr/bin/env bash
set -euo pipefail
mkdir -p internal/config cmd/worker
cat > go.mod <<'EOF'
module example.com/worker

go 1.24.0
EOF
cat > internal/config/config.go <<'EOF'
package config

import (
	"os"
	"strconv"
	"time"
)

type Config struct {
	ControlURL    string
	Workers       int
	CheckInterval time.Duration
}

func getEnvInt(key string, def int) int {
	v, err := strconv.Atoi(os.Getenv(key))
	if err != nil {
		return def
	}
	return v
}

func getEnvDuration(key string, def time.Duration) time.Duration {
	v, err := time.ParseDuration(os.Getenv(key))
	if err != nil {
		return def
	}
	return v
}

func Load() Config {
	return Config{
		ControlURL:    os.Getenv("CONTROL_URL"),
		Workers:       getEnvInt("WORKERS", 8),
		CheckInterval: getEnvDuration("CHECK_INTERVAL", 30*time.Second),
	}
}
EOF
cat > cmd/worker/main.go <<'EOF'
package main

import (
	"fmt"
	"time"

	"example.com/worker/internal/config"
)

func main() {
	cfg := config.Load()
	t := time.NewTicker(cfg.CheckInterval)
	defer t.Stop()
	fmt.Println("workers:", cfg.Workers)
}
EOF
