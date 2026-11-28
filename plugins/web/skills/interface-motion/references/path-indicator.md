# Indicator that travels along a path

An active-item marker on a guide line (sidebar, table of contents, stepper) that moves to the new item along the
line, through its curves, instead of jumping or sliding in a straight line.

## Build

- One SVG path describes the line. It runs straight beside each item and bends with a cubic S-curve where the
  nesting depth changes: `L x0 y0 C x0 mid x1 mid x1 y1`, with the bend limited to half the item height.
- Items carry their depth and key in data attributes (`data-depth`, `data-key`). The component measures them with
  `getBoundingClientRect()` relative to its container, adds the container's `scrollTop`, and rebuilds the path on
  `ResizeObserver` and `MutationObserver` callbacks and once fonts have loaded.
- The marker is a second copy of the same path with a dash: `stroke-dasharray: [length] [total + length]` and
  `stroke-dashoffset: -[start]`. Moving the marker changes only these two values, so a CSS transition on
  `stroke-dasharray` and `stroke-dashoffset` makes it follow the curve. The SVG attribute is animatable
  (https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/stroke-dashoffset, verified 2026-11).
- Path length at a height: binary search over `getPointAtLength()` until the point's `y` matches the item's top
  and bottom (inset a few pixels so the marker sits inside the item). The method "returns the point at a given
  distance along the path"
  (https://developer.mozilla.org/en-US/docs/Web/API/SVGGeometryElement/getPointAtLength, verified 2026-11).
- Size the SVG from the last item's bottom, never from the container's `scrollHeight`, which includes the SVG.
- Put the line on half pixels (`x = n + 0.5`, 1 px stroke) so it fills one pixel column at 1× and matches 1 px CSS
  borders it connects to.

## Behaviour

- No animation on the first placement: set a ready flag two animation frames after the first `place()`, and only
  then enable the transition, so the marker does not slide in from the top on load.
- The component lives in the persistent layout, not in the page, so it survives navigation and the marker can
  travel from the old page's item to the new one.
- With reduced motion, the transition is off and the marker moves instantly.

## Verify

- Capture frames during a move (for example at 60, 160, 260 and 600 ms) and check that the marker's centre lies on
  the path in each frame, through a depth change.
- Sample pixel colours of the line and of the CSS connector next to it at 1× and 2×; they match.
- Navigate from a long section to a short one: the container's scroll height equals its content.
