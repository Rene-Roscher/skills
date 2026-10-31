# XSS sinks

Vue escapes text interpolation and attribute bindings. It does not sanitize HTML you pass to `v-html`, URLs in
`:href` or `:src`, or values in `:style`. Source: https://vuejs.org/guide/best-practices/security.html
(verified 2026-10-31).

## Sinks and what to do

| Sink | Risk | Do |
|---|---|---|
| `v-html`, `innerHTML`, `outerHTML`, `insertAdjacentHTML` | script execution | the shared sanitizer, or no HTML at all |
| `v-html` with a translated string that interpolates data | script execution through the interpolated value | `<i18n-t>` with slots |
| `:href`, `:src`, `window.location` with stored URLs | `javascript:` URLs | allow only `https:`, `mailto:` and relative paths; validate when saving and when rendering |
| `:style` from data | clickjacking, CSS exfiltration | object syntax with an allowlist of properties; colours through a validating helper |
| Markdown or rich text | any of the above | render, then sanitize the rendered HTML |
| Confirmation dialogs | HTML in a message built from entity names | plain text plus a list of substrings to emphasize |

## Markup inside a translation

Do not render `t('invite.body', { name })` through `v-html` to get bold text. Put the markup in the template and
fill the message placeholders through slots of the Translation component:

```vue
<i18n-t keypath="invite.body" tag="p">
  <template #name><strong>{{ org.name }}</strong></template>
</i18n-t>
```

The message stays `"You were invited to {name}"`, and `org.name` is escaped like any other interpolation.
Source: https://vue-i18n.intlify.dev/guide/advanced/component (verified 2026-10-31).

## The shared sanitizer

One composable, used by every remaining `v-html`:

```ts
// composables/useSafeHtml.ts (sketch)
import DOMPurify from 'dompurify'

const ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'code', 'pre', 'h2', 'h3', 'blockquote']
const ALLOWED_ATTR = ['href', 'title']

export function safeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, { ALLOWED_TAGS, ALLOWED_ATTR, ALLOWED_URI_REGEXP: /^(?:https?:|mailto:|\/(?!\/))/i })
}
```

Check the option names against the DOMPurify version in your lockfile. The decision is the explicit allowlist:
no `style` attribute, no `on*` handlers, no `iframe`, no `svg`, URLs limited to safe schemes.

Payload tests for the composable (each must come back without script, handler or `javascript:` URL):

```text
<img src=x onerror=alert(1)>
<a href="javascript:alert(1)">x</a>
<svg onload=alert(1)>
<a href="JaVaScRiPt:alert(1)">x</a>
<iframe src="https://example.com"></iframe>
<p style="background:url(https://example.com/x)">x</p>
```

## Server-rendered public pages

Customer-authored content (descriptions, announcements, profile text) that renders on public pages goes through
the same allowlist on the server before it is stored or before it is rendered, and again on the client if the
client renders it with `v-html`. Two layers, because a change in one path should not open the sink.

## Review checks

- Every `v-html` has a disable comment for `vue/no-v-html` that names `safeHtml` (or another reviewed sanitizer).
- No `v-html` whose expression starts with `t(` or `$t(`.
- No string concatenation of HTML from entity fields anywhere in components or composables.
