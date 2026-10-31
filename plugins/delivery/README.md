# delivery

Baselines for the path from commit to running container: GitHub Actions workflows that resist supply-chain and
privilege abuse, and container images that are small, reproducible and safe to run.

## Skills

| Skill | Use it when |
|---|---|
| `github-actions-hardening` | creating, editing or reviewing `.github/workflows/*.yml`, an `action.yml` or a Dependabot config |
| `container-images` | writing or reviewing a Dockerfile, a `.dockerignore`, a base image choice or an image build and signing step |

Claude Code loads a skill when the task matches its description, including in a repository that has no workflow
or Dockerfile yet. You can also call one directly, for example `/delivery:container-images`.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install delivery@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it.

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off). Choices such as Dependabot versus Renovate live in the example profile under
`templates/project-overlay/profiles/` at the repository root.

See [CHANGELOG.md](CHANGELOG.md) for changes.
