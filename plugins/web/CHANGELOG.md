# Changelog

All notable changes to the `web` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.2.0 - 2026-11-28

### Added

- `design-quality`: audit what you touch, unasked, content edits included (rendered headings against the
  source); prose at 45 to 80 characters per line, measured on rendered lines; traps for dialogs after a reset,
  native dialogs that do not lock scrolling, modal-by-default menus, 1 px SVG lines at 1×, overlays sized from
  `scrollHeight`; tell T20 (tinted box with a border in the same hue); new reference `docs-sites.md` for docs
  and help sites. The description now names edits to rendered content.
- `browser-verification`: crawl every route after a content or shared-layout change, with reference
  `content-crawl.md`.
- `interface-motion`: reference `path-indicator.md`, a marker that travels along a curved guide line as a dash
  of the same path.

## 0.1.0 - Unreleased

### Added

- Skill `interface-motion`: springs as CSS `linear()` with a generator, motion that can be caught mid-flight
  with dependent elements on the same curve, per-frame measurement in Chromium, Firefox and WebKit with a catch
  test, and notes for Vue, Reka UI and Tailwind CSS. `design-quality` points to it from its motion rule.
- Skills `web-architecture`, `browser-verification` and `design-quality`.
- Skill `vue-inertia-frontend`.
- Dependency on `core`.
- Design references per surface type in `design-quality`.
- `design-quality`: no emoji and no characters as icons (flags as SVG), enforced by the audit's new `emoji-glyph`
  and `symbol-icon` checks; global CSS inside cascade layers, with an `unlayered-css` warning; theme tokens from
  measured reference values with one token per role; a state matrix for interactive controls; one z-index scale,
  checked through a `zIndex` token list.
- `vue-inertia-frontend`: state styles through ARIA attributes where a trigger wrapper shares the element; partly
  fitting UI libraries (toasts) used for mechanics with the product's own component.
- `browser-verification`: the suite runs on its own ports, database and build and starts clean every run; design
  changes and their tests change in the same commit.
- Eval cases for flag emoji, unlayered focus styles, an isolated end-to-end setup and the pressed style under a
  tooltip trigger.
- `design-quality`: the emoji rule covers everything the agent writes (UI, docs, comments, mails, CLI output,
  invented data), with real icon or SVG assets instead and user input kept as entered, plus a codepoint scan for
  changed files; the z-index scale became a layer hierarchy invariant (which layer opens which, child above
  opener, Escape and focus on the topmost only); the SKILL.md body is back to 300 lines.
- `vue-inertia-frontend`: pages with several sources load each widget by cost (first response, own deferred
  group with rescue, when visible), with per-widget skeleton, error, retry and poll interval; reference
  `dashboard-loading.md`.
- Eval cases `adversarial-flair-without-emoji` and `output-confirm-above-slideover`; the flag grader matches
  emoji by escaped ranges instead of literal characters.
- `vue-inertia-frontend`: favorite library per need in `references/libraries.md` (shadcn-vue on Reka UI,
  `@lucide/vue`, vue-sonner, Inertia forms with built-in Precognition, Pinia, VueUse, `Intl` then date-fns,
  TanStack Table, Apache ECharts, Wayfinder, vue-i18n, SVG flags or flag-icons), one library per need, and
  `check_frontend_deps.py` for avoid-list packages, duplicates per need and unrecorded non-favorites.
- Eval cases `trigger-add-revenue-chart` and `adversarial-quick-fix-second-libraries`; eval fixtures import
  icons from `@lucide/vue` instead of the deprecated `lucide-vue-next`.
