# Questions per technique

## Contents

- Encryption of data
- Keys
- Passwords
- Random values and secret tokens
- Comparisons
- Self-contained tokens and signatures
- Signed and expiring links
- Webhooks, inbound and outbound
- TLS
- Uploads and downloads
- Writing the row

Answer each question from the code and the installed library's docs or source, not from its README. A "no" or "I
do not know" is a finding until it is settled. Values below were checked on 2026-11-06 against the sources in
SKILL.md; look them up again when the source is older than a year.

## Encryption of data

- Is the mode authenticated (AES-GCM, ChaCha20-Poly1305, XChaCha20-Poly1305), or is a MAC checked before
  decryption (encrypt-then-MAC)? Wrong: AES-CBC or AES-CTR alone, ECB anywhere.
- Where does the nonce or IV come from, and can it repeat under the same key? Wrong: a constant, a value derived
  from the data, a counter that resets on restart, random 96-bit nonces beyond 2^32 messages per key.
- Is associated data (the record ID, the tenant) bound in, so a ciphertext cannot be moved to another record?
- What does decryption do on a failed tag: one generic error, no partial plaintext, no distinguishable timing?
- Which attacker does it stop? Database dump without the key: yes. Someone who calls the application's decrypt
  path: no.

## Keys

- Where is the key? Wrong: in source code, in version control, in the same database or backup as the data, in a
  log line, in an error report.
- Who and what can read it (processes, operators, CI)? More than needed is a finding.
- How is it rotated: a key ID stored with each ciphertext, old keys kept for decryption only, a re-encryption
  path? What happens on suspected compromise, and how long does it take?
- Is a key used for one purpose only (encryption, signing, cookies each separate)?

## Passwords

- Function and parameters, as a minimum: Argon2id with 19 MiB memory, 2 iterations, parallelism 1; else scrypt
  with N = 2^17, r = 8, p = 1; bcrypt (legacy) with cost 10 or more and input limited to 72 bytes; PBKDF2 with
  HMAC-SHA-256 and 600,000 iterations where FIPS-140 is required.
- Are hashes upgraded on the next login when parameters rise?
- Is the comparison done by the library's verify function, not by hashing and comparing strings?
- Are login, reset and registration answers the same for known and unknown accounts, and rate limited?

## Random values and secret tokens

- Source: the platform CSPRNG (`random_bytes`, `secrets`, `crypto.randomBytes`, `crypto/rand`)? Wrong:
  `rand`, `mt_rand`, `Math.random`, `uniqid`, timestamps, UUIDs.
- At least 128 bits of entropy for anything that must not be guessed (session IDs, reset and invitation tokens,
  API keys).
- Stored as a hash where the server only needs to recognise it (API keys, reset tokens), shown once?
- Single use where the flow implies it, with an expiry, and invalidated after a password or email change?

## Comparisons

- Are secrets, MACs, tokens and signatures compared in constant time (`hash_equals`, `hmac.compare_digest`,
  `crypto.timingSafeEqual`, `subtle.ConstantTimeCompare`)? Wrong: `==`, `===`, `strcmp`, early return on the first
  differing byte.
- Are lengths normalised before a compare that throws on unequal lengths?

## Self-contained tokens and signatures

- Is the accepted algorithm pinned by the verifier, not taken from the token header? Is `none` rejected? Can an
  HMAC key be confused with a public key?
- Are expiry, not-before, issuer, audience and token type checked, with a small clock skew?
- Can a token be revoked before expiry (logout, password change, removed member)? If not, is the lifetime short
  enough for that?
- Is the signature checked before any claim is read or used?

## Signed and expiring links

- Does the signature cover the full target (path and every query parameter) and the expiry, so neither can be
  changed?
- Is the expiry checked on the server, with a lifetime that fits the asset?
- Is the link bound to a user or tenant where it should be, and does access still check permissions?
- Is the signing key separate from other keys, and can it be rotated?

## Webhooks, inbound and outbound

- Inbound: is the provider's signature verified over the raw body, in constant time, with a timestamp tolerance
  and replay protection (event ID seen before)?
- Outbound: is the payload signed with a per-endpoint secret, and does the target URL pass an egress check?

## TLS

- Do all clients verify certificates and hostnames? Search for disabled verification flags in code and config.
- Are internal connections (database, cache, queues, other services) encrypted where they leave the host?
- Is there no fallback to plain text?

## Uploads and downloads

- Are size, type (by content, not by name) and count limited before processing?
- Are files stored outside the web root or behind authorised, expiring access, never served with a type that
  executes?
- Are file names generated, not taken from the user?

## Writing the row

| Property | Asset | Attacker | Mechanism | Evidence | Not covered |
|---|---|---|---|---|---|
| A download link cannot be changed or used after expiry | invoice PDFs | anyone holding an old or edited link | HMAC-SHA-256 over path, query and expiry, constant-time compare, key from the secret store | `tests/Feature/SignedDownloadTest.php` (tamper, expiry, other account) | someone holding a valid link before it expires |
