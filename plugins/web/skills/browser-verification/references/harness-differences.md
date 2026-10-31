# Harness differences

Where a headless test browser differs from what users run, and how to check those parts.

## Headless Chromium launched by Playwright

When `headless` is set, Playwright adds `--headless`, `--hide-scrollbars`, `--mute-audio` and
`--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4` to
the Chromium launch, and some launch paths add `--enable-unsafe-swiftshader` (software GL). Checked in the
source on the main branch
(https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/chromium/chromium.ts)
and in the published 1.61.1 and 1.64.1 bundles, 2026-10-31. Re-check the locked version in your project when
a result depends on it.

| Behaviour | Headless run | How to check it |
|---|---|---|
| Scrollbar styling | scrollbars hidden | a headed check by the user, or a real-device service; list as not verifiable headless |
| Audio | muted | assert media state (`paused`, `currentTime`) only; audible output is not verifiable headless |
| Hover and pointer media queries | reports hover and a fine pointer | read `matchMedia('(hover: hover)')` and `(pointer: coarse)` in the test; touch-only paths need a device emulation, and the test asserts what the media query returned |
| WebGL, canvas, video decoding | may render through software GL | for video, draw a frame to a canvas and read pixels; a non-black frame proves rendering, an advancing `currentTime` does not |
| Safari | Playwright's WebKit build is not Safari | media codecs, range requests and Safari-only CSS need a real Safari or a device service |

## Emulation that only goes half way

- `colorScheme: 'dark'` (Playwright) or `inDarkMode()` (Pest) sets `prefers-color-scheme`. An app that stores
  the theme in a cookie or `localStorage` ignores it. Set the app's own persistence.
- Browser `locale` changes `navigator.language` and `Accept-Language`. An app that reads the locale from the
  user record ignores it. Set both.
- Device emulation sets viewport, device scale factor and touch. It does not change the engine: a Chromium run
  with an iPhone profile is still Chromium.

## Fonts

CI machines have different system fonts. Text width, line breaks and therefore overflow and fit results depend
on the font. Self-host the web fonts the app uses, wait for them before measuring
(`await page.evaluate(() => document.fonts.ready)`), and do not trust overflow numbers taken with a fallback
font.

## The report line

List every behaviour from the table that the change touches under "Not verified" with the reason, for example:
"Scrollbar styling: scrollbars are hidden in headless Chromium; needs a headed check."
