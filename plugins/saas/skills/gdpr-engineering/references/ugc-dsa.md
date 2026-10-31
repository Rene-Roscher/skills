# User-generated content and the DSA

Review-ready draft, not legal advice. Scope: EU. Source: Regulation (EU) 2022/2065,
https://eur-lex.europa.eu/eli/reg/2022/2065/oj (verified 2026-10).

## Who is covered

Storing content that users provide (comments, boards, public profiles, uploaded files shown to others) makes you
a hosting provider. Art. 14 applies to all intermediary services and Art. 16 and 17 to all hosting services.
The exemption for micro and small enterprises in Art. 19 covers only the section on online platforms (with an
exception for Art. 24(3)); it does not remove Art. 14, 16 or 17. Content visible only after login is still hosted
content.

## Duties to build

| Article | Duty | What to build |
|---|---|---|
| 14 | Terms describe content restrictions and moderation, including automated tools | numbered moderation clauses that decisions can cite |
| 16 | A notice mechanism for illegal content | an endpoint or form that captures the reason, the exact location (URL), the notifier's name and email, and a good-faith statement; confirmation of receipt; a decision with redress information |
| 16(6) | Timely, diligent, non-arbitrary and objective handling; disclose automated means | moderation queue with timestamps, `automated` flag on decisions |
| 17 | A statement of reasons for each restriction: removal, blocking, demotion, payment limits, suspension | a record with the restriction type and scope, facts, whether a notice triggered it, automated means, legal or terms ground, redress options |

## Privacy side of user content

- You are the controller for content posted on your own surfaces: privacy notice and VVT, not the AVV.
- Showing a person's name publicly is not covered by the service contract. Use consent, or a display name the
  person chose.
- Moderation records contain personal data of notifiers and posters. Give them a retention period and an entry
  in the inventory.
