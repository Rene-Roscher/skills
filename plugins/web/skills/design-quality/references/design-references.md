# Design references by surface

## Contents

- How to use this file
- Rule: principles, not brands
- Surface to references
- Per company: what is published, strengths, what to take, what not to take
- Companies that publish nothing reusable

Every URL and repository below was opened on 2026-11-03 and returned the content described. A company that
publishes no design system is marked "product only, study the live product". Nothing here is a design system
invented on a company's behalf.

## How to use this file

1. Name the surface type of the work: marketing page, app shell and lists, dashboard or data view, settings,
   billing, form or onboarding, AI chat, command palette, security and trust, charts, states.
2. Pick two or three references for that type from the table. The product's own artifact of the same type stays
   the first reference; the outside ones calibrate it.
3. For each reference, write one line in the plan: which principle it contributes (density, hierarchy, states,
   motion, copy tone) and where it was observed (doc page, open-source component, or live product screen).
4. Measure the result against them the same way as against the product's own artifact: element screenshots at the
   same viewport and theme, plus the computed values the audit reports (body size, row height, number of text
   colours, radius per level). A reference behind a login is compared through its public documentation
   screenshots, a public demo, or the open-source component; say which, and say what could not be captured.
5. If a reference disagrees with WCAG or with the product's tokens, WCAG and the tokens win. Premium products miss
   contrast too.

## Rule: principles, not brands

Study how a reference solves a problem, never copy what makes it recognisable. Take density, hierarchy, state
coverage, motion timing and copy tone. Do not take a brand's logo, wordmark, brand colour, illustrations, icon
set, custom typeface, marketing copy or the exact layout of a signature screen. A page that a buyer could mistake
for the reference has failed, even when every value passes the audit.

Community files that reconstruct a brand's tokens (for example a "Notion design system" token file published by
someone other than Notion) are not references. They are guesses, and they push work toward a clone.

## Surface to references

| Surface | First references | Also useful |
|---|---|---|
| Marketing and landing pages | Vercel, Linear, Stripe, Apple (live sites) | Raycast |
| App shell, navigation, dense lists | Linear, Vercel (Geist), Cloudflare (Kumo) | Raycast |
| Dashboards, data, observability | Grafana (Saga), Sentry, Cloudflare (Kumo charts) | Vercel, Linear |
| Settings and account pages | Stripe, Vercel, Proton | Grafana form templates, 1Password |
| Billing, plans, payment methods, invoices | Stripe, Vercel | Linear |
| Forms and onboarding | Grafana (Saga forms, save, multistep form), Stripe, Apple HIG writing | Adobe Spectrum |
| AI chat and agent UIs | Anthropic (Claude), OpenAI (Apps SDK UI guidelines), Vercel AI Elements | Notion |
| Command palettes, keyboard-first work | Raycast, Linear | Vercel Web Interface Guidelines |
| Security and trust (sign-in, 2FA, recovery, destructive actions) | 1Password, Proton | Grafana "tasteful friction", Kumo delete-resource block |
| Real-time chat, presence, social | Discord | Linear |
| Documents and block editors | Notion | Linear |
| Accessibility and component behaviour | Adobe Spectrum (React Aria), Apple HIG | Vercel Web Interface Guidelines |
| Charts | Apple HIG charts, Grafana, Kumo charts | Sentry |
| Empty, loading and error states | Grafana empty-state pattern, Sentry design tenets | Raycast store guidelines |

## Per company

### Vercel (Geist, Web Interface Guidelines)

- Published: the Geist design system docs (https://vercel.com/geist/introduction), the Geist typeface
  (https://github.com/vercel/geist-font), the Web Interface Guidelines (https://vercel.com/design/guidelines,
  source https://github.com/vercel-labs/web-interface-guidelines), and an agent skill that reviews code against
  them (`web-design-guidelines` in https://github.com/vercel-labs/agent-skills).
- Strongest at: app chrome, dense lists, marketing pages, interaction details (focus, loading, URL state, forms).
- Take: role-based type scale, two or three text greys, radius per elevation, the guideline checklist for states,
  focus and motion.
- Do not take: the black-and-white brand look, the triangle mark, the guideline items Vercel itself calls brand
  choices. Its own site had 8 elements with `transition: all` when measured on 2026-10-31, against its own rule.

### Vercel AI Elements

- Published: a React component registry on shadcn/ui for chat, code, voice and workflow UIs
  (https://elements.ai-sdk.dev, https://github.com/vercel/ai-elements), with an agent skill in the repository.
  The README says the project will be deprecated at the end of November 2026 and replaced by AI Elements in
  shadcn/ui (https://ui.shadcn.com/docs/ai-elements).
- Strongest at: AI chat anatomy: conversation, message, prompt input, reasoning, tool call, sources, inline
  citation, confirmation, plan, queue.
- Take: the list of parts a chat surface needs and the states each part has while streaming.
- Do not take: the component code into a non-React stack, or a dependency on the deprecated registry for new work.

### Linear

- Published: product only, plus design essays: https://linear.app/now/how-we-redesigned-the-linear-ui
  (2024-03-28), https://linear.app/now/behind-the-latest-design-refresh (2026-03-12),
  https://linear.app/now/invisible-details (2020-09-17, sub-menu safe areas). No public design system or
  component library.
- Strongest at: dense app screens, receding chrome, keyboard-first flows, contextual menus, marketing pages that
  show the product.
- Take: themes from base colour, accent and contrast; fewer dividers and smaller icons; a sidebar a few notches
  dimmer than the work area; speed as a design goal.
- Do not take: the dark-only marketing look, the glow treatments, or the low-contrast 12 px metadata in its
  product mock-ups (about 3.4:1, measured on 2026-10-31).

### Stripe

- Published: Stripe Apps design guidance (https://docs.stripe.com/stripe-apps/design), UI components
  (https://docs.stripe.com/stripe-apps/components) and patterns (https://docs.stripe.com/stripe-apps/patterns);
  the essay "Designing accessible color systems" (https://stripe.com/blog/accessible-color-systems, 2019-10-15).
  The Dashboard's own design system is not public.
- Strongest at: settings and billing surfaces, payment forms, marketing pages with real product UI, accessible
  colour scales.
- Take: separate view types for context, focused tasks and settings; custom styling limited on purpose so
  contrast holds; colour levels built in a perceptual colour space so a fixed level gap guarantees contrast.
- Do not take: the animated gradient hero, the brand purple, or its text colour count (33 distinct on the
  marketing site, measured on 2026-10-31).

### Cloudflare (Kumo)

- Published: Kumo, Cloudflare's React component library on Base UI, with charts, blocks and a design skill
  (https://kumo-ui.com, https://github.com/cloudflare/kumo, skill at `skills/kumo-design`).
- Strongest at: dense product dashboards, resource lists, destructive flows (a delete-resource block), charts.
- Take: 14 px content text with larger sizes only for headings, sentence-case headings, no bold weights,
  concentric radii, no border plus drop shadow on the same element, dialogs that are always mounted.
- Do not take: Kumo's component API outside a Kumo project, or Cloudflare's orange.

### Grafana (Saga)

- Published: the Saga design system (https://grafana.com/developers/saga/about/overview) with design principles,
  voice and tone, accessibility, patterns (empty state, forms, save, navigation, alert) and page templates (list,
  table, grid, form, multistep form); components live in `packages/grafana-ui` of
  https://github.com/grafana/grafana.
- Strongest at: data and observability views, forms, empty states, page templates.
- Take: "UI friction should match the severity and risk of the user's action"; three empty-state kinds
  (call to action, not found, completed); list and form page templates as a checklist.
- Do not take: panel chrome from monitoring dashboards into settings or billing screens.

### Sentry

- Published: frontend design tenets (https://develop.sentry.dev/frontend/design-tenets/) and the open-source app
  (https://github.com/getsentry/sentry). Its in-repository design-system skill targets Sentry's own codebase and
  is not reusable elsewhere.
- Strongest at: error and issue detail views, stack traces, observability lists.
- Take: disable and explain instead of hiding; navigation that changes visible data goes in the URL; placeholders
  instead of spinners, spinners only for content of unknown height; keep content between navigations.
- Do not take: the brand purple or its illustrations.

### 1Password

- Published: product only, study the live product. Its design system is internal; the developer site
  (https://developer.1password.com) covers the CLI and SDKs, not design.
- Strongest at: security and trust: sign-in, unlock, recovery, sharing, permission prompts, warnings that do
  not alarm.
- Study in the live product: how risky states are worded, how many actions a security prompt offers, and when
  recovery is explained. These are observations to make, not published rules.
- Do not take: anything visual; there is no published token or component to calibrate against.

### Proton

- Published: the web clients as open source (https://github.com/ProtonMail/WebClients) and a public Storybook of
  their design system (https://design-system.protontech.ch).
- Strongest at: privacy and trust UX in settings, account recovery, encryption and key states.
- Take: how settings group dangerous options, how recovery and verification are explained, the CSS utilities and
  component states as a reference for coverage.
- Do not take: Proton's brand colour, logos or illustrations, or its components into another product.

### Anthropic

- Published: the `frontend-design` skill (https://github.com/anthropics/skills, `skills/frontend-design`, also
  the `frontend-design` plugin in the official Claude Code marketplace) and the essay on generic generated design
  (https://claude.com/blog/improving-frontend-design-through-skills). The Claude web UI is product only, study the
  live product.
- Strongest at: avoiding generated-template looks; for the Claude UI, AI chat: streaming, long answers,
  attachments, artifacts beside the conversation.
- Take: from the skill, boldness spent in one place and calls to action that say what happens. From the live
  product, study how long answers, streaming text and side-by-side artifacts are laid out.
- Do not take: Claude's typefaces, colours or mark. In an existing product, the product's own artifact outranks
  the skill's push toward a new aesthetic direction.

### OpenAI

- Published: UI guidelines for apps inside ChatGPT (https://developers.openai.com/plugins/concepts/ui-guidelines;
  the older `apps-sdk` path redirects there) and a component library with Tailwind foundations and tokens
  (https://github.com/openai/apps-sdk-ui, docs https://openai.github.io/apps-sdk-ui/).
- Strongest at: UI embedded in a chat: inline cards, carousels, fullscreen, picture-in-picture.
- Take: use cards and fullscreen only "when visual interaction improves the workflow"; "No nested scrolling";
  WCAG AA contrast inside embedded views.
- Do not take: ChatGPT-specific rules (such as leaving the logo out of a response) into a standalone product.

### Notion

- Published: product only, study the live product. Its blog covers engineering and AI, not a design system.
- Strongest at: documents and block editors, slash menus, inline database views, calm empty pages.
- Study in the live product: where controls appear (on hover, after a slash) and how much chrome an empty page
  shows. These are observations to make, not published rules.
- Do not take: third-party "Notion design system" token files (see the rule above).

### Discord

- Published: design guidelines for building on Discord, not for your own app: Social SDK guidelines with
  principles (https://docs.discord.com/developers/discord-social-sdk/design-guidelines) and Activities design
  patterns (https://docs.discord.com/developers/activities/design-patterns); brand assets at
  https://discord.com/branding. For your own chat UI: product only, study the live product.
- Strongest at: real-time chat, presence, unread state, notification settings.
- Take: the Social SDK principle "Uphold data privacy, transparency, and control" for presence and sharing
  settings. Study in the live product how unread and mention states stay distinct.
- Do not take: Blurple, the mascot or the brand illustrations.

### Apple (Human Interface Guidelines)

- Published: https://developer.apple.com/design/human-interface-guidelines, including writing, accessibility and
  charts pages.
- Strongest at: accessibility, writing (voice and tone per context), charts, platform conventions.
- Take: an accessible interface is intuitive, perceivable and adaptable; a voice defined once and a tone matched
  to the situation; charts that highlight a few key values.
- Do not take: platform controls, system materials and system icons onto the web, where they do not belong. For
  marketing pages, apple.com is product only: study its pacing and photography, not its look.

### Raycast

- Published: developer docs with store guidelines (https://developers.raycast.com/basics/prepare-an-extension-for-store)
  and the extension repository (https://github.com/raycast/extensions). The app's own design system is not
  public.
- Strongest at: command palettes, action panels, keyboard-first lists.
- Take: never render an empty list before the data arrives; one place for configuration (preferences, not a
  separate command); subtitles only when they add context.
- Do not take: title-case action labels into a product that uses sentence case; it follows the Apple Style Guide
  for Raycast's platform.

### Adobe (Spectrum)

- Published: the Spectrum design system (https://spectrum.adobe.com), React Spectrum and React Aria
  (https://github.com/adobe/react-spectrum, https://react-aria.adobe.com), Spectrum Web Components
  (https://github.com/adobe/spectrum-web-components) and design data with tokens
  (https://github.com/adobe/spectrum-design-data).
- Strongest at: accessibility and component behaviour: keyboard models, focus management, internationalised
  inputs, date and number fields.
- Take: React Aria's behaviour as the bar for any hand-built component; Spectrum's principle "Focused: delivers
  what's needed, when it's needed".
- Do not take: Spectrum's visual style for a product that is not a creative tool.

## Companies that publish nothing reusable

- 1Password: product only.
- Notion: product only.
- Linear: product only, plus design essays.
- Anthropic's Claude UI: product only (the `frontend-design` skill is published).
- Discord: guidelines cover building on Discord only; its own chat UI is product only.
- Raycast and Stripe: guidelines cover building on their platforms; their own app design systems are not public.
