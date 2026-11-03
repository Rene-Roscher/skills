---
type: llm
weight: 3
focus: trace
---

Judge the final `.github/workflows/release.yml` as written in the trace, and the reply.

PASS if: the signing job has `id-token: write`; the verify step pins the identity exactly or with a regexp anchored to the release workflow and `refs/tags/v`; `SHA256SUMS` is generated after the SBOMs and covers every published asset; syft is installed at an exact version with a checksum check (or through a SHA-pinned action with an explicit version); the reply proposes release notes that begin with the verification commands.
FAIL if verification is missing, the identity regexp is unanchored, a download is still piped into a shell, or the checksum file is signed before all assets exist.
