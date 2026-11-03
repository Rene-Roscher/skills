## Contents

- Platform facts checked 2026-11-03
- AI-content labels
- Package template

## Platform facts checked 2026-11-03

Re-check each line before relying on it. "Unverified" means no official page was found.

| Fact | Value | Source |
|---|---|---|
| TikTok ad format | 9:16 recommended, at least 540 x 960; non-Spark ads up to 10 minutes | https://ads.tiktok.com/help/article/video-ads-specifications?lang=en |
| TikTok ad safe zone | depends on dimension and caption length; download the safe-zone files from the same page | same page |
| TikTok organic safe zone | unverified, no official numbers found; take the box from a screenshot of the current app UI at 1080 x 1920 and write down how it was measured | none |
| TikTok business accounts | only see the Commercial Music Library when adding sound | https://ads.tiktok.com/resources/help/article/how-to-use-the-commercial-music-library?lang=en |
| Reels ads safe zone | keep about 14 % top, 35 % bottom, 6 % each side free of text and logos; 9:16 | https://www.facebook.com/business/ads-guide/update/image/instagram-reels |
| Reels organic specs | unverified (the help page did not render for checking) | https://help.instagram.com/1038071743007909 |
| Instagram hashtags | reported limit of 5 per post; trade press quoting Instagram, no help page found | https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/ |
| YouTube Shorts length | up to 3 minutes, square or vertical | https://support.google.com/youtube/answer/15424877 |
| YouTube Shorts links | URLs in Shorts descriptions and comments are not clickable | https://support.google.com/youtube/answer/13748639 |
| Loudness targets | unverified for all three: no platform publishes a LUFS target on the pages checked; YouTube's encoding page lists codec, sample rate and bitrate only | https://support.google.com/youtube/answer/6039860 |

Consequences for the package: put links in the profile on all three vertical platforms and say so ("link in
profile"); tag every link with UTM parameters naming the platform; use the video's own sound, not trending
tracks, when posting from a business account; keep to five hashtags or fewer.

## AI-content labels

| Platform | When a label is required | Source |
|---|---|---|
| YouTube | realistic content made or altered with AI: a real person saying something they did not, altered footage of a real place or event, a realistic scene that did not happen. Not required for clearly unrealistic content, minor aesthetic edits, or AI help with script, captions or thumbnail. A synthetic narrator voice is not addressed directly. | https://support.google.com/youtube/answer/14328491 |
| TikTok | AI-generated or significantly edited content that shows realistic-looking scenes or people; unlabelled content may be removed, restricted or labelled by TikTok | https://www.tiktok.com/community-guidelines/en-GB/integrity-authenticity?cgversion=2025H2update |
| Instagram and Facebook | photorealistic video or realistic-sounding audio that was digitally created or altered must use the disclosure tool | https://about.fb.com/news/2026/02/meta-prepares-for-2026-us-midterms/ (announcement; the help page did not render) |
| EU law | deep fakes (AI content resembling real persons, objects, places or events that would falsely appear authentic) must be disclosed by the deployer, Art. 50(4) AI Act. Review-ready draft, not legal advice; scope EU. | https://eur-lex.europa.eu/eli/reg/2024/1689/oj |

Default decision: when the voice or a realistic background plate is generated, switch the platform's AI label
on. A photorealistic generated room is a "realistic scene that did not happen" on a strict reading, and the
label costs nothing.

## Package template

```markdown
### [Platform]
Description: [hook question], [one or two sentences with the benefit and one sourced number], [call to action
that fits the platform, e.g. "link in profile"]
Hashtags (5 at most): #[topic] #[audience] #[product category]
Link: https://example.com/?utm_source=[platform]&utm_medium=social&utm_campaign=[slug]
Cover: frame 0 (or the frame named here, with its timestamp)
Sound: original audio of the video
AI label: on / off, because [rule and URL, date]
Pinned first comment: [a question to the audience]
Posting: [date and time]; platforms a day or two apart so each can be measured on its own
```
