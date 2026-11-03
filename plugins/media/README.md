# media

Short product and explainer videos for social platforms and websites: what to decide and get approved before
anything renders, and how to build, voice, mix, master and deliver the result with checks that measure instead
of guessing. The skills are written for an agent that cannot see or hear its own output.

## Skills

| Skill | Use it when |
|---|---|
| `video-planning` | asked for a video, reel, short, TikTok or product film: briefing, platform specs, sourced claims, story, captions, look via style frames, timing table, posting package and AI labels |
| `video-production` | building, voicing, mixing, mastering or exporting an approved plan, or fixing one after review |

Claude Code loads a skill when the task matches its description. `video-production` also loads when you work
in a project with a `remotion.config.*` file. You can call one directly, for example `/media:video-planning`.

`video-production` ships five scripts: a two-pass loudness master for social platforms, an 8-bit AV1 plus
H.264 web export, a contact sheet with safe zone and black-cover check, a voice-to-rest and voicing check, and
a sound-effect synthesiser. They need ffmpeg; the two audio scripts also need numpy.

## Install

```text
/plugin marketplace add Rene-Roscher/skills
/plugin install media@rene-roscher-skills
```

The plugin depends on `core` from this marketplace, which is installed with it. The skills refer to
`evidence-before-claims`, `agent-delegation` and `learning-loop` from `core`, and to `eu-de-legal-baseline`
from `saas` for the AI Act transparency duty.

## How rules are tagged

Each rule is tagged `[invariant]` (never deviate; it carries a test) or `[default]` (deviate only with an ADR that
names the trade-off).

See [CHANGELOG.md](CHANGELOG.md) for changes.
