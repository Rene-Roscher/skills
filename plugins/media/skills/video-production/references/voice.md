## Contents

- Provider adapter
- ElevenLabs facts checked 2026-11-03
- Writing the script for the model
- Choosing a take
- Cutting a take
- The unvoiced-word trap
- Draft voices

## Provider adapter

One function per provider: `generate(script, voice, model, settings, seed, context) -> audio, request_id, cost`.
The script file has one paragraph per line, direction tags in front. A second file maps line ids to the
caption text and the exact spoken text (`spoken`, no tags); alignment uses `spoken`, captions use the caption
text. Keep the API key in a file readable only by the user or in the environment, never in the repo or chat.

## ElevenLabs facts checked 2026-11-03

- Models: `eleven_v4` is the newest text-to-speech model, with a 10,000-character limit per request;
  `eleven_v3`, `eleven_multilingual_v2` and flash models remain. Source:
  https://elevenlabs.io/docs/overview/models
- Direction: audio tags in square brackets (for example `[whispers]`), placed before or after the text they
  affect. v4 and v3 do not support SSML break tags; use tags, ellipses and sentence structure for pauses.
  Capitals add emphasis. Source: https://elevenlabs.io/docs/best-practices/prompting/eleven-v4
- Voice settings: which settings a model honours differs per model; read the model's page before setting any.
  The v4 prompting page documents a speed setting from 0.7 to 1.2 (default 1.0).
- Request fields: `seed` (best-effort determinism), `previous_text`, `next_text`, `previous_request_ids`,
  `next_request_ids`. Source: https://elevenlabs.io/docs/api-reference/text-to-speech/convert
- Stitching by request IDs is not available for `eleven_v3`; at most 3 IDs, no older than two hours. Source:
  https://elevenlabs.io/docs/eleven-api/guides/how-to/text-to-speech/request-stitching
- Credits: `GET /v1/user/subscription` returns `character_count` and `character_limit`; each generation
  returns its cost in the `character-cost` header. Sources:
  https://elevenlabs.io/docs/api-reference/user/subscription/get,
  https://elevenlabs.io/docs/api-reference/introduction
- Licence: the pricing page lists a commercial licence from the Starter plan up. Source:
  https://elevenlabs.io/pricing

## Writing the script for the model

- Tags describe the voice (`[tense]`, `[relieved, warm]`, `[short pause]`), in English, never sounds. A tag
  that names a sound was observed to produce a sound effect instead of a delivery.
- Write product names the way they should be pronounced in plain spelling; phonetic notation in the script
  confused reviewers reading it.
- Pauses come from punctuation and line breaks. Capitals for one word per line at most.

## Choosing a take

Generate two seeds of the whole script and compare:

| Measure | How | Use |
|---|---|---|
| Word error rate | Whisper large-v3-turbo transcript against `spoken`, tags removed, normalised to lowercase words | Above a few percent: listen to the lines that differ |
| Naturalness | a MOS predictor such as UTMOS (https://github.com/tarepan/SpeechMOS) | Compare takes of the same voice only; absolute values vary by voice |
| Pace | words per minute and total length against the plan | The bound timeline absorbs small differences; large ones change the cut |
| Voicing of critical words | `audio-check.py voicing` | See below |

Whisper sometimes adds a closing phrase into trailing silence; ignore it when it is not in the audio.

## Cutting a take

1. Normalise the whole take once (one gain, for example to -18 LUFS) so all clips share a level.
2. Force-align the exact spoken text against the take with a CTC aligner (for example the MMS aligner in
   torchaudio: https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_for_multilingual_data_tutorial.html;
   its page carries a deprecation banner, so check the installed version and pin it).
3. For each line boundary, find the quietest RMS frame between the previous line's last letter and this line's
   first letter. Cut there. Limit the pre-roll to about 0.35 s and the tail to about 0.45 s.
4. Apply 8 ms fades at both ends. Do not insert silence; gaps in the timeline are filled by the take's own room
   tone or by the bed.
5. Write one clip per line and the word-timing file (word times relative to each clip).

Whisper word timestamps are not used for cutting: they drift and clip word endings.

## The unvoiced-word trap

A single word on its own line (an exclamation, a one-word reaction) came out unvoiced, as a whisper, on one
voice, whatever the tags said. Embed the word in a sentence ("Oh no. Not again.") and measure:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/audio-check.py" voicing take.mp3 --from 4.20 --to 4.75
```

The check counts frames with a cepstral peak above 6 in the 80 to 250 Hz pitch range. Measured on that voice:
20 to 40 % voiced frames for normally spoken words, 0 to 2 % for whispered ones. The default threshold is 10 %.
For a second opinion, render a spectrogram (0 to 2.5 kHz) and ask the image reviewer whether it shows
horizontal harmonics or only noise.

## Draft voices

Use a local model with a licence that allows commercial use, even for drafts, so a draft that ends up in a
release is not a problem: for example Kokoro-82M (Apache-2.0, https://huggingface.co/hexgrad/Kokoro-82M).
Read the model card before each new model; some popular open TTS weights are CC-BY-NC-4.0.
