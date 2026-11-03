## Contents

- Recipes
- Mix
- Checks

## Recipes

`synth-sfx.py` implements the first three; the others follow the same building blocks.

| Sound | Construction |
|---|---|
| Phone vibrating on a desk | An eccentric-mass motor at about 150 Hz with a slight speed wobble and a 60 ms spin-up. The case knocks the desk once per revolution: a sharpened half-wave of the rotation, slightly randomised, drives a bank of modal filters (desk body around 210 and 330 Hz, case rattle around 1.1 and 2.4 kHz, damped), plus a little motor hum. DC removed, high-pass at 70 Hz, low-pass at 4 kHz. No saturation and no clipping. Two pulses of 0.4 s. |
| Notification chime | Two FM-bell notes in quick succession (90 ms apart), short decay, a small room. Your own interval, not a platform's tone. |
| Resolving bed | A low open chord (root, fifth, ninth) with a slow heartbeat pulse under the tension; at the turn it resolves into a major triad an octave higher with more harmonics. |
| Ringtone | Your own melody on FM bells, two bars, repeated. |
| Impact | A sub drop (pitch falling from about 110 to 38 Hz) plus a short thud. |
| Rewind | Band-passed noise with a falling centre frequency and flutter, plus a falling tone. |
| Resolution chime | Four bell notes rising through a major chord, 70 ms apart, with air noise and a longer room. |

Keep the motif of all tonal effects in one key, so the bed, the chime and the ending agree.

## Mix

- Voice first. Effects at 0.3 to 0.5, the bed at 0.3.
- Ducking under speech: effects `volume * (1 - 0.45 * speaking)`, the bed `volume * (1 - 0.5 * speaking)`, where
  `speaking` is 1 during a voice clip and ramps over about 100 ms at its edges. In a frame-driven renderer,
  compute it from the word-timing file like any other animation.
- A bed under an end card can swell after the last word; it never rises during speech.

## Checks

- Per effect: peak below 0 dBFS (the script normalises to -3 dBFS, the bed to -6), no DC offset, and for the
  vibration most of the energy between 100 and 400 Hz.
- On the final file: `audio-check.py voice-to-rest FINAL.mp4 --clip line01.wav --at 0.10 --clip ...` with one
  `--clip`/`--at` pair per spoken line; every line at +4 dB or more. Lines in well-made mixes measured +6 to
  +20 dB.
- Loudness on the master: `master-social.sh` prints and checks it.
- Nobody on the build side can hear the result: the delivery note says which items were measured only, so the
  owner listens to those first.
