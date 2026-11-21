# Vue, Reka UI and Tailwind CSS

## Vue

- `<Transition>` applies enter and leave classes; give it CSS transitions on `transform` and `opacity`, with the
  curve tokens from the springs reference.
- `mode="out-in"` waits for the leave before the enter starts, which leaves a gap. When text swaps inside a component
  that keeps its place, cross-fade both copies on top of each other instead.
- Leaving text that should not rewrap while it fades: fix its width in `@before-leave` from `offsetWidth`.
- `<TransitionGroup>` moves list items with its move class (a built-in FLIP). Give the move class a transition on
  `transform` only.
- A drag handler keeps its gesture state in plain variables, not in reactive state, and writes the offset through
  one reactive style binding. The catch reads `getComputedStyle` in the `pointerdown` handler before anything else
  changes the element.
- Page changes in an app (Inertia visits, router navigation) get no page transition: they happen too often.

## Reka UI

Floating content exposes its computed origin as a custom property, so a scale-in starts at the trigger:

```css
.popover-content {
    transform-origin: var(--reka-popover-content-transform-origin);
}
```

The same pattern exists for dropdown menus (`--reka-dropdown-menu-content-transform-origin`) and hover cards
(`--reka-hover-card-content-transform-origin`). Check the component's API reference for others. Wrappers such as
shadcn-vue often set it already; read the component before adding a second origin.

## Tailwind CSS

- List the animated properties: `transition-[translate,opacity]` or `transition-transform`, never `transition-all`.
- Curve tokens as theme variables: `--ease-*` in `@theme` creates the `ease-*` utilities. A startup script can then
  replace the variable's value with a generated `linear()`:

  ```css
  @theme {
      --ease-settle: cubic-bezier(0.2, 0, 0, 1);
  }
  ```

- In Tailwind CSS 4, `hover:` applies only when the primary input can hover (`@media (hover: hover)`), so hover
  motion does not stick after a tap on touch screens. A custom hover variant brings back the old behaviour; keep the
  default.
- Press feedback belongs on the shared button component once, for example a scale to 0.97 on `active:`, not on
  each button.

## Toast libraries

Libraries such as vue-sonner place and stack toasts; the look can be a component of the product. Two behaviours to
plan for, observed with vue-sonner 2.0.9:

- The toast's height is measured when it mounts. A toast that grows afterwards keeps the old height in the stack:
  set the start size without a transition before the library measures, and keep the line count per toast stable.
- The stack reads internal data attributes for front and index. Pin the version and cover the gestures with a
  browser test, so an update that renames them fails a test instead of a user.

## Sources

- https://reka-ui.com/docs/components/popover, https://reka-ui.com/docs/components/dropdown-menu and
  https://reka-ui.com/docs/components/hover-card, origin-aware animations, verified 2026-11.
- https://tailwindcss.com/docs/upgrade-guide, hover styles on mobile, and https://tailwindcss.com/docs/theme, the
  `--ease-*` namespace, verified 2026-11.
- https://vuejs.org/guide/built-ins/transition.html and https://vuejs.org/guide/built-ins/transition-group.html,
  verified 2026-11.
- https://github.com/emilkowalski/skills (`emil-design-eng`, press feedback), verified 2026-11.
