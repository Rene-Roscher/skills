# delivery

Baselines for the path from commit to running software: GitHub Actions workflows that resist supply-chain and
privilege abuse, container images that are small, reproducible and safe to run, and releases that are signed,
verified and rolled out in stages.

## Skills

| Skill | Use it when |
|---|---|
| `local-dev-stack` | setting up or changing the local Docker Compose stack, its ports, Makefile targets or dev environment |
| `github-actions-hardening` | creating, editing or reviewing `.github/workflows/*.yml`, an `action.yml` or a Dependabot config |
| `container-images` | writing or reviewing a Dockerfile, a `.dockerignore`, a base image choice or an image build and signing step |
| `release-supply-chain` | tagging, signing, publishing or rolling out a release of binaries, packages or images, including self-updating agents |

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
