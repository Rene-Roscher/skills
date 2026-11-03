---
description: A German error message and empty state with apology filler, mixed du and Sie, nominal style, an anglicism the glossary forbids and a vague button must come back as native German UI text. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent rewrites copy/ui-texte.md from copy/fakten.md. The error says what happened (not saved, no connection), that the draft is kept and that saving retries every 30 seconds, in du, without Ups, leider, bitte or an exclamation mark. The empty state says what appears there and offers the one button Aufgabe anlegen. No Task, no nominal style, no Sie.
tags: [human-copy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Überarbeite die Fehlermeldung und den Leerzustand in copy/ui-texte.md direkt in der Datei. Grundlage ist nur copy/fakten.md. Die Texte sollen klingen, als hätte sie eine deutsche UX-Autorin geschrieben.
