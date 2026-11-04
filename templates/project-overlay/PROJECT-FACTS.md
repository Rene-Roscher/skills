# Project facts

Copy this file to `docs/PROJECT-FACTS.md` in your project and replace every `[placeholder]`. Agents read it
instead of guessing. Keep it to facts: names, commands, limits. Rules and their reasons live in the skills.
Delete sections that don't apply.

## Stack and versions

| Component | Version source |
|---|---|
| Runtime (for example PHP, Node, Go) | [file that pins it, for example composer.json config.platform] |
| Framework | [lockfile] |
| Production database engine | [engine and major version] |
| Cache, queue and session store | [engine; one instance or one per durability tier] |

## Scaffold

One row per component the approved architecture names, and nothing else. `project-scaffold` fills it before
the first installer command; its `check_scaffold.py` compares the repository against it.

| Component | Directory | Starter | Version | Flags |
|---|---|---|---|---|
| [for example App] | [app, or . for the root] | [for example Laravel Vue starter kit] | [installer and framework version, pinned] | [every choice as a flag] |

## Commands

| Purpose | Command |
|---|---|
| Start the local stack | [command] |
| Run the tests on the production database engine | [command] |
| Run the fast test lane, if one exists | [command] |
| Lint and format changed files | [command] |
| Build the production bundle | [command] |
| Run a headless browser check | [command] |

Tests run in [container or host]. Reason, if it matters: [for example "the host has a different PHP minor
version"].

## Ports and URLs (local only)

| Service | URL or port |
|---|---|
| App | [http://localhost:port] |
| Public site | [http://localhost:port] |
| Mail catcher | [http://localhost:port] |

## Queues

| Queue | Carries | Never carries |
|---|---|---|
| [name] | [for example jobs that notify a person now] | [for example bulk mail] |
| [name] | [ ] | [ ] |

## Providers

| Purpose | Provider | Sandbox or test mode |
|---|---|---|
| Payments | [provider] | [how to reach the test mode] |
| Transactional mail | [primary, failover] | [ ] |
| SMS or voice | [provider] | [ ] |
| Error tracking | [tool, region] | [ ] |
| Hosting | [provider, region] | [ ] |

Local development sends real messages through: [none, or the list]. Treat those as actions that leave the
machine.

## Approval list

Actions that need the owner's explicit approval in this project, beyond the defaults in `core:safe-actions`:

- [for example: any write to the production database replica]
- [for example: deploys outside the release window]

Actions that are fine without asking here:

- [for example: restarting local containers]

## Tracker and branches

- Issues live in: [tracker and project]
- Status names: [for example Todo, In progress, Review, Done] and who may set Done: [role]
- Branch policy: [trunk-based commits to main, or pull requests from feature branches]
- Commit format: [for example Conventional Commits, trailer that links the issue]

## Plans and decisions

- Plans: [docs/plans/YYYY-MM-DD-slug.md]
- Architecture decision records: [docs/adr/NNNN-slug.md]
- Profile in use: [templates/project-overlay/profiles/example-laravel-saas.md, or your own]
