---
name: video-production
description: "Builds, voices, mixes, masters and delivers an approved video plan: Remotion animation bound to voice word timings, contact sheets with safe zones, independent image review, TTS takes chosen by measurement, forced-alignment cuts, synthesised SFX, voice-over-rest checks, -14 LUFS social master, 8-bit AV1 web export. Use when rendering or fixing a planned video. Not for planning or live footage."
license: Apache-2.0
compatibility: "Remotion 4 (rules checked against the v4.0.540 docs), ffmpeg with libx264 and libsvtav1 (scripts tested with ffmpeg 6.1.1), Python 3.9 or later; numpy for audio-check.py and synth-sfx.py. Voice, image and depth models are examples, not requirements."
metadata:
  author: "Rene Roscher"
paths:
  - "**/remotion.config.*"
---

# Video production

This skill turns an approved plan from `video-planning` into a delivered file: scenes, voice, sound, master,
web export and the delivery note. It decides the tools, the order, the numbers and the checks; renderer, TTS and
ffmpeg syntax stay in their docs (check them with a documentation tool such as Context7 before relying on an
option). The failure it prevents: a video that looks right in a few stills and sounds right to nobody, because
the agent building it cannot see or hear it and nothing was measured.

## Applies when / does not apply

- Applies: building scenes or style frames, rendering, generating or cutting a voice-over, making sound
  effects, mixing, mastering for social platforms, exporting for a website player, delivering, fixing any of
  these after review.
- Does not apply: deciding what the video says or how it looks (`video-planning`), editing recorded camera
  footage, live streaming, podcasts without picture.

## Rules

### Build

- [invariant] Start only from an approved plan with a timing table. Why: every unapproved decision made while
  building is a render and a review round spent twice. Test: the plan's approval line exists before the first
  render command.

- [default] Use Remotion for programmatic video. Why: each frame is a pure function of its frame number, so a
  re-render after a fix is exact and scenes are code that can be reviewed. Trade-off: rendering runs a
  headless browser and is slower than a native editor; companies above three people need a paid company
  licence. Deviate only with an ADR that names this trade-off. Source:
  https://www.remotion.dev/docs/license (free for individuals and organisations of up to 3 people, verified
  2026-11-03).

- [invariant] Drive every animation from `useCurrentFrame()` (with `interpolate()` or `spring()`). No CSS
  transitions or animations, no `requestAnimationFrame`, no `useFrame()` from React Three Fiber, no shader that
  reads wall-clock time. Why: anything not derived from the frame number renders differently per frame and
  flickers. Test: a search of the composition sources for `requestAnimationFrame`, `useFrame(`, `transition:`
  and `animation:` finds nothing. Source: https://www.remotion.dev/docs/animating-properties and
  https://www.remotion.dev/docs/troubleshooting/css-animations, verified 2026-11-03.

- [invariant] Give `<ThreeCanvas>` explicit `width` and `height`, and render WebGL scenes with `--gl=angle`.
  Why: without the size the Studio layout breaks; without ANGLE the headless browser can return an empty
  canvas. Test: a still of a 3D frame is not uniform in colour. Source: https://www.remotion.dev/docs/three-canvas
  and https://www.remotion.dev/docs/three-webgpu-canvas, verified 2026-11-03 against the v4.0.540 docs.

- [invariant] Set the colour space explicitly on every render (`--color-space=bt709` for social masters).
  Why: Remotion 4 defaults to BT.601 and Remotion 5 to BT.709, so an implicit default changes colour when the
  project upgrades. Test: `ffprobe` reports the expected `color_space` on the render. Source:
  https://www.remotion.dev/docs/options/color-space, verified 2026-11-03.

- [invariant] Bind the timeline to the voice's word timings. Scene starts, element arrivals and caption changes
  are computed from a word-timing file (one entry per line: clip, duration, words with start and end), never
  typed in as seconds. Why: every new take or language shifts every beat; a bound timeline follows on its own.
  Test: swapping in a different take moves the scenes without code changes; no scene timing is a literal frame
  number. Format in [references/build-and-review.md](references/build-and-review.md).

- [invariant] Review with independent eyes until it passes, then show the owner. Render the key frames,
  build a contact sheet with the safe zone drawn (`contact-sheet.py`), and give it with the single stills to an
  image-reviewing subagent that did not build the scene, with explicit criteria and a request for pixel
  positions. Fix and repeat until it passes. Why: the agent that writes a scene cannot see it, and an agent
  judging its own work tends to confirm it; typical looks needed four to six rounds. Test: the report lists each
  round's verdict with pixel references; the owner sees only a passed version. See `agent-delegation` (core).

- [invariant] Measure; do not eyeball. Safe zone (no text or UI pixels outside the box), caption contrast at
  least 4.5:1 against the measured background behind it, at least 40 px between captions and tappable UI.
  Why: "looks inside" was wrong by tens of pixels more than once. Test: the report gives the numbers per
  checked frame. Source: https://www.w3.org/TR/WCAG22/ (1.4.3 contrast minimum, verified 2026-11-03).

- [default] Keep motion at "100 %, not 120 %": the numbers in
  [references/build-and-review.md](references/build-and-review.md). Trade-off: less punch in the first second.
  Deviate only with an ADR that names this trade-off. Proof: the louder values (±3 px shake, 500 px fly-ins,
  white flashes, overshooting springs) were rejected as too much.

### Voice

- [default] Put the TTS provider behind a small adapter (script in, audio plus request id and cost out) and use
  ElevenLabs as the default example. Trade-off: a paid per-character service and its terms. Deviate only with
  an ADR that names this trade-off. Proof: the selection and cutting steps below work on any provider's output.

- [invariant] Check the remaining credits before generating and state the expected cost; log the actual cost
  per request. Why: in one measured request a 640-character script, tags included, cost 252 credits, and a
  second seed doubles that. Test: the log has free credits before and the cost header of each request after. Source:
  https://elevenlabs.io/docs/api-reference/user/subscription/get (`character_count`, `character_limit`) and
  https://elevenlabs.io/docs/api-reference/introduction (`character-cost` header), verified 2026-11-03.

- [default] Generate the whole script in one request, two seeds, and choose by measurement: word error rate of a
  Whisper transcript against the spoken text, a MOS predictor compared only between takes of the same voice,
  and timing against the plan. Trade-off: a weak single line costs a whole take or a stitched re-take. Deviate
  only with an ADR that names this trade-off. Proof: one request kept energy and voice consistent across lines
  where line-by-line requests drifted. Details: [references/voice.md](references/voice.md).

- [invariant] Re-do a single line only with its neighbours as context (`previous_text` and `next_text`, or
  request IDs where the model supports stitching). Why: a line generated alone changes pitch and pace against
  its neighbours. Test: the re-take request carries the context fields. Source:
  https://elevenlabs.io/docs/api-reference/text-to-speech/convert and
  https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching (stitching not
  available for `eleven_v3`), verified 2026-11-03.

- [invariant] Cut takes by forced alignment over the exact spoken text, at the quietest point inside each
  pause, with short fades (about 8 ms). Never cut on Whisper timestamps and never pad with digital silence.
  Why: Whisper times drift by tens of milliseconds and clipped word ends; inserted zeros sound like a dropout
  against the take's own room tone. Test: each cut lies at an RMS minimum inside its pause; the voice track has
  no run of exact zeros longer than 10 ms. Details: [references/voice.md](references/voice.md).

- [invariant] Never leave a single isolated word (an exclamation, a one-word line) to the model on its own:
  embed it in a sentence and measure that it is voiced (`audio-check.py voicing`). Why: one voice spoke an
  isolated word unvoiced, as a whisper, whatever the direction tags said. Test: the word's voiced share passes
  the check (measured 20 to 40 % for normal words and 0 to 2 % for whispered ones on that voice).

- [default] Use a local, free TTS model for timing drafts and switch to the final voice only for the approved
  script. Trade-off: the draft voice's pace differs from the final one. Deviate only with an ADR that names this
  trade-off. Proof: drafts cost no credits; the bound timeline re-flows when the final take arrives.

### Sound

- [default] Synthesise sound effects (`synth-sfx.py`) instead of using samples, stock libraries or platform
  sounds. Trade-off: time to tune each sound. Deviate only with an ADR that names this trade-off. Why: no
  licence question, every parameter adjustable after review, and business accounts on TikTok only get the
  Commercial Music Library. Source:
  https://ads.tiktok.com/resources/help/article/how-to-use-the-commercial-music-library?lang=en, verified
  2026-11-03.

- [default] Mix voice first: sound effects at 0.3 to 0.5, the bed at 0.3, both ducked under speech. Trade-off:
  effects carry less drama. Deviate only with an ADR that names this trade-off. Proof: at 0.9 and 0.5 the voice
  was buried under its own effects.

- [invariant] Measure voice against everything else on the final file: at least +4 dB per spoken line
  (`audio-check.py voice-to-rest`). Why: mastering, limiting and ducking change the balance after the mix
  looked fine. Test: the script passes on the delivered file.

### Images

- [default] Generate background plates locally with an open image model and give them depth of field from a
  depth-estimation model, not from a blur filter. Prompt rules and the bokeh method are in
  [references/plates.md](references/plates.md). Trade-off: a GPU and minutes per plate. Deviate only with an ADR
  that names this trade-off. Proof: CSS blur read as frosted glass; depth-based disc blur read as a lens.

- [invariant] Check usage rights of every model or service whose output ends up in a published video: the
  weights' licence on the model card, the service's plan terms. Why: in one model family the small depth model
  is Apache-2.0 while the larger ones are CC-BY-NC-4.0; some open TTS weights are non-commercial; a TTS
  service's commercial licence started with its first paid tier. Test: an asset ledger names model, licence and
  source URL per generated asset. Source: https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf,
  https://huggingface.co/depth-anything/Depth-Anything-V2-Base-hf, https://huggingface.co/SWivid/F5-TTS and
  https://elevenlabs.io/pricing, verified 2026-11-03.

### Master and deliver

- [default] Master social files with `master-social.sh`: two-pass loudness normalisation to about -14 LUFS
  integrated, true peak at or below -1.5 dBTP with a limiter, H.264 High yuv420p tagged BT.709, AAC, faststart,
  checked on the written file. Trade-off: -14 LUFS is a convention, not a platform spec; none of the platforms
  checked publishes one. Deviate only with an ADR that names this trade-off. Source:
  https://support.google.com/youtube/answer/6039860 (no loudness target listed, verified 2026-11-03); one-pass
  loudnorm stopping short was measured.

- [invariant] For a website's own player, export 8-bit AV1 with an H.264 fallback (`export-web.sh`), never
  10-bit AV1, with the colour matrix tagged. Why: measured on one Linux setup with GPU decoding, Chromium-based
  browsers played a 10-bit AV1 file with sound and a black picture; 8-bit AV1 and H.264 showed it. Test: the
  script refuses anything but 8-bit 4:2:0 and prints the tags.

- [default] Tag web exports as BT.601 matrix (`smpte170m`) with BT.709 primaries and transfer. Trade-off: this
  is a local measurement, not a standard: on one setup it was the only tagging that showed a brand colour
  within one code value in every browser tested, while BT.709-tagged files drifted on the GPU decode path.
  Deviate only with an ADR that names this trade-off. Proof: re-measure a known colour on the end card in
  the target browsers before changing it (method in
  [references/master-and-deliver.md](references/master-and-deliver.md)).

- [invariant] Do the final check on the rendered MP4, not on stills, and deliver with a frame strip
  (`contact-sheet.py --count 14`), the cover (frame 0) and a note that separates what a reviewer saw from what
  was only measured. Why: encoding, colour tags and audio exist only in the file. Test: the delivery lists the
  file, the strip, the cover, the master check output and the measured-only items.

- [invariant] Record what went wrong and what worked after each video. Why: most rules here exist because a
  mistake repeated. Test: the delivery note links a lesson entry. See `learning-loop` (core).

## Procedure

1. Gate: approved plan present; tools present (`ffmpeg -encoders` lists libx264 and libsvtav1, Remotion
   installed, numpy for the audio scripts). If not, stop and say what is missing.
2. Plates and style frames: generate and select plates, build the 4 or 5 style frames, review until pass.
3. Draft voice: local TTS for timing; write the word-timing file; build all scenes bound to it.
4. Review loop on stills and a contact sheet; then a draft render watched as a frame strip.
5. Final voice: check credits, state cost, generate, select by measurement, cut by alignment, check voicing.
6. Sound: synthesise effects, mix with ducking, render.
7. Master: `master-social.sh` and, for websites, `export-web.sh`; run `audio-check.py voice-to-rest` and
   `contact-sheet.py --strict` on the delivered files.
8. Deliver to the owner with strip, cover and the measured-only list; record lessons.

## Traps

- A still looked right while the video flickered: one element animated with a CSS transition.
- A 3D scene rendered as an empty canvas in the headless renderer until ANGLE was enabled.
- A bright light in a 3D scene turned a coloured lamp white through tone mapping; the coloured part needed an
  unlit material.
- A clipped, saturated vibration sound was heard as "broken"; the fix was a modelled motor, not more distortion.
- The voice sat under its own effects; the mix numbers looked moderate, the measurement on the master said
  otherwise.
- One-pass loudness normalisation stopped about 2 LU short of the target on a file with hot peaks.
- Whisper added a closing phrase that was never spoken to the silence at the end of a take; it is a transcript
  artefact, not a fault in the take.
- An image prompt with a film-stock brand name put a film canister on the desk. Brand words leak objects.
- A 10-bit AV1 web file was black in two Chromium-based browsers with GPU decoding and fine in every headless
  test.

## Done when

- The delivered files pass `master-social.sh` or `export-web.sh` checks, `audio-check.py voice-to-rest` and
  `contact-sheet.py --strict`.
- The last review round passed, with pixel-level notes resolved, before the owner saw the video.
- The delivery has file, frame strip, cover, asset ledger with licences, and the list of measured-only items.
- A lesson entry exists for this video.

## References

- [references/build-and-review.md](references/build-and-review.md): load when building scenes, binding the
  timeline, setting motion values or briefing the image reviewer.
- [references/voice.md](references/voice.md): load before generating, choosing or cutting a voice-over.
- [references/sound.md](references/sound.md): load when making effects or mixing.
- [references/plates.md](references/plates.md): load when generating backgrounds or adding depth of field.
- [references/master-and-deliver.md](references/master-and-deliver.md): load when mastering, exporting for the
  web or writing the delivery note.
- [scripts/master-social.sh](scripts/master-social.sh): social master with a pass/fail loudness check.
- [scripts/export-web.sh](scripts/export-web.sh): 8-bit AV1 plus H.264 for a web player.
- [scripts/contact-sheet.py](scripts/contact-sheet.py): contact sheet or frame strip with safe zone and a
  black-cover check.
- [scripts/audio-check.py](scripts/audio-check.py): voice-to-rest on the final mix, and voicing of a word.
- [scripts/synth-sfx.py](scripts/synth-sfx.py): vibration, chime and resolving bed, with level checks.

Run them as `"${CLAUDE_SKILL_DIR}/scripts/[name]" --help`.

## Sources

- https://www.remotion.dev/docs/animating-properties: animate with `useCurrentFrame()`; other animation
  flickers, verified 2026-11-03.
- https://www.remotion.dev/docs/troubleshooting/css-animations: CSS animations do not render correctly,
  verified 2026-11-03.
- https://www.remotion.dev/docs/three-canvas: `width` and `height` are required; animate with
  `useCurrentFrame()`, not `useFrame()`, verified 2026-11-03.
- https://www.remotion.dev/docs/three-webgpu-canvas: `--gl=angle` to avoid an empty canvas in Chrome Headless
  Shell, verified 2026-11-03.
- https://www.remotion.dev/docs/options/color-space: values and defaults; the 5.0 migration notes move the
  default to `bt709`, verified 2026-11-03.
- https://www.remotion.dev/docs/license: free for individuals and teams of up to 3, company licence above,
  verified 2026-11-03.
- https://elevenlabs.io/docs/overview/models: `eleven_v4` is the newest TTS model with a 10,000-character
  limit; `eleven_v3`, `eleven_multilingual_v2`, flash models, verified 2026-11-03.
- https://elevenlabs.io/docs/best-practices/prompting/eleven-v4: audio tags in square brackets; v4 and v3 do
  not support SSML break tags; capitals add emphasis, verified 2026-11-03.
- https://elevenlabs.io/docs/api-reference/text-to-speech/convert: `seed`, `previous_text`, `next_text`,
  request IDs, verified 2026-11-03.
- https://elevenlabs.io/docs/api-reference/user/subscription/get and
  https://elevenlabs.io/docs/api-reference/introduction: credit fields and the `character-cost` header,
  verified 2026-11-03.
- https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_for_multilingual_data_tutorial.html:
  multilingual forced alignment with the MMS aligner; the page carries a deprecation banner for these APIs,
  verified 2026-11-03.
- https://huggingface.co/depth-anything/Depth-Anything-V2-Small-hf (Apache-2.0),
  https://huggingface.co/depth-anything/Depth-Anything-V2-Base-hf (CC-BY-NC-4.0),
  https://huggingface.co/SWivid/F5-TTS (CC-BY-NC-4.0): licences read from the model cards, verified 2026-11-03.
- https://support.google.com/youtube/answer/6039860: upload encoding settings, no loudness target, verified
  2026-11-03.
- https://www.w3.org/TR/WCAG22/: contrast minimum 4.5:1, verified 2026-11-03.
