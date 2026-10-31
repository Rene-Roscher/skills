---
description: Should load mcp-server-design. Train split. Run with --ablation none --threshold 0.5.
tags: [mcp-server-design, trigger]
runs: 3
allowed_tools: [Read, Glob, Grep, Skill]
---

Our MCP tool created the same record twice after the client retried. How do we stop that?
