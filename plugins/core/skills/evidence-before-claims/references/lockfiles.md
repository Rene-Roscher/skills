# Lockfiles and runtime pins

Load when you need the installed version or the production runtime pin.

## Range versus resolved version

A manifest holds a range. `^12.0` allows any 12.x release from 12.0 on, so it does not say which one is
installed. The lockfile holds the resolved version. Read the lockfile, and if there is none, say so: the
installed version is then unknown until someone installs or the environment reports it.

## Where the resolved version is

| Ecosystem | Manifest | Lockfile | Command that prints the resolved version |
|---|---|---|---|
| PHP | `composer.json` | `composer.lock` | `composer show [package]` |
| Node, npm | `package.json` | `package-lock.json` | `npm ls [package]` |
| Node, pnpm | `package.json` | `pnpm-lock.yaml` | `pnpm ls [package]` |
| Node, Yarn | `package.json` | `yarn.lock` | `yarn why [package]` |
| Node, Bun | `package.json` | `bun.lock` | read the lockfile entry |
| Go | `go.mod` | `go.sum` (versions are in `go.mod`) | `go list -m [module]` |
| Rust | `Cargo.toml` | `Cargo.lock` | `cargo tree -i [crate]` |
| Python, uv | `pyproject.toml` | `uv.lock` | `uv tree` or `uv pip show [package]` |
| Python, Poetry | `pyproject.toml` | `poetry.lock` | read the lockfile entry |
| Ruby | `Gemfile` | `Gemfile.lock` | read the lockfile entry |
| Terraform | `required_providers` blocks | `.terraform.lock.hcl` | read the lockfile entry |

The commands need the dependencies installed. Reading the lockfile works without them.

## Runtime pins

Read the runtime version that production uses, not the one on the host:

- Container images: the `FROM` tag of the production Dockerfile, or the image digest the deploy uses.
- Toolchain files: `.tool-versions`, `mise.toml`, `.nvmrc`, `.node-version`, `.python-version`,
  `rust-toolchain.toml`, the `go` and `toolchain` lines in `go.mod`.
- Package manager platform settings, such as `config.platform.php` in `composer.json` or `engines` in
  `package.json`. These say what the resolver assumed, not what runs.
- CI images and the setup steps in workflow files.

If two places name different versions, that is drift. Report both and say which one production uses.

## Why the minor matters

A runtime minor can change results without any code change. PHP 8.4 rewrote `round()`: its UPGRADING notes say
rounding 0.49999999999999994 to an integer used to return 1.0 and now returns 0.0, and that a "pre-rounding"
step was removed. A money test can pass on an 8.3 host and fail on an 8.4 production image.

Source: https://github.com/php/php-src/blob/PHP-8.4/UPGRADING (verified 2026-10).
