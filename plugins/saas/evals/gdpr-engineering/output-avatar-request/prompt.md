---
description: "A request for third-party avatars must come back with a self-hosted alternative and the reason."
expected_outcome: "The reply proposes initials or uploaded avatars you host, explains that every image request sends the viewer's IP address to a third party, adds no avatar-service URL or email hash to the code, and names a guard such as a CSP img-src rule."
tags: [gdpr-engineering, output]
runs: 3
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Add Gravatar avatars to the member list in src/views/members.html of our project tool.
