## Contents

- Rendering the master
- Social master
- Web player export
- Measuring colour in browsers
- Delivery note

## Rendering the master

Render once to a high-quality intermediate (ProRes HQ or lossless) with the colour space set explicitly, for
example `npx remotion render [entry] [composition] out/[video]/master.mov --codec=prores --prores-profile=hq
--color-space=bt709 --gl=angle`. Check the flags against the Remotion version in the project. All deliverables
are made from this one file.

## Social master

```bash
"${CLAUDE_SKILL_DIR}/scripts/master-social.sh" out/[video]/master.mov out/[video]/[video]-social.mp4
```

- Pass 1 measures loudness with ffmpeg's `loudnorm` (JSON). Pass 2 applies the measured values with a peak
  limiter at the true-peak ceiling and repeats with a raised aim when limiting leaves it short. The script then
  measures the written file with `ebur128` and fails when it is more than 1 LU from the target or above the
  ceiling by more than 0.5 dB.
- Defaults: -14 LUFS integrated, -1.5 dBTP, H.264 High CRF 16, yuv420p, BT.709 converted and tagged, AAC 256 kbps
  at 48 kHz, faststart. Tested on synthetic inputs from -27 to -12 LUFS with peaks near 0 dBFS.
- No platform publishes a loudness target on the pages checked (2026-11-03); -14 LUFS is a common convention.

## Web player export

```bash
"${CLAUDE_SKILL_DIR}/scripts/export-web.sh" out/[video]/master.mp4 site/media [video]
```

- Writes `[video].av1.mp4` (SVT-AV1, 8-bit, CRF 32) and `[video].h264.mp4` (fallback, CRF raised until it fits
  the size ceiling, 24 MiB by default). List the AV1 source first in the `<video>` element; the player falls
  back to H.264.
- Never 10-bit. Measured: on one Linux machine with an NVIDIA GPU, two Chromium-based browsers decoding on the
  GPU played a 10-bit AV1 file with sound and an all-black picture; 8-bit AV1 and H.264 showed it; every
  headless test looked fine. A headless check does not cover this.
- Colour tags: by default BT.601 matrix (`smpte170m`) with BT.709 primaries and transfer; a BT.709 master is
  converted. This default is a local measurement (below), not a standard.
- Web players do not normalise loudness. Set the level to sit with the page's other media with `--gain-db`.
- Captions as WebVTT next to the files; a poster image from the cover frame in AVIF and WebP.

## Measuring colour in browsers

What was measured: a brand colour on the end card, read back from the decoded frame in each browser.

- BT.601-tagged file: within one code value of the source in every browser tested (two Chromium-based browsers
  with GPU decoding, one without, Firefox with and without).
- BT.709-tagged file: within two code values everywhere except the Chromium GPU path on that machine, which
  decoded it as BT.601 and showed the colour visibly too bright.
- Untagged BT.601 content: looked dull wherever a BT.709 assumption was applied.

Re-measure before relying on it on other hardware: draw the playing video into a canvas in each target browser
with GPU decoding on, read the pixel of a known flat colour, and compare with the source value.

## Delivery note

- Files with codec, size, loudness and colour tags (the scripts print these).
- A frame strip: `contact-sheet.py [file] strip.png --count 14 --strict`; the cover: frame 0 as PNG.
- What the image reviewer saw and passed, round by round.
- What was only measured and not seen or heard by anyone yet (sound balance, voicing, loudness), so the owner
  checks those first.
- The asset ledger with licences.
- Open decisions.
