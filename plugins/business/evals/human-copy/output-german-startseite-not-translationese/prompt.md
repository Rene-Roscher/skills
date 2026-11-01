---
description: A German startpage draft with calqued phrases, mixed du and Sie, English title-case heading and wrong price format must come back as native German in one address form. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent rewrites copy/startseite.md from copy/fakten.md in du-form with a sentence-case heading, German price format, no buzzwords and no em dash, keeping the 30-second interval.
tags: [human-copy, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Überarbeite copy/startseite.md direkt in der Datei. Nutze nur, was copy/fakten.md bestätigt. Der Text soll klingen wie von einer deutschen B2B-Autorin geschrieben, nicht wie übersetztes Englisch.
