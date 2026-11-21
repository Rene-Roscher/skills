# Springs as CSS

## Contents

- The model
- Values to start from
- Generating a curve
- Wiring curves as tokens
- Carrying a release velocity
- Reduced motion

## The model

A spring is described by two numbers: a perceptual duration and a bounce. Bounce 0 is critically damped, a smooth
approach with no overshoot. Positive values overshoot; negative values flatten the approach. The conversion to the
physics triplet, with mass 1:

| Quantity | Formula |
|---|---|
| natural frequency | w0 = 2 pi / duration |
| stiffness | w0 squared |
| damping ratio | 1 - bounce for bounce of 0 or more, 1 / (1 + bounce) below 0 |
| damping | 2 x damping ratio x w0 |
| overshoot (bounce above 0) | exp(-pi x ratio / sqrt(1 - ratio squared)) |

The generator samples the damped oscillator until it stays within 0.2 % of the target and writes the samples as a
`linear()` easing. That time is the CSS `transition-duration`. It is longer than the perceptual duration because the
spring's tail is part of the curve.

## Values to start from

Measured with `scripts/spring.mjs`:

| Use | Duration | Bounce | Settles after | Overshoot |
|---|---|---|---|---|
| A drawer, popover or sheet settling without a gesture | 0.30 s | 0 | 400 ms | 0 |
| The same, a little calmer | 0.35 s | 0 | 471 ms | 0 |
| Larger surfaces | 0.40 s | 0 | 537 ms | 0 |
| The end of a release with momentum | 0.35 s | 0.15 | 446 ms | 0.6 % |
| A throw that lands | 0.40 s | 0.20 | 508 ms | 1.5 % |
| One approved signature element | 0.36 s | 0.31 | 537 ms | 5.0 % |

Durations under 300 ms keep frequent motion out of the way. Modals, drawers and toasts may take longer because the
tail of the curve does not hold the user up: the element is usable before it rests.

## Generating a curve

```bash
node "${CLAUDE_SKILL_DIR}/scripts/spring.mjs" 0.35 0           # duration, bounce
node "${CLAUDE_SKILL_DIR}/scripts/spring.mjs" 0.35 0.2 --v 3   # with a release velocity
node "${CLAUDE_SKILL_DIR}/scripts/spring.mjs" --k 300 --d 24   # stiffness and damping, mass 1
node "${CLAUDE_SKILL_DIR}/scripts/spring.mjs" --self-test
```

The first line of the output states duration, bounce, overshoot and settle time; the second is a ready transition.
The module also exports `spring()`, `params()` and `position()` for use in the browser.

## Wiring curves as tokens

Declare each curve with a fallback that every browser understands, next to its duration:

```css
:root {
    --ease-settle: cubic-bezier(0.2, 0, 0, 1);
    --ease-settle-ms: 400ms;
}

.drawer {
    transition: translate var(--ease-settle-ms) var(--ease-settle);
}
```

At startup, replace both where the browser supports `linear()`:

```js
import { spring } from './spring.mjs';

if (CSS.supports('transition-timing-function', 'linear(0, 1)')) {
    const settle = spring({ duration: 0.3, bounce: 0 });
    document.documentElement.style.setProperty('--ease-settle', settle.easing);
    document.documentElement.style.setProperty('--ease-settle-ms', `${settle.ms}ms`);
}
```

Components read the tokens. A component that needs a curve nobody has yet adds a token; it does not inline a
`linear()` list.

## Carrying a release velocity

A release has a speed. To let the element leave the pointer at that speed, give the spring an initial velocity in
progress units per second: the release speed in px/s divided by the px still to travel. Generate the curve for that
release and set it on the element for this one transition only:

```js
const remaining = Math.hypot(targetX - x, targetY - y);
const velocity = remaining > 0 ? releaseSpeedPxPerSecond / remaining : 0;
const curve = spring({ duration: 0.35, bounce: 0.15, velocity });
element.style.transition = `translate ${curve.ms}ms ${curve.easing}`;
```

Clear the inline transition when it ends, so the token applies again. A CSS transition that is retargeted while it
runs starts again at zero velocity; when a curve has to stay continuous through retargeting, generate the next curve
from the current speed the same way.

## Reduced motion

Under `prefers-reduced-motion: reduce`, set travel to an opacity change or let the state switch at once. Keep a
duration of a frame or two rather than none, so code that waits for `transitionend` still runs.
