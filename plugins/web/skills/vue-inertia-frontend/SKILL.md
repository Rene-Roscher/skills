---
name: vue-inertia-frontend
description: "Writes and reviews Vue 3 script-setup TypeScript pages on Inertia: typed props from the backend, forms without double submits, partial reloads, polling, deferred props and dashboards that load each widget on its own, typed routes, vue-i18n message syntax, ref unwrapping, Reka and shadcn-vue dialogs, UI-only client state, accessible controls, library favorites. Use when editing .vue pages, components or locale files in an Inertia app, or adding a frontend dependency. Not for public Nuxt sites."
license: Apache-2.0
compatibility: "Vue 3 with script setup and TypeScript, Inertia 2 or later with @inertiajs/vue3, vue-i18n 9 or later, Reka UI 2. API syntax comes from the vendor docs for the installed versions."
metadata:
  author: "Rene Roscher"
paths:
  - "**/*.vue"
  - "**/resources/js/**"
  - "**/locales/**/*.json"
---

# Vue and Inertia frontend

This skill sets the rules for components and pages in a server-driven Vue app on Inertia: how props, forms,
reloads, translations and dialogs behave so the UI does what the server tests already prove. Where surfaces live,
CSP, caching and the build-wide i18n and route rules belong to `web-architecture`; proving the result in a browser
belongs to `browser-verification`. Vendor syntax stays in the Inertia, Vue, vue-i18n and Reka UI docs. The failure
it prevents: bugs that every server-side test passes, such as two POSTs per click, a value the user typed that
never reaches the request, or a translation that takes a whole dialog down.

## Applies when / does not apply

- Applies: writing or reviewing a `.vue` page or component in an Inertia app; forms, buttons and submit
  handling; polling, partial reloads, deferred props, dashboards and KPI pages; locale JSON edits; wrapping a
  Reka UI or shadcn-vue primitive; dialogs, sheets and confirms; toasts and other partly fitting UI libraries;
  Pinia stores; "the form submits twice", "the toggle moves but nothing saves", "the pressed style is gone",
  "field required although I typed it", "the dashboard is slow"; adding a frontend dependency or choosing a
  library for toasts, charts, icons, dates, tables or flags.
- Does not apply: public marketing or docs sites and SSR caching (`web-architecture`), visual design
  (`design-quality`), headless browser checks and screenshots (`browser-verification`), backend validation and
  authorization, general Vue questions the Vue docs answer.

## Rules

Most important first. Examples use a project-management app: projects, tasks, members.

- [invariant] One submit path per form. Do not attach `@submit` or `@submit.prevent` to Inertia's `<Form>`
  component; gate a submission with its `onBefore` callback (returning `false` cancels the visit) and submit
  programmatically through the component's `submit`. Why: Vue passes an undeclared listener through to the
  component's root element, and when that element already has its own listener both run; where this was observed,
  every click sent two POSTs, the first one committed and the second one showed "already taken". Test: a browser
  test clicks submit once and counts exactly one request to the endpoint. Source:
  https://vuejs.org/guide/components/attrs.html, "both listeners will trigger"; Inertia `onBefore`
  (https://inertiajs.com/docs/v2/the-basics/manual-visits), both verified 2026-11-03.
- [invariant] Every `<button>` inside a form has an explicit `type`, including buttons rendered by a component
  wrapper. Why: a button without `type` in a form is a submit button, and pressing Enter in a field clicks the
  first submit button in tree order, so a typeless Cancel or Delete placed first runs on Enter. Test: a DOM test or
  lint rule finds no `button` without `type` inside `form`; pressing Enter in a field sends the intended request
  only. Source: MDN `button` type default
  (https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/button) and HTML implicit submission
  (https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#implicit-submission), verified
  2026-11-03.
- [invariant] Submissions have an in-flight guard: the submit control is disabled while `processing` is true,
  handlers that can fire twice (Enter plus blur, a keyboard handler plus implicit submission) return early while a
  request runs, and no `@keyup.enter` handler submits a form that Enter already submits. Creates that must not
  repeat send an idempotency key the server checks. Why: double events produce duplicate writes that the client
  then reports as errors. Test: press Enter in a field with a blur-save handler; one request. Source: Inertia
  forms, the `processing` state and a submit button disabled by it
  (https://inertiajs.com/docs/v2/the-basics/forms, verified 2026-11-03).
- [invariant] Never pass a ref from the template into a function that assigns `.value`. Pass `$event` and mutate
  the ref in script scope. Why: top-level refs are unwrapped in templates, so the function receives the plain
  value, the assignment does nothing, and the server reports a required field the user filled in. Test: a
  component test types into the field and asserts the emitted payload carries the value. Source:
  https://vuejs.org/guide/essentials/reactivity-fundamentals.html, refs unwrap in templates (verified 2026-11-03).
- [invariant] Bind the prop and event the installed primitive declares. In Reka UI 2 a switch is controlled with
  `modelValue` and `update:modelValue`; a wrapper that receives an older name (`checked`) passes it to `$attrs` and
  the primitive runs uncontrolled. When a wrapper keeps an old name for compatibility, it maps it explicitly and
  emits both events. Why: the control moves on screen while the parent state and the saved value never change.
  Test: a component test toggles the control and asserts the parent's form value changed. Source: Reka UI
  `SwitchRoot` props and events
  (https://github.com/unovue/reka-ui/blob/v2/docs/content/meta/SwitchRoot.md, verified 2026-11-03).
- [invariant] vue-i18n messages treat `{`, `}`, `@`, `$` and `|` as syntax. Write a literal character as literal
  interpolation (`support{'@'}example.com`), and keep code and JSON examples out of locale files as component
  constants. A test compiles every message in every locale. Why: a raw `@` breaks the message and the component
  that renders it; a raw `{` made a whole lazily loaded locale file fail while the page still answered 200 with
  sections missing. Test: the compile test fails on a message containing `foo@bar`. Source:
  https://vue-i18n.intlify.dev/guide/essentials/syntax, special characters and literal interpolation (verified
  2026-11-03); build-wide i18n checks in `web-architecture`.
- [invariant] Dialogs are accessible: a visible title as the accessible name, a description linked only when it
  exists, focus moved into the dialog on open and returned to the trigger on close, and icon-only buttons with an
  `aria-label`. Without a trigger component, give the content an explicit `id`, and never set `aria-describedby`
  to `undefined` when a description is rendered. Why: missing names and broken links between title, description
  and content are invisible on screen and break screen readers. Test: a browser test reads the dialog's
  accessible name and checks `document.activeElement` after open and close. Source: WAI-ARIA APG dialog pattern
  (https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/, verified 2026-11-03).
- [invariant] Style a control's own state through its ARIA state attribute (`aria-pressed`, `aria-checked`,
  `aria-expanded`, `aria-selected`, `aria-current`, `aria-invalid`), not through `data-state`, whenever another
  primitive can render onto the same element, such as a tooltip or popover trigger with `as-child` around a
  toggle. Why: with `as-child` both primitives write `data-state` to the one merged element, so the toggle's
  `on`/`off` and the tooltip's `closed`/`delayed-open` compete for one attribute, and the pressed style vanishes
  while the saved value is right. Test: a component test wraps the toggle in the tooltip trigger, presses it, and
  asserts the pressed style through the selector on `aria-pressed="true"`. Source: Reka UI Toggle (`data-state`
  `on`/`off`, renders `aria-pressed`), TooltipTrigger (`data-state` `closed`, `delayed-open`, `instant-open`) and
  `asChild` "merging their props and behavior"
  (https://github.com/unovue/reka-ui/tree/v2/docs/content/docs/components and
  https://github.com/unovue/reka-ui/tree/v2/packages/core/src, `Toggle.vue`, `TooltipTrigger.vue`), verified
  2026-11-05.
- [default] Page props are typed from the backend contract (generated types or a contract test) and declared with
  `defineProps<T>()` in `<script setup lang="ts">`; a rendered-DOM test proves at least one new prop reaches the
  component. Trade-off: generation or a contract test in the build. Deviate only with an ADR that names this
  trade-off. Source: https://vuejs.org/guide/components/props.html (verified 2026-11-03); casing and generation
  rules in `web-architecture`.
- [default] URLs come from generated, typed route helpers (Wayfinder in Laravel apps), never from string paths.
  Trade-off: a generation step that must run before type checks. Deviate only with an ADR that names this
  trade-off. Source: `web-architecture`, typed routes rule; https://github.com/laravel/wayfinder (verified
  2026-11-03).
- [default] Reloads name what they reload: realtime handlers and polls call `router.reload({ only: [...] })` or
  `usePoll(interval, { only: [...] })` with the affected props, and poll intervals follow the cost of the props
  behind them. Trade-off: a forgotten prop stays stale until the next visit. Deviate only with an ADR that names
  this trade-off. Source: https://inertiajs.com/docs/v2/data-props/polling, `usePoll` stops on unmount and throttles
  background tabs by 90 % unless `keepAlive` (verified 2026-11-03).
- [default] A page that reads several sources loads each widget by its cost, never all in one request: cheap,
  critical data (titles, counts the layout needs) in the first response; each expensive widget as a deferred
  prop in its own group, so one slow source does not hold the others; widgets below the fold as optional props
  behind `<WhenVisible>`; every widget renders its own size-keeping skeleton, an error state with a retry that
  reloads only its prop, and its data; no page-wide spinner. Each widget polls at the interval its freshness
  needs, only its own props, and not while the tab is hidden. Trade-off: more requests and one component per
  widget. Deviate only with an ADR that names this trade-off. Proof: a backend test asserts the deferred props
  are `missing` from the first response and loads each group on its own (`loadDeferredProps`); a browser test
  blocks one group's request and sees the other widgets render and the blocked one show its error and retry.
  Source: Inertia 3 deferred props (groups "fetch props in parallel", `rescue`), load when visible, partial
  reloads (`Inertia::optional`) and testing (https://inertiajs.com/docs/v3/data-props/deferred-props,
  https://inertiajs.com/docs/v3/data-props/load-when-visible,
  https://inertiajs.com/docs/v3/data-props/partial-reloads, https://inertiajs.com/docs/v3/advanced/testing),
  verified 2026-11-06; the backend side is in `laravel-architecture`.
- [default] A UI library that fits only in part supplies the mechanics, and the product renders its own
  component; decide this before the first override. For toasts: keep the library's queue, placement, timers,
  swipe and live region, and render the product's toast component through its custom-render API (`toast.custom`
  in vue-sonner) or its unstyled mode, instead of stacking CSS overrides on its default close button, title and
  layout. List what the library gets right and wrong against the design first; a third override of its markup or
  styling means wrap or replace. Trade-off: one more component to own and test. Deviate only with an ADR that
  names this trade-off. Proof: the wrapper is the only place that imports the library; no stylesheet targets the
  library's internal class names or attributes. Source: vue-sonner README, `toast.custom(markRaw(HeadlessToast))`,
  `unstyled` with `classes`, Toaster props `position`, `closeButton` and `closeButtonPosition`
  (https://github.com/xiaoluoboding/vue-sonner, verified 2026-11-05).
- [default] Frontend dependencies come from the favorites in `references/libraries.md`: shadcn-vue on Reka UI,
  Lucide, vue-sonner, Inertia forms and props (TanStack Query only for data outside page props), Pinia for UI
  state, VueUse, `Intl` then date-fns, TanStack Table, Apache ECharts, Wayfinder, vue-i18n, and SVG flags
  (`flag-icons` once the product works with many countries). An owner profile, `AGENTS.md` or an ADR that names
  another library wins; a need the table lacks goes through `build-vs-buy`. One library per need: never a second
  toast, icon, chart, date, table, i18n, flag or UI-primitive library, and never moment. Trade-off: a specialist
  library can beat the favorite for one feature. Deviate only with an ADR that names this trade-off. Proof:
  `scripts/check_frontend_deps.py` reports no error, and each F03 warning names the ADR or profile line behind
  it. Source: `references/libraries.md` (npm registry metadata and vendor docs, verified 2026-11-06).
- [default] Client state holds UI state only: sidebar, open dialogs, view preferences. Server data lives in page
  props or a query cache keyed by tenant, and stores that hold tenant data reset on a tenant switch. Trade-off:
  some reloads instead of local caches. Deviate only with an ADR that names this trade-off. Proof: switch tenant in
  a browser test; no store holds data of the previous tenant.

## Procedure

1. Gate: is this an Inertia page, a component used by one, or a locale file? Public Nuxt pages go to
   `web-architecture`.
2. Read the installed versions of `@inertiajs/vue3`, `vue`, `vue-i18n` and `reka-ui` from the lockfile and check
   the APIs you use against their docs. Before adding a dependency, take the favorite from
   [references/libraries.md](references/libraries.md) and run `scripts/check_frontend_deps.py`.
3. Props: type them from the backend contract; add one rendered-DOM assertion for new props.
4. Forms: one submit path, `type` on every button, in-flight guard, idempotency key for creates that must not
   repeat.
5. Inputs: handlers take `$event`; wrappers bind the primitive's declared prop and event; state styles select
   ARIA attributes where a trigger wrapper shares the element.
6. Data refresh: `only` on every reload and poll; on a page with several sources, plan each widget's loading
   (first response, deferred group, when visible), its states and its poll interval with
   [references/dashboard-loading.md](references/dashboard-loading.md).
7. Text: run the locale compile test after each locale edit.
8. Dialogs: title, description, id, focus on open and close; place each overlay on `design-quality`'s layer
   hierarchy.
9. Prove behaviour with `browser-verification`: request counts, focus, the prop on screen.

## Traps

- A component wrapper (shadcn-vue `Button`) renders a native `<button>` without `type`. Inside a form it submits.
- `@keyup.enter` on a field inside a form fires after implicit submission already sent the form.
- A handler called as `onText(username, $event)` receives a string, not the ref.
- A switch wrapper that declares `modelValue` silently ignores `:checked`, and the switch still animates.
- `router.reload()` without `only` re-evaluates every prop on the server, including the expensive ones.
- An email address or a JSON sample in a locale file breaks message compilation.
- A dialog opened from a URL at hydration, with a Reka UI version before the fix for issue 2867
  (https://github.com/unovue/reka-ui/issues/2867), can leave `pointer-events: none` on `<body>` after closing, so
  the page stops reacting to clicks. More SSR dialog traps in the reference.
- Teleported dialog content sits under `<body>`, so a text color set only on the layout wrapper does not reach it.
- A pressed-state class written as `data-[state=on]:` stops working the day a tooltip trigger wraps the toggle.
- Deferred props without a group share one request, so the slowest source decides when every widget appears.
- A deferred prop that throws fails its whole group unless it is rescued; the other widgets of that group stay
  on their skeletons.
- A quick fix that installs moment, a second toast library or a second icon set next to the favorite stays
  forever; the next feature uses whichever it finds first.
- `lucide-vue-next` is deprecated on npm; `@lucide/vue` is the current Vue package.
- A toast library's default close button, position and title layout survive every override in one corner
  (mobile, dark mode, a long title); the custom component does not have that problem.

## Done when

- No `@submit` on Inertia's `<Form>`; every button in a form has a `type`; a browser test counts one request per
  submit.
- Typed props, with a rendered-DOM assertion for new ones.
- Every reload and poll names its props; on a multi-source page every expensive widget is deferred in its own
  group or loaded when visible, with its own skeleton, error and retry.
- The locale compile test is green.
- Dialogs have a name, focus moves in and returns.
- State styles on controls inside trigger wrappers select ARIA attributes, and a test proves the pressed style.
- Client stores hold no server data that survives a tenant switch.
- `check_frontend_deps.py` reports no error; every non-favorite library has its ADR or profile line.

## References

- [references/forms-and-inputs.md](references/forms-and-inputs.md): load when building or fixing a form, a custom
  input, a switch or checkbox wrapper, or a submit-twice bug.
- [references/dashboard-loading.md](references/dashboard-loading.md): load when building or reviewing a dashboard
  or any page that reads several sources or shows KPIs.
- [references/libraries.md](references/libraries.md): load before adding a frontend dependency or choosing a
  library for UI primitives, icons, toasts, forms, state, dates, tables, charts, routes, i18n or flags.
- [references/i18n-dialogs-ssr.md](references/i18n-dialogs-ssr.md): load when editing locale files, building a
  dialog, or rendering a dialog during SSR or hydration.

## Sources

- https://vuejs.org/guide/components/attrs.html: listener fallthrough, both listeners trigger, verified 2026-11-03.
- https://vuejs.org/guide/essentials/reactivity-fundamentals.html: ref unwrapping in templates, verified
  2026-11-03.
- https://inertiajs.com/docs/v2/the-basics/forms: `useForm`, `<Form>`, `processing`, verified 2026-11-03.
- https://inertiajs.com/docs/v2/data-props/polling: `usePoll`, unmount, background throttling, verified 2026-11-03.
- https://inertiajs.com/docs/v2/data-props/deferred-props: deferred props and `<Deferred>`, verified 2026-11-03.
- https://inertiajs.com/docs/v3/data-props/deferred-props, `.../load-when-visible`, `.../partial-reloads` and
  https://inertiajs.com/docs/v3/advanced/testing: groups, `rescue`, `WhenVisible`, `Inertia::optional`,
  `loadDeferredProps`, verified 2026-11-06.
- https://vue-i18n.intlify.dev/guide/essentials/syntax: special characters, literal interpolation, verified
  2026-11-03.
- https://github.com/unovue/reka-ui/blob/v2/docs/content/meta/SwitchRoot.md: `modelValue` and
  `update:modelValue`, verified 2026-11-03.
- https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/: dialog name, description, focus, verified 2026-11-03.
- https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#implicit-submission: Enter clicks the
  default button, verified 2026-11-03.
- https://github.com/unovue/reka-ui/issues/2867: body pointer-events ownership, closed, verified 2026-11-03.
- https://github.com/unovue/reka-ui/tree/v2/packages/core/src: `Toggle.vue` renders `aria-pressed` and
  `data-state`; `TooltipTrigger.vue` sets `data-state` and passes `as-child`, verified 2026-11-05.
- https://github.com/xiaoluoboding/vue-sonner: `toast.custom`, `unstyled`, Toaster props, verified 2026-11-05.
- npm registry metadata, https://github.com/laravel/vue-starter-kit, https://inertiajs.com/docs/v3/the-basics/forms
  and https://github.com/ecomfe/vue-echarts: favorites, versions, built-in Precognition, ECharts setup, verified
  2026-11-06; details in `references/libraries.md`.
