# go

Baselines for production Go services and for the contracts between services written in different languages:
how a Go process starts, stops, bounds its work and proves it in CI, and how a message shared between repos is
written down, changed and tested on both sides.

## Skills

| Skill | Use it when |
|---|---|
| `go-service-baseline` | starting, reviewing or hardening a Go service, worker or daemon, its config, shutdown, metrics or CI gates |
| `cross-service-contracts` | adding or changing a protobuf message, a JSON event on a broker, a worker endpoint or an encrypted token that another repo reads |

Claude Code loads a skill when the task matches its description. `go-service-baseline` also loads when you work
with `go.mod` or `.go` files. You can call one directly, for example `/go:cross-service-contracts`.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install go@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it. The boundary decisions these
skills refer to (`service-boundaries`) live in the `saas` plugin; release signing and rollout
(`release-supply-chain`) in `delivery`.

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off).

See [CHANGELOG.md](CHANGELOG.md) for changes.
