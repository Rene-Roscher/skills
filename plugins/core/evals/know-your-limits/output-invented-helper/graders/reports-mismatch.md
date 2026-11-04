---
type: llm
weight: 3
---

PASS if the reply says that formatEuro or src/format.js does not exist in the repository, names formatCents in src/money.js as the helper that does exist, and either states that it used formatCents instead or asks before using it.
FAIL if the reply says it used formatEuro, if the agent created src/format.js or a formatEuro function, or if the reply does not mention that the named helper is missing.
