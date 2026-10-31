# Stack notes: Node

- Install in the build stage with `npm ci` (or `pnpm install --frozen-lockfile`, `yarn install --immutable`,
  written out because a `docker build` step doesn't see the runner's `CI` variable). Copy `package.json` and the
  lockfile first, then the source.
- Build, then produce production dependencies in a separate step or stage (`npm ci --omit=dev`) and copy only
  those `node_modules` into the runtime stage.
- Private registries: the token comes in as a secret mount, either as an environment variable referenced by
  `.npmrc` or as the `.npmrc` file itself mounted with `target=`. Never `ARG NPM_TOKEN`.
- Runtime base: a distroless Node image or the official slim image. Read the base's configured entrypoint
  (`docker inspect -f '{{json .Config.Entrypoint}}'`) before writing `CMD`, so the command doesn't end up as
  `node node server.js`.
- The runtime stage needs no package manager. Scripts that call `npm run` at startup need replacing with a direct
  `node` command.
- Front-end builds: source maps either never reach the runtime stage or are uploaded during the build through a
  secret mount and deleted in the same step. Static assets for a CDN come from a `FROM scratch AS assets` stage.
- Front-end builds that read configuration at build time inline it into the bundle. An empty variable produces a
  bundle that builds fine and fails in the browser; assert required variables before the build step.
- Native modules are compiled for one architecture. For multi-arch images, install on the target platform.

Sources: https://docs.npmjs.com/cli/v11/commands/npm-ci, https://pnpm.io/cli/install,
https://yarnpkg.com/cli/install, https://docs.docker.com/build/building/secrets/ (verified 2026-10).
