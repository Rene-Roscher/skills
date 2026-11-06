# Frontend library favorites

## Contents

- How to use this table
- Favorites per need
- Notes per need
- Sources

## How to use this table

Load this before adding any frontend dependency to an Inertia and Vue app. Take the favorite for the need. An owner
profile, `AGENTS.md` or an ADR that names another library wins over this table. A need that is not in the table
goes through `build-vs-buy` (saas plugin). One library per need: a second toast, icon, chart, date, table, i18n,
flag or UI-primitive library is never added for a quick fix. `scripts/check_frontend_deps.py` reads
`package.json` and reports avoid-list packages (F01), two libraries for one need (F02) and a non-favorite without
a recorded reason (F03).

Versions are the ones seen on 2026-11-06. Read the installed version from the lockfile and its docs before writing
code against it.

## Favorites per need

| Need | Favorite (package) | Seen 2026-11-06 | Instead of |
|---|---|---|---|
| UI primitives | shadcn-vue components copied into the project, on Reka UI (`reka-ui`) | reka-ui 2.11.0 (2026-10-05), shadcn-vue CLI 2.9.0 (2026-10-28), MIT | radix-vue (renamed to reka-ui), a second component kit |
| Icons | Lucide (`@lucide/vue`) | 1.70.0 (2026-11-06), ISC | `lucide-vue-next` (deprecated on npm), a second icon set, emoji |
| Toasts | vue-sonner through shadcn-vue's Sonner, the product's card through `toast.custom` | 2.0.9 (2025-10-01), MIT | vue-toastification, a second toast library |
| Forms | Inertia `useForm` or `<Form>`, validation on the server, Precognition built into Inertia 3 | @inertiajs/vue3 3.11.0 (2026-11-02), MIT | client-side schema validators as the source of truth, `laravel-precognition-vue-inertia` on Inertia 3 |
| Server state | Inertia page props, deferred props, partial reloads | as above | a client cache for data the page props already carry |
| Server state outside page props | TanStack Query (`@tanstack/vue-query`), only for JSON APIs the page polls or calls itself | 5.106.1 (2026-11-05), MIT | swrv, hand-written fetch caches |
| Client state | Pinia, UI state only | 4.1.0 (2026-10-14), MIT | vuex |
| Composables | VueUse (`@vueuse/core`) | 15.0.0 (2026-09-16), MIT | copies of the same helpers |
| Dates and numbers | `Intl` first; date-fns (`@date-fns/tz` for zones) where `Intl` has no API | date-fns 4.4.0 (2026-05-29), MIT | moment, moment-timezone, dayjs or luxon next to date-fns |
| Tables | TanStack Table (`@tanstack/vue-table`) through shadcn-vue's data table | 9.3.1 (2026-10-12), MIT | a grid product for a plain list |
| Charts | Apache ECharts (`echarts`) through `vue-echarts` | echarts 6.1.0 (2026-05-19), Apache-2.0; vue-echarts 8.3.2 (2026-10-09), MIT | shadcn-vue charts (Unovis), Chart.js, ApexCharts next to ECharts |
| Typed routes | Wayfinder (`laravel/wayfinder`, `@laravel/vite-plugin-wayfinder`) | plugin 0.1.11 (2026-10-16), MIT, pre-1.0 | string URLs, Ziggy |
| i18n | vue-i18n with messages loaded per locale and precompiled | 11.4.18 (2026-11-03), MIT | i18next, Fluent next to vue-i18n |
| Flags | SVG files in the project; `flag-icons` when the product works with many countries | flag-icons 7.6.0 (2026-10-15), MIT | emoji flags, regional-indicator pairs, vue-country-flag-next (no release since 2022) |

The official Laravel Vue starter kit already ships reka-ui, `@lucide/vue`, vue-sonner, VueUse and the Wayfinder
plugin, so on a scaffolded app most rows need no install.

## Notes per need

**UI primitives.** shadcn-vue is a generator: components are copied into `resources/js/components/ui` and owned
by the project, so changes go into those files, not into overrides. Reka UI supplies behaviour and accessibility.
A component shadcn-vue does not have is built on the matching Reka primitive before another kit is considered.

**Toasts.** vue-sonner had its last release on 2025-10-01 and its repository was last pushed on 2025-12-30. It is
still the toast of shadcn-vue and of the Laravel starter kit, so it stays the favorite; check its issues against
the installed Vue version when upgrading. Keep the library behind one wrapper (`toast.custom` with the product's
card) so a replacement touches one file. If it stops working, the fallback is Reka UI's Toast primitive, which the
project already has; shadcn-vue deprecated its own Reka-based toast in favour of Sonner, so the fallback is a
custom component.

**Forms.** Inertia 3 contains Precognition: `useForm(...).withPrecognition()` with `validate()`, `invalid()` and
`validating`, and the `<Form>` component's `validate`, `invalid` and `touched` slot props. The separate
`laravel-precognition-vue-inertia` package declares Inertia 1 or 2 as its peer and is removed on Inertia 3. The
server's form request stays the only source of validation rules.

**Server state.** Inertia props, deferred props and partial reloads come first (`dashboard-loading.md`). TanStack
Query is for data that does not arrive as page props, for example a widget polling a JSON endpoint; its query keys
include the tenant.

**Dates and numbers.** `Intl.DateTimeFormat`, `Intl.RelativeTimeFormat`, `Intl.NumberFormat` and
`Intl.PluralRules` cover formatting in the user's locale. date-fns covers arithmetic and parsing that `Intl` does
not (adding months, start of week, intervals). moment is in maintenance mode by its own docs.

**Charts.** Import ECharts in its tree-shaken form and register only what the chart uses:

```ts
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, AriaComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, AriaComponent])
```

- Colours, fonts and grid lines come from the design tokens, read once per theme into an ECharts theme object;
  switch the theme when the colour scheme changes (`THEME_KEY` or the `theme` prop). A theme switch recreates the
  chart model, so keep legend selection and zoom that must survive in the option.
- Accessibility: register `AriaComponent` and set `aria.show: true`, so the chart gets an `aria-label` built from
  title, type and data; use `aria.decal.show` where series differ only by colour. Every chart also has a text
  alternative: the key number in text, or the data as a table behind a toggle.
- `autoresize` on the component, and a fixed height on its container.
- Contrast of marks, axes and the chart type follow `design-quality` (chart marks at least 3:1).

**Typed routes.** Wayfinder is still below 1.0; pin it and read its changelog on upgrades.

**i18n.** Messages load per locale (and per domain on large apps) with dynamic imports and are precompiled at
build time (`@intlify/unplugin-vue-i18n`), which `web-architecture` requires for a strict CSP.

**Flags.** The default is an SVG file per flag the product shows, imported from `resources/`. When the product
works with many countries (country pickers, per-country data, many locales), use `flag-icons`: MIT, 271 flags in
4:3 and 1:1, active (release 2026-10-15), and plain SVG files and CSS without a framework binding. Import single
files (`flag-icons/flags/4x3/de.svg`) or limit its SASS build to the countries in use
(`$flag-icons-included-countries`); importing the full CSS ships every flag file as an asset. `country-flag-icons`
was the alternative: also MIT and maintained, but 3:2 only, React components first, and a `unicode` export that
produces emoji flags, which the emoji rule forbids. A flag always sits next to the country or language name; it
never stands alone as the label.

## Sources

- npm registry metadata (`npm view [package] --json`: version, release time, licence, deprecation, peer
  dependencies) for every package in the table, read 2026-11-06.
- https://github.com/laravel/vue-starter-kit (`package.json`): reka-ui, `@lucide/vue`, vue-sonner, VueUse,
  Wayfinder plugin, read 2026-11-06.
- https://inertiajs.com/docs/v3/the-basics/forms: Precognition built in, `withPrecognition()`, `<Form>`
  `validate`, removing `laravel-precognition`, verified 2026-11-06.
- https://github.com/unovue/shadcn-vue (`apps/v4/content/docs/components`): Sonner built on vue-sonner, toast
  deprecated in favour of Sonner, data table on TanStack Table v9, charts on Unovis, read 2026-11-06.
- https://github.com/ecomfe/vue-echarts: tree-shaken `use()`, `VChart`, `THEME_KEY`, `autoresize`, theme switch
  resets uncontrolled state, verified 2026-11-06.
- https://echarts.apache.org/handbook/en/best-practices/aria/: `aria.show`, `AriaComponent`, generated
  `aria-label`, `aria.decal`, verified 2026-11-06.
- https://github.com/lipis/flag-icons and the 7.6.0 package contents (`flags/4x3`, `flags/1x1`, 271 files,
  `$flag-icons-included-countries`), read 2026-11-06.
- https://momentjs.com/docs/#/-project-status/: "Moment.js is a legacy project in maintenance mode.", read
  2026-11-06.
