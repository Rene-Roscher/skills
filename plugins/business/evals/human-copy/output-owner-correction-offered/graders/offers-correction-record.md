---
type: llm
weight: 4
---

PASS if the final reply does all of these: (1) confirms that copy/buchung.md now says Termin instead of Slot; (2) offers to record the owner's correction in docs/voice/corrections.jsonl by showing the proposed line, or states that it recorded it and shows the line, with at least before, after, reason, surface or lang, and a rule such as "Termin statt Slot"; (3) notes that the same rule already appears in corrections.jsonl, or that the owner said "immer", and therefore proposes promoting it to a glossary row that lists Slot as a variant to avoid for Termin (or says it added that row).

FAIL if the reply only says the change was made, or says "noted" or "I will remember" without a correction record; if it records customer data beyond the example name in the draft; if it creates approved examples in docs/voice/examples/; or if it changes other wording in the mail without saying so.
