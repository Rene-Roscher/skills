---
type: llm
weight: 4
---

PASS if the review states all of: the checksum comes from the same origin as the binary, so it proves integrity but not authenticity; the update must verify a signature against a trust anchor shipped inside the binary (a compiled-in public key or pinned identity) before replacing anything; `os.WriteFile` over the running binary is not atomic and leaves no previous binary, so the update should write a temp file, rename atomically and keep the old binary; a health check after restart with automatic rollback is needed; fetching `latest` without a version or digest from the control plane allows downgrades or unexpected versions.
FAIL if any of these five points is missing, or if the review calls the checksum check sufficient.
