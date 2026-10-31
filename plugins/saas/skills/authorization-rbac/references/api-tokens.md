# API tokens and integration connections

Load when designing or changing API tokens, agent or integration connections, service accounts, rotation, or what
happens to a token when its creator is demoted or deactivated.

## Ownership and scope

- A token belongs to the tenant, records its creator, and carries an explicit ability subset chosen at mint time.
- The subset is capped by the creator's effective permissions at mint time (see `grant-paths.md` in this skill).
- A token is bound to exactly one tenant. The tenant is part of the token record, never a request parameter.

## Storage

- Store a hash of the secret, never the plaintext. Show the plaintext once, at creation.
- A recognisable prefix per credential class lets secret scanners and support recognise a leaked token. The prefix
  names the class, not the tenant.
- Keep a public ID for each token, used in the UI, in audit entries and in error messages.

## Checks on every path

- One ability check runs per route for token requests.
- Every shortcut that answers before the controller calls the same check: idempotent replay of a stored response,
  response caches, batch endpoints that fan out to several actions.
- A token request also passes the tenant and membership checks: a token whose creator was removed is handled as the
  demotion ADR says.

## Lifecycle

- Expiry: tokens have an expiry date or a documented reason not to.
- Rotation: issue the new token, accept both during a grace window, then revoke the old one. The new token's subset
  is at most the old one's.
- Revocation: immediate. Cached token lookups are invalidated on revoke.
- Deactivation of the creator: runs through the member deactivation choke point, which revokes or flags the tokens
  the member minted.

## Demotion ADR

Pick one model per token class and write it down:

| Model | Effective abilities | Creator demoted below the subset |
|---|---|---|
| Tenant service account | the frozen subset | flag for an owner decision, or revoke |
| Delegated credential | subset ∩ creator's current permissions | narrows automatically; notify the owner |

Either way, a demotion of the creator below the token's subset triggers revocation or a flag. A test demotes the
creator and asserts the ADR's outcome.

## Tests

- A token without the ability gets 403 on the route.
- An idempotent replay after the ability was removed gets 403.
- The token table holds only hashes (assert no column equals the plaintext).
- Deactivating the creator revokes or flags the token, as the ADR says.
- Minting above the minter's permissions is rejected and nothing is written.
