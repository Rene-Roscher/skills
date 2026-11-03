## Contents

- Project layout
- Word-timing file and a bound timeline
- Motion values
- Layout and measurement
- Briefing the image reviewer

## Project layout

One folder per video, never inside a finished one: `src/[video]/` for compositions, `film/[video]/` for the
plan, script and word timings, `public/[video]/` for voice clips, effects and plates, `out/[video]/` for
renders. Reuse building blocks (UI elements, caption, highlight, grain) by import, not by copy. A finished
video's folders are read-only; a new video that starts from one copies the composition into its own folder
first. Overwriting a finished video's voice or timing file silently changes that video on its next render.

## Word-timing file and a bound timeline

The cutting step writes one file per video; the composition imports it.

```json
{
  "l01": {"text": "Friday, 6 pm. A client is angry.", "duration": 2.18,
          "words": [{"w": "Friday,", "s": 0.12, "e": 0.55}, {"w": "6", "s": 0.61, "e": 0.78}]},
  "l02": {"text": "Their invoice was due on Monday. Four days ago.", "duration": 2.71, "words": []}
}
```

- `text` is the caption, `words` are times relative to the clip start, `duration` is the clip length.
- The composition places clips in order with a lead-in per line and derives everything else: a scene starts at
  its line's first word, an element arrives on a named word, a caption changes when its line starts.
- Helpers worth having: `start(id)`, `end(id)`, `word(id, i)`, all returning frames.
- When a take changes, re-run the cut, keep the ids, and the picture follows.

## Motion values

"100 %, not 120 %". Values for a 1080 x 1920 frame at 60 fps; scale distances with the frame size.

| Element | Value that passed | Value that was rejected |
|---|---|---|
| Haptic shake of the picture | ±1.6 px, two pulses of 0.4 s, sine envelope | ±3 px continuous |
| Phone ringing | ±0.35° in 24-frame bursts every 60 frames | ±1.3° |
| Phone entering | 140 px travel plus opacity | 500 px fly-in |
| Notification arriving | spring over 30 frames, damping 0.92, from -60 px, scale 0.94 to 1 | springs that overshoot |
| Impact shake | 7 px, decaying over 10 frames | longer or larger |
| Flashes | coloured, opacity at most 0.22 | white flashes |
| Ambient glow | ±0.05 opacity, slow | fast pulsing |
| Camera zoom | ease in and out, at most 1.9x on a detail | cuts that jump |
| Idle life of a character | breathing ±1.2 % over 3.2 s, tilt ±1.6° over 5.3 s, gaze over 6.1 s | static, or constant bouncing |

## Layout and measurement

- Safe zone: take it from the platform's template (see `video-planning`). A working box used for organic
  vertical posts at 1080 x 1920 was x 80 to 940, y 220 to 1540 (it keeps clear of the right column of action
  buttons and the caption and sound line at the bottom). It is not a platform spec; check it against a current
  screenshot of the app before relying on it. For Reels ads use Meta's
  14 % top, 35 % bottom, 6 % per side.
- Captions: inside the box, at least 40 px from any tappable-looking UI, never over the subject's key area.
  Keep a number and its unit together with a non-breaking space. Set line breaks by hand.
- Highlight a word with a solid block behind it and check the contrast of the word on the block; a light block
  needs dark text.
- Measure, per checked frame:
  - Safe zone: threshold the frame for caption-coloured pixels (for white text, all channels above 235) and
    report the bounding box against the safe-zone box.
  - Contrast: median colour of the background directly behind the caption against the caption colour, WCAG
    formula, at least 4.5:1.
  - Grounding: under an object standing on a surface, brightness falls into its contact shadow without a gap.
- Contact sheets come from `contact-sheet.py` with `--safe x0,y0,x1,y1`, on the rendered file once one exists.

## Briefing the image reviewer

Give the reviewer the contact sheet and the full-size stills, and this frame:

```text
You review frames of a short vertical video as a strict art director. Look only; change nothing.
Already approved, do not re-judge: [list].
Last round asked for: [list]. Say for each whether it is fixed.
Safe zone: x [x0]-[x1], y [y0]-[y1] in a [w] x [h] frame; the red box on the sheet.
Criteria: [the reviewer list from video-planning, plus anything specific to this video].
Answer: each problem with frame number and pixel position, the top fixes in order, a score from 1 to 10,
and a final line "SHOW: yes" or "SHOW: no".
```

Use a strong model for look decisions and a smaller one for single yes/no questions. Repeat until "SHOW: yes",
then send to the owner with what the reviewer checked.
