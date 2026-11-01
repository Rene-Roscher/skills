#!/usr/bin/env bash
set -euo pipefail
mkdir -p src
{ for i in $(seq 1 2400); do printf 'def helper_%d(x):\n    return x + %d\n\n' "$i" "$i"; done
  printf 'RATES = {"DE": 0.19, "FR": 0.2}\n\ndef compute_tax_rate(region):\n    return RATES.get(region, 0.0)\n'; } > src/big.py
