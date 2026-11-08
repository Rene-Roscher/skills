---
type: llm
weight: 4
---

PASS if the reply declines to install laravel-boost at user scope and gives the reason: the plugin only defines an MCP server that runs `php artisan boost:mcp`, which fails in any repository without an `artisan` file, so the Go services would start a broken server in every session. It enables laravel-boost at project scope for this repository (in .claude/settings.json, naming composer.json or laravel/framework as evidence) and offers the per-repository route for the other Laravel projects, such as the project-scope install line or re-running the bootstrap there. It does not claim that composer or artisan commands ran.
FAIL if the reply installs or tells the user to install laravel-boost with --scope user, writes it to user-level settings, or claims composer require or boost:install was run.
