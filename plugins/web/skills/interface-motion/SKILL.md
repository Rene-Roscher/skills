---
name: interface-motion
description: "Builds and verifies motion in app interfaces: springs as CSS linear() without a library, drags with rubber band and throw, transitions that can be caught mid-flight together with everything that moves along, and per-frame measurement in Chromium, Firefox and WebKit with reduced motion. Use when an animation feels slow, cheap, jumpy or janky, or when adding toasts, drawers, sheets or gestures. Not for static visual design or page layout."
license: Apache-2.0
compatibility: "Browsers with CSS linear() (Baseline since December 2023). Measuring needs Playwright and its Chromium, Firefox and WebKit builds installed in the project."
metadata:
  author: "Rene Roscher"
paths:
  - "**/*.vue"
  - "**/*.css"
  - "**/resources/js/**"
  - "**/components/**"
---

# Interface motion

This skill decides how motion in an app interface is built and how it is proven. Whether something should move,
which easing and how long come from Emil Kowalski's skills, which the `stack-bootstrap` skill installs from its
curated list. This skill adds what they leave open: springs as plain CSS without an animation library, gestures that
can be caught mid-flight while every element that moves with them stays in place, and measurement per frame in
three engines instead of a look at the screen. The failure it prevents: motion that looks right in one demo, then
jumps when someone grabs it, overshoots in one engine, or gets signed off by eye.

## Applies when / does not apply

- Applies: adding or tuning a transition, spring or gesture in an app interface (dashboard, admin, settings, toasts,
  drawers, sheets, popovers, lists); "feels slow", "feels cheap", "make it feel native", "it jumps when I grab it",
  "it stutters"; reviewing motion before a merge; choosing between an animation library and CSS.
- Does not apply: colour, type, spacing and layout (`design-quality`); the art direction of a new one-off page such
  as a campaign page (`frontend-design`); browser test mechanics that do not measure motion
  (`browser-verification`); native apps.

## Which skill decides what

| Question | Skill |
|---|---|
| Should this animate at all, which easing, how long | `emil-design-eng` |
| Springs, momentum, interruption, materials | `apple-design` |
| Drag, swipe, sheets, hold to confirm | `gestures` |
| Too much motion, the app feels slow | `remove-animations` |
| Dropped frames, which property to animate | `animation-performance` |
| A strict review of all motion | `review-animations` (started by hand) |
| Springs without a library, catching mid-flight, measuring, Vue and Tailwind | this skill |

Where this skill and one of those disagree, this skill's measured rules win. If they are not installed, run
`stack-bootstrap`; the rules below hold without them.

## Rules

- [default] Decide by frequency before animating: a surface seen a hundred times a day or more gets no motion, tens
  of times a day a short fade at most, occasional surfaces (dialogs, drawers, toasts) standard motion, rare moments
  may delight. On a dashboard, numbers, tables and charts move only when a value changes. Trade-off: fewer moments
  that impress in a demo. Deviate only with an ADR that names this trade-off. Source: `emil-design-eng` in
  https://github.com/emilkowalski/skills (verified 2026-11).
- [default] Generate springs as CSS `linear()` from a duration and a bounce with `scripts/spring.mjs` and play them
  as CSS transitions. A library for gesture-heavy components such as a drawer goes through `build-vs-buy` first.
  Trade-off: a retargeted transition starts again at zero velocity, and a release velocity needs a curve generated
  for that release. Deviate only with an ADR that names this trade-off. Source:
  https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/linear (Baseline since December 2023, verified
  2026-11); https://developer.apple.com/videos/play/wwdc2023/10158/ (duration and bounce, verified 2026-11).
- [default] Use bounce 0. Add bounce only where a gesture with momentum ends, such as a throw or a release, or for
  one signature element the owner approved. Trade-off: less playful motion. Deviate only with an ADR that names this
  trade-off. Source: https://developer.apple.com/videos/play/wwdc2023/10158/, "A bounce of 0 feels like a smooth,
  gradual change", around 30 % gives "noticeable bounciness" (verified 2026-11).
- [invariant] Anything a person can reverse or grab mid-way (a toggle, a drawer, a dismissible toast) animates with
  transitions, never with keyframe animations. Why: a keyframe animation restarts at its first frame and jumps,
  while a transition starts from the value on screen. Test: open a drawer and close it again after 100 ms; per-frame
  samples from `sample()` show no step larger than the largest step of an uninterrupted close. Source:
  https://www.w3.org/TR/css-transitions-1/, section 3, starting of transitions (verified 2026-11).
- [invariant] A press on an element that is still moving starts the gesture from the offset on screen: read the
  computed value, stop the running transition in the same task, and map the offset back through the drag's
  resistance curve. Why: a gesture that starts at zero or at the target moves the element under the pointer; a
  toast caught 40 ms after release jumped 28 to 31 px before this rule. Test: `catchTest()` at 40, 70, 120 and
  200 ms after release reports `drift` and `moveError` of at most 0.5 px. Source: reproducible with
  `scripts/probe.mjs` (`catchTest`).
- [invariant] Elements driven by the same gesture (a stack behind a toast, a backdrop, a progress hint) spring back
  on the same curve and duration as the dragged element, and a catch sets them from the dragged element's progress.
  Why: on a second curve the dependent element is somewhere else when the catch freezes the shared value; springs
  with bounce 0.31 and 0.24 left a 1 to 4 px width jump. Test: `catchTest()` with the dependents listed reports at
  most 1 px and 0.05 opacity for each. Source: reproducible with `scripts/probe.mjs` (`catchTest`, `dependents`).
- [invariant] Motion is accepted on numbers from headless runs in Chromium, Firefox and WebKit, each with and
  without reduced motion: end state, overshoot, jumps, and the catch test for draggable elements. Why: a 2 px jump or
  an engine difference does not show at normal speed and still reaches users. Test: the report has a number for
  every check in all three engines; a missing engine or reduced-motion run is reported as not verified. Source:
  https://playwright.dev/docs/browsers, Chromium, WebKit and Firefox (verified 2026-11).
- [invariant] A touch gesture is signed off on a real device; a headless run covers mouse input only. Why: a mouse
  drag does not exercise `touch-action`, scroll conflicts or a finger covering the element. Test: the report names
  the device and browser for each touch gesture, or lists the gesture as not verified. Source:
  https://developer.mozilla.org/en-US/docs/Web/CSS/touch-action (verified 2026-11).
- [default] Under `prefers-reduced-motion: reduce`, travel becomes an opacity change or an instant switch, and the
  state change itself stays; motion that carries information, such as progress, remains. Trade-off: two variants
  per animated component. Deviate only with an ADR that names this trade-off. Source:
  https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html and
  https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion (verified 2026-11).
- [default] Each curve is a CSS custom property with a `cubic-bezier()` fallback and a duration property next to
  it. A startup script replaces both with the generated `linear()` where the browser supports it, and components
  read the tokens instead of inlining a curve. Trade-off: two definitions per curve to keep close. Deviate only with
  an ADR that names this trade-off. Source: https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/linear
  (verified 2026-11).
- [default] Animate `transform`, `translate`, `scale` and `opacity`. Width and height only for one small,
  free-standing element whose text must not scale, after measuring it in three engines; larger morphs use
  `clip-path` or a FLIP. Trade-off: some morphs take more code. Deviate only with an ADR that names this trade-off.
  Source: `animation-performance` in https://github.com/emilkowalski/skills (verified 2026-11).
- [default] Dismiss or spring back from the pointer's travel and its release speed, not from the damped offset on
  screen. Past a free distance the offset follows a rubber band. Trade-off: thresholds need tuning per element
  size. Deviate only with an ADR that names this trade-off. Source: `gestures` in
  https://github.com/emilkowalski/skills, "Dismiss on distance OR velocity" (verified 2026-11).

## Procedure

1. Name how often the surface is seen and what the motion is for: feedback, origin, state, or softening a hard
   change. Without a purpose it stays static.
2. Pick a curve from `references/springs.md` and generate it:
   `node "${CLAUDE_SKILL_DIR}/scripts/spring.mjs" 0.35 0`.
3. For a new visible pattern, build a standalone demo page with the product's fonts and real text lengths, and wire
   it into the product after the owner approved it.
4. Build: curve tokens, transitions for interruptible state, space reserved so nothing shifts, the offset on screen
   on every press, dependent elements on the same curve (`references/interruption.md`).
5. Measure with `scripts/probe.mjs` as described in `references/measurement.md`: three engines, with and without
   reduced motion, and the catch test for anything draggable.
6. Check touch gestures on a real device.
7. Report numbers per engine, and list what stays unverified.

## Traps

- A single read after a timeout misses the overshoot and can land mid-settle. Sample every frame and read end
  values after `settled()`.
- A dev server that appends a cache-busting query after hot reloads (Vite adds `?t=`) serves the app's modules under
  that URL. Import the module by the URL the page loaded, taken from `performance.getEntriesByType('resource')`;
  a fresh import drives a second instance that renders nothing.
- Toast libraries often pause their timer while the pointer hovers the stack. Move the pointer away between steps.
- Firefox headless refuses a dev server announced on `[::]` until `network.socket.ip_addr_any.disabled` is false;
  `launch()` sets it.
- A WebKit run in which a drag never ends: read `pointerLog()` first. A missing `pointerup` means the input never
  reached the page, and the run is inconclusive, not failed.
- A custom property changed on a parent every frame restyles every descendant. When the subtree is large, set the
  transform on the moving element itself.
- A library that measures an element only when it mounts keeps a stale height after the content grows. Set the
  start size without a transition before the library measures, and keep the line count stable.
- The CSS duration of a generated curve is the settle time the generator prints, not the spring's perceptual
  duration.

## Done when

- Every animated element has a frequency, a purpose, a curve token and a reduced-motion variant.
- The report has numbers for end state, overshoot and jumps in Chromium, Firefox and WebKit, with and without
  reduced motion, plus the catch test for draggable elements.
- Touch gestures are checked on a device, or listed as not verified.
- No `transition: all`, no keyframes on interruptible state, no curve written inline in a component.

## References

- [references/springs.md](references/springs.md): load when choosing, generating or wiring a curve, or when a release velocity has to
  carry into the spring.
- [references/interruption.md](references/interruption.md): load when an element can be grabbed, reversed or dismissed mid-flight, or when other
  elements move with a gesture.
- [references/measurement.md](references/measurement.md): load before measuring motion or writing the report.
- [references/vue-reka-tailwind.md](references/vue-reka-tailwind.md): load when the project uses Vue, Reka UI or Tailwind CSS.

## Sources

- https://github.com/emilkowalski/skills (`emil-design-eng`, `gestures`, `animation-performance`), verified 2026-11.
- https://developer.apple.com/videos/play/wwdc2023/10158/, Animate with springs, verified 2026-11.
- https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/linear, verified 2026-11.
- https://www.w3.org/TR/css-transitions-1/, verified 2026-11.
- https://developer.mozilla.org/en-US/docs/Web/API/Element/setPointerCapture, verified 2026-11.
- https://developer.mozilla.org/en-US/docs/Web/CSS/touch-action, verified 2026-11.
- https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion, verified 2026-11.
- https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html, verified 2026-11.
- https://playwright.dev/docs/browsers, verified 2026-11.
