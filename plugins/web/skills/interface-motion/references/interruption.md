# Catching motion mid-flight

## Contents

- Why transitions and not keyframes
- Catching a dragged element
- Elements that move with the gesture
- A worked example
- What the catch test checks

## Why transitions and not keyframes

A CSS transition that is interrupted starts its next run from the value currently on screen. A keyframe animation
starts at its first keyframe again, so a quick second trigger jumps. Anything a person can reverse, grab or dismiss
mid-way therefore animates with transitions, or with a script that reads the current value first.

## Catching a dragged element

When a press lands on an element that is still springing back, the gesture continues from where the element is
on screen:

1. In `pointerdown`, read the offset on screen with `getComputedStyle(element).translate`, or the matrix from
   `transform`. During a transition this is the animated value, not the target.
2. Stop the transition in the same task: set the offset as the inline value and switch to a state class whose
   `transition-property` leaves the offset out. Both changes apply in one style update, so nothing moves.
3. Map the offset back into pointer space. With a rubber band that shows `s = f(d)` for a pointer distance `d`, the
   pointer distance is the inverse `d = f'(s)`. For the curve that is 1:1 up to `free` px and then approaches
   `reach` px:

   ```text
   shown(d)   = d                                            when d <= free
              = free + (reach - free) * (1 - exp(-(d - free) / soft))
   pointer(s) = s                                            when s <= free
              = free - soft * ln(1 - (s - free) / (reach - free))
   ```

4. Start the gesture's origin at the press position minus that pointer offset, in the offset's direction. The first
   pointer move then continues the curve instead of restarting it.
5. Capture the pointer after these steps, and treat a press outside the spring's running time as an ordinary press.

Keep the release time and the settle time from the spring generator; a press inside that window is a catch.

## Elements that move with the gesture

A stack behind a toast, a backdrop that dims with a sheet, or a hint that grows while dragging all follow one shared
value, for example a custom property `--peek` from 0 to 1. A catch freezes that value too, so the dependent elements
have to be where the value says:

- While the dragged element springs back, the dependent elements spring on the same curve and duration. Set this
  with a state attribute on the shared parent during the return, and let the dependent elements read their curve
  from custom properties that the attribute overrides.
- At the catch, compute how far the spring has come back from the dragged element's offset:
  `progress = (offset . releaseOffset) / |releaseOffset|^2`, 1 at the release, 0 at rest, below 0 while it
  overshoots. The shared value is then `valueAtRelease * progress`.
- If the drag maps pointer distance to the shared value in its own way, blend the difference out as the pointer
  moves on: `value = mapping(distance) + difference * exp(-travel / length)`. Nothing steps at the catch, and the
  usual mapping returns after a short way.

## A worked example

A toast in a project tool can be dragged in any direction. It follows the pointer 1:1 for 16 px, then a rubber band
towards 72 px with a softness of 60 px. It is thrown away past 80 px of pointer travel or above 0.45 px/ms, and
springs back otherwise. Waiting toasts sit behind it as thin edges and grow towards their own size while it is
dragged.

| Measured | Before | After |
|---|---|---|
| Toast pressed 40 ms after release | jumped 28 to 31 px back | 0 px in Chromium and Firefox |
| 5 px of pointer travel after the catch | snapped to about 5 px | on the curve within 0.1 px |
| Waiting toast at the catch, its size on a second spring | 1 to 4 px width jump | 0.1 px once it shared the toast's curve |

The two springs that caused the width jump had bounce 0.31 and 0.24. Their progress differs by only 0.01 to 0.02
early on, but the waiting toast's width spans the difference between two text lengths, a few hundred px.

## What the catch test checks

`catchTest()` in `scripts/probe.mjs` pulls the element, holds still so it is no throw, lets go, and presses again
40, 70, 120 and 200 ms later. A capture listener reads the state at the press before the component's own handler
runs. It then reports:

- `drift`: movement while the pointer holds still for two frames, expected 0;
- `moveError`: distance from the curve's prediction after 5 px of pointer travel, expected 0;
- `dependents`: the largest box and opacity change of each listed dependent element while held still;
- `settled`: the offset 900 ms after letting go, expected 0.

Pass criteria are in the measurement reference.
