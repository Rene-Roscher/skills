---
description: "Should trigger design-quality: a content edit on a docs site renders as a page. Run with --ablation none."
tags: [design-quality, trigger]
runs: 3
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
---

Add a section about recurring bookings to content/guides/calendar.md in our help site, with a screenshot block,
and make sure the page still looks right afterwards.
