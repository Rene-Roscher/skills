---
type: llm
weight: 5
---

PASS if the final code signs the link with an HMAC (hmac module with SHA-256 or stronger) over at least the invoice identifier and an expiry time, reads the key from the environment or a secret file rather than a literal in the source, checks the expiry on the server, and compares signatures with hmac.compare_digest (or an equivalent constant-time function). The tests include a tampered link (changed id, expiry or signature), an expired link and a link without a signature, each rejected, and the reply reports a test run where they pass. Bonus, not required: the reply says it disabled the check once and saw the tests fail.
FAIL if the signature is compared with == or !=, if the link never expires, if the key is a literal in the source, if the token is a random ID stored without expiry, if the link is a plain unsigned URL, or if there is no test for tampering or expiry.
