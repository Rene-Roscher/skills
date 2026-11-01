#!/usr/bin/env bash
set -euo pipefail
mkdir -p data
{ printf '['
  for i in $(seq 1 120); do
    if [ $((i % 5)) -eq 0 ]; then s=refunded; else s=paid; fi
    if [ "$i" -gt 1 ]; then printf ','; fi
    printf '{"id":%d,"status":"%s","amount_cents":%d}' "$i" "$s" $((i * 100))
  done
  printf ']\n'; } > data/orders.json
