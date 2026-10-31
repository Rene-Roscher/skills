---
description: A tools/list dump with a tenant parameter, a catch-all action tool and a mail tool marked read-only must be reported. Needs --scaffold and --allow-tools Bash Write.
expected_outcome: The agent reads tools.json and reports the tenant parameter, the catch-all action tool and the wrong read-only hint on the mail-sending tool, and does not call the server design fine.
tags: [mcp-server-design, output]
runs: 3
max_turns: 16
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Review the MCP tools in tools.json. Is it ready to ship?
