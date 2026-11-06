---
name: security-assurance
description: "Proves each security property a product relies on or claims instead of trusting labels: asset, attacker and mechanism in its own words, then checks how each technique is used (AEAD and nonces, keys and rotation, password hashing, CSPRNG tokens, constant-time compares, token algorithms, TLS verification) and backs it with attack tests that must fail. Use when adding auth, tokens, crypto, signed links or a security claim. Not for tenant scoping."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Security assurance

This skill turns "it is secure" into a set of properties, each with an attacker, a mechanism and evidence. The
agent builds its own model of the attack, checks how the chosen technique is actually used at the installed
version, and writes a test that performs the attack and must fail. It never invents a cryptographic primitive and
never tries to break a standard one; it checks that the standard one is used correctly. The failure it prevents: a
property believed because a README, a vendor page or a library tagline says "encrypted" or "secure", while the
code uses an unauthenticated cipher mode, a reused nonce, a string compare on a signature or a token that never
expires.

## Applies when / does not apply

- Applies: authentication, sessions, password storage, reset and invitation tokens, API keys, signed or expiring
  links, webhook signatures, encryption of stored data, key handling, JWT or other self-contained tokens, TLS
  settings of clients and servers, file upload and download paths, any README, spec or sales text that claims a
  security property, and the question "is this secure?".
- Does not apply: scoping data per tenant (`tenant-isolation` in the saas plugin), role and permission design
  (`authorization-rbac`), CI and supply-chain hardening (`github-actions-hardening`, `release-supply-chain`),
  checking non-security claims in docs (`evidence-before-claims`), and breaking or reviewing a primitive itself.

## Rules

- [invariant] No security property without its row: every property the product relies on or claims is written as
  property, asset, attacker (who, with what access), mechanism, evidence, and what is not covered. A label is not
  a row: "secure", "fully encrypted", "military-grade", "bank-level", a vendor's "enterprise-grade security" or a
  library's "safe by default" proves nothing until it is broken down. Why: a label survives review because it
  sounds authoritative, and nobody can test it. Test: a README says "end-to-end encrypted, fully secure" while the
  code encrypts with AES-CBC and no MAC; the agent does not repeat the claim, writes the row it can prove, and
  names the gap (eval `adversarial-readme-claim-vs-code`). Source: OWASP ASVS 5.0.0, 11.1.2, "Verify that a
  cryptographic inventory is performed, maintained, regularly updated, and includes all cryptographic keys,
  algorithms, and certificates used by the application." (https://asvs.owasp.org/, verified 2026-11-06).
- [invariant] Model the attack yourself, as deep as the asset is worth. Before accepting a mechanism, write in a
  few lines what the asset is, who attacks it with which access (anonymous network client, signed-in user of
  another account, holder of a leaked link, someone with read access to the database or the backups, a
  compromised dependency) and what success means for them. A public read-only page gets one line; credentials,
  payments, personal data and admin paths get the full table and attack tests. Why: a mechanism is only right
  relative to an attacker; "encrypted at rest" by the cloud provider does nothing against an attacker who reads
  through the application. Test: asked whether stored API keys are safe because "the disk is encrypted", the
  reply names the attacker the disk encryption does not stop. Source: OWASP ASVS 5.0.0, "Level evaluation": risk
  reduction weighed against effort, and higher-level requirements taken earlier "based on their own specific risk
  considerations" (https://asvs.owasp.org/, verified 2026-11-06).
- [invariant] Every property has an attack test that performs the attack and must fail, and that test was seen
  passing only because of the mechanism: disable the check once and watch the test go red. Attacks to cover where
  they apply: no credentials, another account's identifier, a tampered payload or signature, a replayed token, an
  expired link or token, a swapped or `none` algorithm, an oversized or malformed input. Why: a security test
  that passes with the check removed tests nothing. Test: removing the signature comparison from a signed-link
  handler turns the tamper test red. Source: OWASP ASVS 5.0.0, 9.1.1, "Verify that self-contained tokens are
  validated using their digital signature or MAC to protect against tampering before accepting the token's
  contents." (https://asvs.owasp.org/, verified 2026-11-06); consistent with `test-strategy` (seen failing).
- [invariant] Check how each technique is used, not only which one was chosen, with the questions in
  `references/technique-questions.md`: encryption is authenticated (AES-GCM, ChaCha20-Poly1305, or an approved
  cipher with a MAC); a nonce is never reused with the same key; keys live outside source code and version
  control, apart from the data, with a rotation path; passwords use a password hashing function with current
  parameters; non-guessable values come from a CSPRNG with at least 128 bits of entropy; secret comparisons are
  constant-time; token verification pins the allowed algorithms and checks expiry, issuer and audience; TLS
  clients verify certificates. Why: the failures live in the use: GCM with a repeated nonce, a correct HMAC
  compared with `==`, a strong hash with a cost from ten years ago. Test: code that encrypts with AES-GCM under a
  constant nonce is reported as broken although "AES-256-GCM" appears in the docs. Source: NIST SP 800-38D,
  section 8, "The probability that the authenticated encryption function ever will be invoked with the same IV
  and the same key on two (or more) distinct sets of input data shall be no greater than 2-32."
  (https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf); OWASP ASVS 5.0.0, 11.3.3,
  11.3.4, 11.5.1, 11.2.4, 9.1.2, 12.3.2 (https://asvs.owasp.org/); RFC 8725, section 3.1
  (https://www.rfc-editor.org/rfc/rfc8725.html); all verified 2026-11-06.
- [invariant] Never build a primitive or a protocol of your own: no hand-made MAC such as `hash(key + message)`,
  no own token format compared as a string, no own key exchange, no "light" encryption by XOR or encoding. Use the
  framework's mechanism or a maintained library's high-level API. Why: home-made constructions fail in ways no
  test written by the same person finds (length extension, timing, malleability). Test: asked to "quickly sign"
  a value, the change uses an HMAC from the standard library or the framework's signer, not string hashing.
  Source: OWASP Cryptographic Storage Cheat Sheet, "Custom Algorithms": "Don't do this."
  (https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html, verified 2026-11-06).
- [invariant] A library's or vendor's security claim is verified in its documentation or source for the installed
  version before it becomes evidence: which mode `encrypt()` uses, whether it authenticates, the default work
  factor, whether the HTTP client verifies TLS, whether the JWT library accepts `none` or lets the token header
  choose the algorithm. Cite the doc URL or `path:line`. Why: taglines describe intent, defaults differ between
  versions, and a wrapper can weaken what the underlying primitive guarantees. Test: asked "is the framework's
  encrypter authenticated?", the reply cites the cipher and the MAC check from the installed source. Source:
  consistent with `evidence-before-claims` (installed source over docs over memory).
- [invariant] Every row says what it does not cover, and a public or customer-facing claim says no more than the
  rows prove. Name the attacker the mechanism does not stop (someone with the full link, a compromised browser, an
  operator with key access, a future key compromise without forward secrecy). Why: a property without its limits
  is read as a promise. Test: `scripts/check_assurance.py` fails on an empty or "none" in the not-covered column.
  Source: none; design judgment, consistent with `evidence-before-claims` (security claims in public docs).
- [default] Keep the table in `docs/SECURITY-ASSURANCE.md` under `## Security assurance`, one row per property,
  and run `scripts/check_assurance.py` before handover and before a release. Trade-off: one more document that
  has to move with the code. Deviate only with an ADR that names this trade-off. Source: none; design judgment.
- [default] Prefer the framework's built-in mechanism (password hasher, encrypter, signed URLs, session handling)
  over a library, and a library over own code, and check its defaults anyway. Trade-off: the framework's choice
  of algorithm and format. Deviate only with an ADR that names this trade-off. Source: OWASP Cryptographic Storage
  Cheat Sheet, "use a maintained library implementing an established hybrid encryption scheme"
  (https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html, verified 2026-11-06).

## Procedure

### Fast path

One mechanism, low-value asset: write its row, answer its questions from the reference, add one attack test,
see it fail with the check disabled, run the checker.

1. Inventory: find every security mechanism the change touches or the docs claim. Search for encryption,
   hashing, signing, random, token, password, `verify`, TLS options and every "secure" or "encrypted" in README,
   specs and marketing copy.
2. Threat model: per asset, the attacker, their access and what success means, as deep as the asset is worth.
3. Use: for each mechanism, go through its questions in `references/technique-questions.md`. Read the installed
   library's docs or source for the defaults; note the version.
4. Table: one row per property in `docs/SECURITY-ASSURANCE.md`, with evidence and what is not covered.
5. Attack tests: one per property and attack that applies; disable the check once, see red, restore, see green.
6. Configuration: the settings the evidence depends on (TLS verification, cookie flags, key source, algorithm
   allowlist) are checked in the deployed configuration, not only in code defaults.
7. Claims: every security sentence in README, specs and customer-facing text matches a row and says no more.
8. Check: `python3 scripts/check_assurance.py [repo]`, exit 0.
9. Report: the rows, the attack tests with their red and green runs, what is not covered, open risks for the
   owner.

## Traps

- AES-CBC or AES-CTR without a MAC is malleable: an attacker flips plaintext bits through the ciphertext, and CBC
  with padding errors can become a padding oracle.
- A random 96-bit GCM nonce is safe only up to a limited number of messages per key; NIST caps random-IV
  constructions at 2^32 invocations per key. Long-lived keys with high volume need a counter or rotation.
- `uniqid()`, `Math.random()`, `mt_rand()`, timestamps and UUIDs are not secret tokens; UUIDs do not carry 128 bits
  of entropy.
- An HMAC or token compared with `==` or `===` leaks timing; use the language's constant-time compare.
- A JWT library that takes the algorithm from the token header accepts `none` or verifies an HMAC with the
  public RSA key as secret.
- bcrypt reads only the first 72 bytes of input; a longer passphrase or a pre-hash without care silently
  truncates.
- A signed URL that signs the path but not the expiry or the query parameters lets the holder extend it or change
  the target.
- `verify=False`, `CURLOPT_SSL_VERIFYPEER => false` or `rejectUnauthorized: false` added for local development
  ships to production with the same config.
- Base64, hex and compression are encodings, not encryption.
- "Encrypted at rest" by the provider does not protect against an attacker who reads through the application or
  its backups with the key.

## Done when

- Every property the change relies on or the docs claim has a row: property, asset, attacker, mechanism,
  evidence, not covered.
- Each mechanism was checked against its questions, with the installed library's docs or source cited.
- Each row's attack test exists, was seen red with the check disabled and is green now.
- Security claims in README, specs and customer-facing text say no more than the rows.
- `check_assurance.py` exits 0.

## References

- [references/technique-questions.md](references/technique-questions.md): load at step 3; the questions per
  technique (encryption, keys, passwords, random values, comparisons, tokens and signatures, signed links, TLS,
  webhooks, uploads) with what a wrong answer looks like.

## Sources

- https://asvs.owasp.org/: OWASP ASVS 5.0.0 (published 30 May 2025), requirements 9.1.1, 9.1.2, 11.1.2, 11.2.4,
  11.3.3, 11.3.4, 11.4.2, 11.5.1, 12.3.2 and the level evaluation; verified 2026-11-06.
- https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf: NIST SP 800-38D, section 8
  (uniqueness requirement on IVs and keys) and section 8.3 (2^32 invocations for random IVs); verified 2026-11-06.
- https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html: Argon2id, scrypt, bcrypt and
  PBKDF2 parameters, bcrypt's 72-byte limit; verified 2026-11-06.
- https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html: authenticated modes,
  custom algorithms, key storage and rotation; verified 2026-11-06.
- https://www.rfc-editor.org/rfc/rfc8725.html: JSON Web Token Best Current Practices, sections 3.1 (algorithm
  verification), 3.8 (issuer and subject), 3.11 (explicit typing); verified 2026-11-06.
