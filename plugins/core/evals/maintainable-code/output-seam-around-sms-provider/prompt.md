---
description: New reminder code that texts a customer must receive its sender through a small interface and be tested with a fake, not by patching the network. Needs --scaffold and --allow-tools Bash Edit Write.
expected_outcome: The agent writes src/reminders.py with send_reminder taking an injected sender, a unit test using a hand-written fake sender, and runs the test without network access and without patching globals.
tags: [maintainable-code, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Add send_reminder(booking) in src/reminders.py that texts the customer the way src/notify.py does, plus a unit test in tests/test_reminders.py. Run the test.
