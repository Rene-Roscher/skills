# Changelog

All notable changes to the `web` plugin are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## 0.1.0 - Unreleased

### Added

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
