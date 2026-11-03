---
description: The owner corrects a term in a drafted booking mail for the second time. The agent must apply it and offer to record the correction in docs/voice/corrections.jsonl, and because the rule recurs, propose promoting it to the glossary. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: copy/buchung.md no longer says Slot. The reply shows the corrections.jsonl line it proposes (date, surface, lang, before, after, reason, rule) or says it recorded it, notes that the same rule is already in corrections.jsonl, and proposes a glossary row that puts Slot in the avoid column for Termin.
tags: [human-copy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Die Buchungsmail in copy/buchung.md hast du gestern geschrieben. Ich habe sie korrigiert: Aus „dein Slot am 12. November“ wird „dein Termin am 12. November“. Slot sagen wir nicht, bei uns heißt das immer Termin. Übernimm das in der Datei.
