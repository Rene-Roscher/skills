# web

Where web surfaces live and how they render, and how to prove a UI change works. Public pages (marketing,
pricing, docs) run as their own deployment with their own failure domain, so an outage of the product does not
take them down. Authenticated dashboards render on the client. UI changes are checked in a headless browser
with measured results instead of a look at a screenshot.

## Skills

| Skill | Use it when |
|---|---|
| `web-architecture` | planning a public site, choosing SSR, CSR or prerendering, adding typed routes, i18n messages, a CSP or `v-html` |
| `design-quality` | building or reviewing app screens and marketing pages so they match the product and measure up, not just look generated |
| `vue-inertia-frontend` | writing or reviewing Vue pages and components on Inertia: forms, reloads, locale messages, dialogs |
| `browser-verification` | asked to verify, screenshot or measure a page, or to confirm a frontend fix works before calling it done |

The skills load automatically when Claude Code works with matching front-end files. You can also call one
directly, for example `/web:browser-verification`.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install web@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it. Server-side permission
rules are in `authorization-rbac` from the `saas` plugin, which is not a dependency; install it for those
rules.

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off). Choices such as the component library or viewport list live in the example profile under
`templates/project-overlay/profiles/` at the repository root.

See [CHANGELOG.md](CHANGELOG.md) for changes.
