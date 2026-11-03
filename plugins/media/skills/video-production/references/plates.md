## Contents

- Generating a plate
- Depth of field from a depth map
- Usage rights

## Generating a plate

Use an open image model run locally whose weights allow commercial use of outputs, for example Z-Image-Turbo
(Apache-2.0 on its model card, https://huggingface.co/Tongyi-MAI/Z-Image-Turbo, checked 2026-11-03).

Prompt rules:

- Describe one real place and its light: a desk in an office at night under a warm desk lamp, rain on the
  window. Name the time of day the story needs.
- Keep the subject zone free: the surface where the phone or object will stand sits in the lower third,
  empty.
- No people, no text, no logos, no screens with content. Generated text and faces are where artefacts show.
- No brand or product words, including film stocks and camera makers: they leak objects into the picture
  (a film-stock name put a film canister on the desk).
- Asking the model for blur does not work; it renders everything sharp. Depth of field comes in the next step.
- Generate four seeds per shot at a size near the target, upscale once, and let an image reviewer pick: score,
  visible artefacts, free surface area, and the y coordinate of the surface edge.

## Depth of field from a depth map

1. Estimate depth with a depth model whose licence allows your use (Depth-Anything-V2-Small is Apache-2.0;
   Base and Large are CC-BY-NC-4.0).
2. Normalise depth to 0 (far) to 1 (near). Read the focus depth as the median in a band around the row where
   the subject stands.
3. Circle of confusion per pixel: zero within about ±0.05 of the focus depth, growing with distance to a maximum
   radius (about 34 px on a 1088-wide plate); the foreground blurs less than the background.
4. Work in linear light (gamma 2.2 removed). Boost highlights before blurring, so lights become round bokeh
   discs instead of grey mush.
5. Blur with disc kernels at about ten radius levels and blend per pixel between the two nearest levels.
6. Compress highlights gently, return to gamma, save. Keep the depth map next to the plate for later fixes.
7. Darken any bright area right behind the subject (a monitor, a window) in the plate itself, rather than with
   an overlay in the composition.

A Gaussian or CSS blur over the whole background reads as frosted glass. Real lenses make discs.

## Usage rights

Keep an asset ledger per video: asset, generating model or service, licence or plan, model card or terms URL,
date checked. Licences differ inside one model family and between code and weights; read the weights' licence.
