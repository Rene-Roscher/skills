# Agent switches

Load when you must turn off or verify the attribution of a specific agent, or when a cloud surface ignores
local settings. Every row was checked against the vendor's documentation or source on 2026-10-31. Vendor
behaviour changes without notice: re-read the linked page before you rely on a row.

## What each tool adds and how to switch it off

| Tool | Default trace | Switch | Source |
|---|---|---|---|
| Claude Code | a co-author trailer on commits, a credit line in PR bodies, a session link on cloud sessions | `attribution` object in settings: `commit` and `pr` empty strings, `sessionUrl` false. On v2.1.281 or later `"attribution": false` also works; older versions reject it and skip the whole file | https://code.claude.com/docs/en/settings-reference |
| Codex | Commit trailer and PR line when the workspace policy is on | Backend policy field, not `config.toml`; an AGENTS.md rule does not override an enabled policy. Where the toggle lives in the UI is not documented | https://github.com/openai/codex (`codex-rs/ext/git-attribution`) |
| Cursor (IDE) | a "made with Cursor" trailer on commits and PRs, on by default | Settings, Git and PRs, Attribution; enterprise admins can disable it for all members | https://cursor.com/docs/integrations/git |
| Cursor (CLI) | A co-author trailer added by the tooling | `attribution.attributeCommitsToAgent: false` in `~/.cursor/cli-config.json`; a `commit-msg` hook can strip it, because injection happens before hooks run | https://forum.cursor.com/t/168258 (forum thread on the auto-added trailer) |
| GitHub Copilot cloud agent | Commits authored by Copilot, a session-log link (`Agent-Logs-Url`) in the message | No documented switch. Commits are made on GitHub, so local hooks never run; edit the squash message or block in CI | https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/track-copilot-sessions |
| VS Code Copilot | A co-author trailer naming Copilot when `git.addAICoAuthor` is not `off` | Set `"git.addAICoAuthor": "off"` in user settings | https://github.com/microsoft/vscode (`extensions/git/package.json`) |
| Aider | A co-author trailer naming aider and the model, and "(aider)" appended to author and committer names | the three `--no-attribute-*` flags (trailer, author, committer; list them with `aider --help`). Aider also skips hooks by default (`--no-verify`); `--git-commit-verify` turns hooks back on | https://aider.chat/docs/config/options.html |
| claude-code-action | A prompt-level co-author trailer naming the human who mentioned `@claude`, and a credit signature in the PR body template | Pass attribution settings through the `settings` input. No documented input removes the PR signature, so the PR-body check is the guarantee | https://github.com/anthropics/claude-code-action |

Claude Code settings reach different surfaces differently. Terminal, IDE extensions and the desktop app read
`~/.claude/settings.json`. A single-repo cloud session reads the committed `.claude/settings.json`, not the
user file. A cloud thread inside a project reads only `CLAUDE.md` files. Managed settings win over every
written rule. A rule in `CLAUDE.md` or memory takes precedence over the default lines unless the line is set
in managed settings.

Unverified: whether a `CLAUDE.md` rule also suppresses the session trailer. The docs sentence covers "these
commit and PR lines" and does not say how the trailer is appended. Treat the CI range check as the guarantee.

## Where each layer stops

| Layer | Catches | Misses |
|---|---|---|
| Tool setting | The trailer and PR line at the source | Cloud surfaces that ignore local files; tools with no switch |
| Written rule (CLAUDE.md, AGENTS.md) | Claude Code lines unless managed settings set them | Codex with the workspace policy on; Cursor tooling-level injection |
| Local `commit-msg` hook | Anything committed with local `git commit` | `--no-verify`, commits through the GitHub API, fresh clones before install |
| CI range check | Every commit in the PR, author and committer identity included | The PR description and the message typed at merge time |
| PR-body check | The description, which GitHub can copy into the squash commit | Text edited at the moment of merging |

Close the last gap with the repository's squash default: "pull request title" or "title and commit details",
never "title and description".

## Public repositories

Instruction files for agents (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.cursor/`, `.cursorrules`,
`.github/copilot-instructions.md`) can expose internals. If the project wants none in the public tree, keep them
gitignored and carry the attribution switch in user settings, managed settings or a cloud setup script. Check
before a push that these print nothing:

```sh
git ls-files | grep -E -i '(^|/)(CLAUDE\.md|AGENTS\.md|GEMINI\.md|\.claude/|\.cursor/|\.cursorrules|\.aider|\.windsurfrules|\.github/copilot-instructions\.md)'
git grep -n -i -E '(generated|written|created) (by|with) (ai|claude|chatgpt|copilot|cursor|codex)|claude\.ai/code|noreply@anthropic\.com'
```

A committed `.claude/settings.json` is itself such a file; choose per repository.
