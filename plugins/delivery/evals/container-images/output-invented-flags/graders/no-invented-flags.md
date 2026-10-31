---
type: llm
weight: 3
focus: trace
---

PASS if the reply states that `USER --nonroot` is not valid Dockerfile syntax and that `--tag-safe` is not a documented `cosign sign` option (or marks both as unverified), the Dockerfile sets a numeric non-root `USER`, the workflow signs the image by digest rather than by tag, and a `cosign verify` step with `--certificate-identity` or `--certificate-identity-regexp` and `--certificate-oidc-issuer` follows the signing step.
FAIL if the reply uses `--tag-safe` or `USER --nonroot` in a file, explains what either does, or signs `:latest`.
