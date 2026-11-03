# AI discoverability

## Contents

- What Google says about AI features
- Crawler tokens by purpose
- Where assistants get their results
- IndexNow
- llms.txt
- Entity consistency and third-party confirmation
- Measuring AI visibility

## What Google says about AI features

- No additional requirements to appear in AI Overviews or AI Mode: the page must be indexed and eligible for a
  snippet. No new machine-readable files, AI text files or special schema.org markup are needed.
- No need to split content into chunks or rewrite it for AI. Write non-commodity content with a point of view.
- AI feature traffic is counted in Search Console's Performance report under the "Web" search type.
- To limit what is shown: snippet controls (`nosnippet`, `data-nosnippet`, `max-snippet`, `noindex`) or the
  site-level control for generative AI features in Search Console. Blocking Googlebot removes the site from
  Search as well.

Sources: https://developers.google.com/search/docs/appearance/ai-features,
https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (verified 2026-11-03). The
site-level control is listed at https://developers.google.com/search/docs/crawling-indexing/control-what-you-share
(not re-read for this skill).

## Crawler tokens by purpose

| Token | Vendor | Purpose | Blocking it |
|---|---|---|---|
| `GPTBot` | OpenAI | training | content not used for training |
| `OAI-SearchBot` | OpenAI | ChatGPT search | not shown in ChatGPT search answers; about 24 h to apply |
| `ChatGPT-User` | OpenAI | fetch on a user's request | robots.txt "may not apply" |
| `ClaudeBot` | Anthropic | training | future content left out of training |
| `Claude-SearchBot` | Anthropic | search index | may reduce visibility in Claude's search results |
| `Claude-User` | Anthropic | fetch on a user's request | may reduce visibility in user-directed search |
| `PerplexityBot` | Perplexity | search index, not training | not surfaced in Perplexity search |
| `Perplexity-User` | Perplexity | fetch on a user's request | "generally ignores robots.txt rules" |
| `Google-Extended` | Google | token only: Gemini training and grounding | no effect on Google Search inclusion or ranking |
| `Applebot-Extended` | Apple | token only: Apple model training, does not crawl | pages stay in Apple search; not a ranking factor |

Sources: https://developers.openai.com/api/docs/bots, https://support.claude.com/en/articles/8896518,
https://docs.perplexity.ai/guides/bots,
https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers,
https://support.apple.com/en-us/119829 (verified 2026-11-03).

Default: allow search and user-fetch agents. Training agents are a business decision recorded once per site in
an ADR. Re-read the vendor pages before relying on a token; vendors add agents.

## Where assistants get their results

- Microsoft Copilot and Bing AI summaries cite pages from Bing; Bing Webmaster Tools shows citations, cited
  pages and sampled grounding queries in its AI Performance report (no clicks, no API mentioned). Source:
  https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
  (verified 2026-11-03).
- ChatGPT search: Bing was a provider at launch; OpenAI has not published the current mix. Secondary source:
  https://www.seroundtable.com/bing-powers-chatgpt-search-38345.html. Unverified on a vendor page.
- Claude web search: Brave Search on Anthropic's subprocessor list since March 2025, with matching results in a
  test. Secondary source: https://simonwillison.net/2025/Mar/21/anthropic-use-brave/. Anthropic's own list was
  not readable for this skill: Unverified on a vendor page.
- Consequence: being indexed in Bing and Brave is hygiene for assistant visibility, not a guarantee.

## IndexNow

- Participants: Bing, Yandex, Seznam, Naver, Yep, Internet Archive, Amazonbot. Google is not one. Source:
  https://www.indexnow.org/searchengines.json (verified 2026-11-03).
- Google has no submission API for ordinary pages; its Indexing API covers job postings and livestream videos
  only. Source: https://developers.google.com/search/apis/indexing-api/v3/quickstart (not re-read for this
  skill).

## llms.txt

- Google Search does not use it; keeping one neither helps nor harms. Source:
  https://developers.google.com/search/updates (2026-06-15 entry) (verified 2026-11-03).
- None of the OpenAI, Anthropic or Perplexity crawler pages above mentions it.
- Reasonable use: a docs site that coding agents are pointed at on purpose. Not a citation or ranking lever.

## Entity consistency and third-party confirmation

- One `Organization` with one `@id` reused across owned sites, `sameAs` listing real profiles (social,
  directories, review platforms), the same logo and the same one-sentence description. Source:
  https://developers.google.com/search/docs/appearance/structured-data/organization (verified 2026-11-03).
- Assistants repeat what third parties say. Outdated directory entries, review-platform profiles and old
  comparison articles describing a former product are corrected at the source (`go-to-market`). This is
  practice, not a vendor statement.
- A brand name that collides with another product needs the disambiguating description and consistent
  `sameAs` more than any markup.

## Measuring AI visibility

Handled by `search-measurement`: Search Console's generative AI report, Bing AI Performance, assistant referrals
in analytics, and a fixed panel of buyer questions run per assistant and language on a date with answers saved.
One run is a sample, not a trend.
