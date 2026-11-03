---
type: regex
pattern: 'uint32\s+latency_ms\s*=\s*5\s*;'
weight: 2
target:
  source: file
  path: proto/worker/v1/result.proto
---
