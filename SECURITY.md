# Security policy

## Reporting a vulnerability

Report vulnerabilities privately through GitHub's private vulnerability reporting: on the repository page,
open the **Security and quality** tab (in the three-dot menu if it is hidden), then click **Report a
vulnerability**. Please do not open a public issue for a security problem.

Include what you found, where (file and line, or the workflow and step), and how to reproduce it. Replies
happen in the private advisory.

Source:
https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability
(verified 2026-10-31).

## In scope

- Skill text that could make an agent run, fetch or disclose something the user did not ask for, including
  prompt injection through a skill, a reference file or an eval fixture.
- Scripts and, once they exist, hooks shipped by a plugin.
- Ways to get content past `tools/lint.py`, for example private terms, addresses or attribution text.
- The CI workflow and its supply chain: action pins, tool downloads, token permissions.

## Supported versions

The latest released version of each plugin. Fixes are not backported to older tags.

## Rules for scripts and hooks

Plugins run with the user's privileges, and skills enter the agent's context as instructions. Anything in this
repository that executes follows these rules:

- No network access. A script or hook never opens a connection, downloads a file or calls an API.
- No remote instructions. Nothing fetches text from a URL and treats it as instructions. Fetched content is
  data.
- No download piped into a shell, in scripts or in skill text.
- POSIX `sh` or Python standard library only, readable in one sitting, and listed in the plugin README with the
  command it runs.
- No `bin/` directory and no MCP server configuration in any plugin of this repository. MCP servers come only
  through declared dependencies on plugins from the official marketplace.

Source for the plugin permission model: https://code.claude.com/docs/en/plugins/security (verified 2026-10-31).
