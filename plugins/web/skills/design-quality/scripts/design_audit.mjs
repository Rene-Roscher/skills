#!/usr/bin/env node
// Design audit: contrast, token, spacing, radius, shadow, z-index, target-size, overflow, motion, glyph, cascade-layer
// and template-tell checks.
//
// Usage (run from the project directory so the project's Playwright is found):
//   node design_audit.mjs --url http://localhost:3000/billing [--tokens tokens.json] [--scheme dark]
//        [--reduced-motion] [--viewport 1440x900] [--marketing]
//   node design_audit.mjs --self-test
//
// Output: JSON on stdout, a one-line summary on stderr.
// Exit codes: 0 no fail finding, 1 at least one fail finding, 2 usage error or Playwright/Chromium missing.
// Level meaning: fail = a threshold or a closed token set is broken; warn = a tell or a judgement call to fix or justify.
// Playwright is not bundled. It is loaded from the current project; nothing is installed or downloaded.
// Pure functions below (contrast, audits, tell lint) need no browser; --self-test runs them first.

import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

export const THRESHOLDS = { text: 4.5, large: 3, targetPx: 24, overflowPx: 1, topSizeShare: 0.6, displayPx: 32 };

// ---------- colour and contrast (WCAG 2.2 formulas, no rounding) ----------

export function parseColor(input) {
  const s = String(input).trim().toLowerCase();
  let m = s.match(/^#([0-9a-f]{3,8})$/);
  if (m) {
    let h = m[1];
    if (h.length === 3 || h.length === 4) h = [...h].map((c) => c + c).join('');
    if (h.length !== 6 && h.length !== 8) return null;
    const n = (i) => parseInt(h.slice(i, i + 2), 16);
    return [n(0), n(2), n(4), h.length === 8 ? n(6) / 255 : 1];
  }
  m = s.match(/^rgba?\(([^)]+)\)$/);
  if (m) {
    const p = m[1].split(/[\s,/]+/).filter(Boolean);
    if (p.length < 3) return null;
    const ch = (v) => (v.endsWith('%') ? (parseFloat(v) / 100) * 255 : parseFloat(v));
    const a = p[3] === undefined ? 1 : p[3].endsWith('%') ? parseFloat(p[3]) / 100 : parseFloat(p[3]);
    const out = [ch(p[0]), ch(p[1]), ch(p[2]), a];
    return out.some((v) => Number.isNaN(v)) ? null : out;
  }
  return null;
}

const lin = (v) => ((v /= 255) <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
export const luminance = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);

export function contrastRatio(a, b) {
  const x = luminance(a);
  const y = luminance(b);
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}

// Composite colour t (with alpha) over an opaque or translucent backdrop b.
export function over(t, b) {
  const ta = t[3] ?? 1;
  const ba = b[3] ?? 1;
  const a = ta + ba * (1 - ta);
  if (a === 0) return [0, 0, 0, 0];
  return [0, 1, 2].map((i) => (t[i] * ta + b[i] * ba * (1 - ta)) / a).concat(a);
}

// Large text per WCAG 1.4.3: 18 pt (24 px) or 14 pt (about 18.5 px) bold.
export const isLarge = (px, weight) => px >= 24 || (px >= 18.5 && Number(weight) >= 700);

// Never rounds up: 4.499 prints as 4.49, so a printed number cannot look like a pass.
export const fmt = (x) => (Math.floor(x * 100) / 100).toFixed(2);

export function textContrast({ fg, bg, fontSize, fontWeight }) {
  const backdrop = bg[3] < 1 ? over(bg, [255, 255, 255, 1]) : bg;
  const ratio = contrastRatio(over(fg, backdrop), backdrop);
  const need = isLarge(fontSize, fontWeight) ? THRESHOLDS.large : THRESHOLDS.text;
  return { ratio, need, pass: ratio >= need };
}

function hueSat([r, g, b]) {
  const [R, G, B] = [r, g, b].map((v) => v / 255);
  const mx = Math.max(R, G, B);
  const mn = Math.min(R, G, B);
  const d = mx - mn;
  if (d === 0) return { h: 0, s: 0 };
  const l = (mx + mn) / 2;
  const s = d / (1 - Math.abs(2 * l - 1));
  let h = mx === R ? ((G - B) / d) % 6 : mx === G ? (B - R) / d + 2 : (R - G) / d + 4;
  h = (h * 60 + 360) % 360;
  return { h, s };
}

// ---------- pure audits over collected records ----------

export function auditContrast(records) {
  const findings = [];
  let checked = 0;
  let unknown = 0;
  for (const r of records) {
    if (!r.hasText || !r.color) continue;
    if (r.bgUnknown || r.clipText) { unknown++; continue; }
    checked++;
    const c = textContrast({ fg: r.color, bg: r.bg, fontSize: r.fontSize, fontWeight: r.fontWeight });
    if (!c.pass) {
      findings.push({ level: 'fail', id: 'contrast', selector: r.sel, message: `${fmt(c.ratio)}:1, needs ${c.need}:1 (${r.fontSize}px, weight ${r.fontWeight})`, value: c.ratio });
    }
  }
  if (unknown) findings.push({ level: 'warn', id: 'contrast-unknown-background', selector: '*', message: `${unknown} text element(s) over a gradient, image or clipped text were not measured; sample pixels or check by hand`, value: unknown });
  return { findings, checked, unknown };
}

export function auditTokens(records, tokens) {
  const findings = [];
  const seen = new Map();
  const add = (kind, value, sel) => {
    const k = `${kind}:${value}`;
    if (!seen.has(k)) { seen.set(k, true); findings.push({ level: 'fail', id: `off-token-${kind}`, selector: sel, message: `${kind} ${value} is not in the token list`, value }); }
  };
  const num = (v) => Math.round(v * 100) / 100;
  const inList = (list, v) => list.some((t) => Math.abs(t - v) < 0.01);
  for (const r of records) {
    if (tokens.fontSizes && r.hasText && !inList(tokens.fontSizes, r.fontSize)) add('fontSize', `${num(r.fontSize)}px`, r.sel);
    if (tokens.fontWeights && r.hasText && !tokens.fontWeights.map(Number).includes(Number(r.fontWeight))) add('fontWeight', r.fontWeight, r.sel);
    if (tokens.fontFamilies && r.hasText) {
      const first = String(r.fontFamily).split(',')[0].replace(/["']/g, '').trim().toLowerCase();
      if (!tokens.fontFamilies.map((f) => f.toLowerCase()).includes(first)) add('fontFamily', first, r.sel);
    }
    if (tokens.spacing) for (const v of r.spacing || []) if (v !== 0 && !inList(tokens.spacing, v)) add('spacing', `${num(v)}px`, r.sel);
    if (tokens.radii) for (const v of r.radius || []) if (v !== 0 && v < 999 && !inList(tokens.radii, v)) add('radius', `${num(v)}px`, r.sel);
    if (tokens.shadows && r.shadow && r.shadow !== 'none' && !tokens.shadows.includes(r.shadow)) add('shadow', r.shadow, r.sel);
    if (tokens.colors && r.hasText && r.color && !tokens.colors.some((c) => sameColor(c, r.color))) add('textColor', rgbString(r.color), r.sel);
    if (tokens.zIndex && r.zIndex != null && r.zIndex !== 0 && !tokens.zIndex.map(Number).includes(r.zIndex)) add('zIndex', r.zIndex, r.sel);
  }
  return findings;
}

const sameColor = (a, b) => a.slice(0, 3).every((v, i) => Math.abs(v - b[i]) < 1) && Math.abs((a[3] ?? 1) - (b[3] ?? 1)) < 0.01;
const rgbString = (c) => `rgb(${c.slice(0, 3).map(Math.round).join(', ')}${(c[3] ?? 1) < 1 ? ` / ${(+c[3].toFixed(2))}` : ''})`;

export function spacingAudit(values, scale) {
  const off = [...new Set(values.filter((v) => v !== 0 && !scale.some((s) => Math.abs(s - v) < 0.01)))].sort((a, b) => a - b);
  const nonZero = values.filter((v) => v !== 0).length;
  const inScale = nonZero === 0 ? 1 : (nonZero - values.filter((v) => v !== 0 && off.includes(v)).length) / nonZero;
  return { off, share: inScale };
}

export function typeHistogram(records) {
  const counts = {};
  let total = 0;
  for (const r of records) if (r.hasText) { const k = `${Math.round(r.fontSize * 100) / 100}px`; counts[k] = (counts[k] || 0) + 1; total++; }
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const top3 = sorted.slice(0, 3).reduce((n, [, c]) => n + c, 0);
  return { counts, total, distinct: sorted.length, topThreeShare: total ? top3 / total : 1 };
}

export function auditType(records) {
  const findings = [];
  const h = typeHistogram(records);
  if (h.distinct > 5 && h.topThreeShare < THRESHOLDS.topSizeShare) {
    findings.push({ level: 'warn', id: 'type-scatter', selector: '*', message: `top three sizes cover ${Math.round(h.topThreeShare * 100)}% of ${h.total} text elements across ${h.distinct} sizes (measured premium sites: 68% to 94%)`, value: h.topThreeShare });
  }
  for (const r of records) {
    if (!r.hasText || r.fontSize < THRESHOLDS.displayPx) continue;
    const ratio = r.lineHeight == null ? 1.2 : r.lineHeight / r.fontSize;
    if (Math.abs(r.letterSpacing) < 0.01 && ratio >= 1.2) {
      findings.push({ level: 'warn', id: 'untuned-display', selector: r.sel, message: `${r.fontSize}px text with tracking 0 and line height ${ratio.toFixed(2)}: set line height 1.0 to 1.2 and negative tracking`, value: ratio });
    }
  }
  for (const r of records) {
    if (r.numericCell && !r.tabular) findings.push({ level: 'warn', id: 'tabular-nums', selector: r.sel, message: 'numeric table cell without font-variant-numeric: tabular-nums', value: r.text });
  }
  return { findings, histogram: h };
}

// Count shadow layers outside parentheses: "rgba(0, 0, 0, .1) 0 1px 2px, rgba(0,0,0,.1) 0 4px 8px" -> 2.
export function shadowLayers(value) {
  if (!value || value === 'none') return 0;
  let depth = 0;
  let n = 1;
  for (const ch of value) { if (ch === '(') depth++; else if (ch === ')') depth--; else if (ch === ',' && depth === 0) n++; }
  return n;
}

export function auditShapes(records) {
  const findings = [];
  const radiusCounts = {};
  let rounded = 0;
  records.forEach((r) => {
    const rad = r.radius && r.radius.length ? Math.max(...r.radius) : 0;
    if (rad > 0 && rad < 999) { rounded++; radiusCounts[`${Math.round(rad * 100) / 100}px`] = (radiusCounts[`${Math.round(rad * 100) / 100}px`] || 0) + 1; }
    if (rad > 0 && rad < 999 && r.parentRadiusIdx != null) {
      const p = records[r.parentRadiusIdx];
      const prad = Math.max(...p.radius);
      if (prad < 999 && rad > prad + 0.01) findings.push({ level: 'fail', id: 'nested-radius', selector: r.sel, message: `child radius ${rad}px is larger than parent radius ${prad}px`, value: rad });
    }
  });
  const top = Object.entries(radiusCounts).sort((a, b) => b[1] - a[1])[0];
  if (rounded >= 6 && top && top[1] / rounded > 0.8 && Object.keys(radiusCounts).length === 1) {
    findings.push({ level: 'warn', id: 'tell-one-radius', selector: '*', message: `one radius (${top[0]}) on all ${rounded} rounded surfaces; radius should follow elevation (T6)`, value: rounded });
  }
  const shadowCounts = {};
  const byParent = new Map();
  for (const r of records) {
    if (!r.shadow || r.shadow === 'none') continue;
    shadowCounts[r.shadow] = (shadowCounts[r.shadow] || 0) + 1;
    if (shadowLayers(r.shadow) < 2 && r.parentKey != null) {
      const k = `${r.parentKey}|${r.shadow}`;
      byParent.set(k, [...(byParent.get(k) || []), r.sel]);
    }
  }
  for (const [k, sels] of byParent) if (sels.length >= 3) findings.push({ level: 'warn', id: 'tell-repeated-shadow', selector: sels[0], message: `one single-layer shadow repeated on ${sels.length} sibling elements (T6): ${k.split('|')[1]}`, value: sels.length });
  return { findings, radii: radiusCounts, shadows: shadowCounts };
}

// WCAG 2.5.8: undersized targets pass when a 24 px circle centred on them touches no other target
// and no circle of another undersized target. Inline targets and user agent controls are exempt.
export function auditTargets(targets) {
  const findings = [];
  const min = THRESHOLDS.targetPx;
  const centre = (t) => ({ x: t.x + t.w / 2, y: t.y + t.h / 2 });
  const under = (t) => (t.w < min || t.h < min) && !t.inline && !t.uaControl;
  const circleHitsRect = (c, t) => {
    const dx = Math.max(t.x - c.x, 0, c.x - (t.x + t.w));
    const dy = Math.max(t.y - c.y, 0, c.y - (t.y + t.h));
    return dx * dx + dy * dy < (min / 2) ** 2;
  };
  targets.forEach((t, i) => {
    if (!under(t)) return;
    const c = centre(t);
    const clash = targets.some((o, j) => {
      if (i === j) return false;
      if (circleHitsRect(c, o)) return true;
      return under(o) && Math.hypot(c.x - centre(o).x, c.y - centre(o).y) < min;
    });
    if (clash) findings.push({ level: 'fail', id: 'target-size', selector: t.sel, message: `${Math.round(t.w)}x${Math.round(t.h)} px target with another target within 24 px; needs 24x24 px or spacing (record equivalent or essential exceptions in the report)`, value: Math.min(t.w, t.h) });
  });
  return findings;
}

// ---------- other audits ----------

export function auditOverflow(list) {
  return list
    .filter((o) => o.scrollWidth > o.clientWidth + THRESHOLDS.overflowPx)
    .map((o) => ({ level: 'fail', id: 'overflow', selector: o.sel, message: `content is ${Math.round(o.scrollWidth - o.clientWidth)} px wider than its box${o.clips ? ' (clipped, not scrollable)' : ''}`, value: o.scrollWidth - o.clientWidth }));
}

export function auditMotion(page, { reducedMotion }) {
  const findings = [];
  for (const sel of page.transitionAll || []) findings.push({ level: 'fail', id: 'transition-all', selector: sel, message: 'transition-property all; list the properties (usually opacity and transform)', value: 'all' });
  if (reducedMotion && page.runningAnimations > 0) findings.push({ level: 'fail', id: 'reduced-motion', selector: '*', message: `${page.runningAnimations} animation(s) still running with prefers-reduced-motion: reduce`, value: page.runningAnimations });
  return findings;
}

export function auditMarketing(page, viewportHeight) {
  const findings = [];
  const p = page.productUi;
  if (!p || !p.visible || p.top > viewportHeight * 1.3) {
    findings.push({ level: 'fail', id: 'product-ui', selector: '[data-testid="product-ui"]', message: p ? `product UI starts at ${Math.round(p.top)} px, limit ${Math.round(viewportHeight * 1.3)} px` : 'no element with data-testid="product-ui" on the page', value: p ? p.top : null });
  }
  if (page.heroButtons > 2) findings.push({ level: 'fail', id: 'hero-buttons', selector: 'h1', message: `${page.heroButtons} buttons in the hero, at most 2`, value: page.heroButtons });
  return findings;
}

// ---------- emoji and symbol stand-ins (fail) ----------

// Emoji: default emoji presentation (this includes the regional-indicator letters that form flags), any
// pictograph forced to emoji style (U+FE0F) and keycaps (U+20E3). Text-style symbols such as (c), (tm) and
// arrows inside a sentence are not emoji. Symbol stand-ins: a character doing an icon's job, either alone (a
// star rating, a close cross, an arrow button) or as a status marker in front of a label (a check mark before
// "Paid"). Text inside code or under [data-user-content] is skipped: users may write emoji.
const EMOJI_GLYPH = /\p{Emoji_Presentation}|\p{Extended_Pictographic}\uFE0F|\u20E3/u;
const ICON_CHARS = '\u2190-\u21FF\u2713-\u2718\u2605\u2606\u2610-\u2612\u26A0\u2139\u25A0-\u25FF\u00D7\u2715\u2716\u203A\u2039\u00AB\u00BB';
const SYMBOL_ONLY = new RegExp(`^[${ICON_CHARS}\\s]+$`, 'u');
const STATUS_MARK = /^[\u2713-\u2718\u2605\u2606\u2610-\u2612\u26A0\u2139]\s*\S/u;

export function auditGlyphs(records) {
  const f = [];
  for (const r of records) {
    if (!r.text || r.inCode || r.userContent) continue;
    if (EMOJI_GLYPH.test(r.text)) f.push({ level: 'fail', id: 'emoji-glyph', selector: r.sel, message: `emoji in UI text "${r.text.slice(0, 40)}"; use the icon set or an SVG (flags as SVG assets)` });
    else if (SYMBOL_ONLY.test(r.text) || STATUS_MARK.test(r.text)) f.push({ level: 'fail', id: 'symbol-icon', selector: r.sel, message: `character used as an icon "${r.text.slice(0, 40)}"; use the icon set or an SVG` });
  }
  const seen = new Set();
  return f.filter((x) => { const k = `${x.id}|${x.selector}`; if (seen.has(k)) return false; seen.add(k); return true; });
}

// ---------- cascade layers (warning) ----------

// Normal declarations outside any @layer beat every layered declaration, whatever the specificity. On a page
// that uses layers (Tailwind v4 emits theme, base, components, utilities), an unlayered rule overrides the
// utilities; a global focus ring there wins over every focus utility.
export function auditLayers(page) {
  if (!page || !page.usesLayers || !page.unlayered || page.unlayered.length === 0) return [];
  const list = page.unlayered.slice(0, 5).join(', ');
  return [{ level: 'warn', id: 'unlayered-css', selector: page.unlayered[0], message: `${page.unlayered.length} style rule(s) outside @layer override layered utilities: ${list}; move them into @layer base or components, or justify (third-party CSS)`, value: page.unlayered.length }];
}

// ---------- template tells (warnings) ----------

const HEADING = /^h[1-6]$/;
const PLACEHOLDER = /lorem ipsum|\bjohn doe\b|\bjane doe\b|\bacme\b|your text here|\bfoo@bar\b/i;

export function lintTells(records, ctx = {}) {
  const f = [];
  const warn = (id, selector, message) => f.push({ level: 'warn', id, selector, message });
  const texty = records.filter((r) => r.text);
  texty.forEach((r, i) => {
    if (r.upperTracked && !HEADING.test(r.tag)) {
      const next = texty[i + 1];
      if (next && /^h[1-3]$/.test(next.tag)) warn('tell-eyebrow', r.sel, `tracked all-caps label "${r.text.slice(0, 40)}" directly above a heading (T7)`);
    }
    if (HEADING.test(r.tag) && r.accentedWord) warn('tell-accent-word', r.sel, 'one word of the heading is styled differently (T10)');
    if (PLACEHOLDER.test(r.text)) warn('tell-placeholder-data', r.sel, `placeholder text "${r.text.slice(0, 40)}" (T18)`);
  });
  const targets = texty.filter((r) => r.tag === 'a' || r.tag === 'button');
  const arrows = targets.filter((r) => /(→|->|›|»)\s*$/.test(r.text));
  if (arrows.length >= 3 && arrows.length / targets.length >= 0.5) warn('tell-arrow-links', arrows[0].sel, `${arrows.length} of ${targets.length} links and buttons end in an arrow (T8)`);
  const dots = texty.filter((r) => r.text.split(' · ').length >= 3);
  if (dots.length >= 2) warn('tell-middle-dot-meta', dots[0].sel, `${dots.length} meta strings joined with middle dots (T8)`);
  const markers = texty.filter((r) => /^0[1-9]\b/.test(r.text) && r.text.length <= 4);
  if (markers.length >= 3) warn('tell-numbered-markers', markers[0].sel, `${markers.length} markers like "01" (T11); fine only if the content is a sequence`);
  const mono = texty.filter((r) => r.mono && !r.inCode && /[a-z]{3,}/i.test(r.text) && r.text.length <= 40);
  if (mono.length >= 3) warn('tell-mono-labels', mono[0].sel, `${mono.length} short labels set in a monospace face outside code (T9)`);
  const entrances = records.filter((r) => r.animName && r.animName !== 'none');
  if (entrances.length >= 4) warn('tell-entrance-animations', entrances[0].sel, `${entrances.length} elements run a CSS animation on load (T13)`);
  for (const r of records) {
    if (r.clipText && r.text) warn('tell-gradient-text', r.sel, 'background-clip: text (T10)');
    if (r.radialGlow) warn('tell-glow-card', r.sel, 'radial gradient with a wide glow shadow (T15)');
    if (ctx.lightPage !== false && r.bgImage && /gradient/.test(r.bgImage)) {
      const purple = (r.bgImage.match(/#[0-9a-f]{3,8}\b|rgba?\([^)]+\)/gi) || []).map(parseColor).filter(Boolean).some((c) => { const { h, s } = hueSat(c); return h >= 250 && h <= 290 && s >= 0.3; });
      if (purple) warn('tell-purple-gradient', r.sel, 'purple or indigo gradient on a light page (T1)');
    }
  }
  const seen = new Set();
  return f.filter((x) => { const k = `${x.id}|${x.selector}`; if (seen.has(k)) return false; seen.add(k); return true; });
}

// ---------- minimal HTML reader for the browserless path ----------

const VOID = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr']);

function cssRules(html) {
  const rules = [];
  for (const m of html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)) {
    for (const r of m[1].replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/([^{}@]+)\{([^{}]*)\}/g)) {
      const decl = {};
      for (const d of r[2].split(';')) { const i = d.indexOf(':'); if (i > 0) decl[d.slice(0, i).trim().toLowerCase()] = d.slice(i + 1).trim(); }
      for (const sel of r[1].split(',')) rules.push([sel.trim(), decl]);
    }
  }
  return rules;
}

const selMatches = (sel, tag, classes, id) => {
  const m = sel.match(/^([a-z][a-z0-9]*)?((?:\.[\w-]+)*)(#[\w-]+)?$/i);
  if (!m) return false;
  if (m[1] && m[1].toLowerCase() !== tag) return false;
  if (m[3] && m[3].slice(1) !== id) return false;
  return (m[2] ? m[2].split('.').filter(Boolean) : []).every((c) => classes.includes(c));
};

const px = (v) => (v == null ? NaN : v.endsWith('em') ? parseFloat(v) : parseFloat(v));

// Reads tags, classes, inline styles and simple selectors (tag, .class, tag.class, #id). No cascade order, no
// inheritance beyond headings: enough for the built-in samples and for linting small snippets.
export function recordsFromHtml(html) {
  const rules = cssRules(html);
  const body = html.replace(/<(script|style)[\s\S]*?<\/\1>/gi, '').replace(/<!--[\s\S]*?-->/g, '');
  const records = [];
  const stack = [];
  const re = /<(\/?)([a-z][a-z0-9]*)([^>]*)>|([^<]+)/gi;
  let m;
  while ((m = re.exec(body))) {
    if (m[4] !== undefined) {
      const top = stack[stack.length - 1];
      const t = m[4].replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
      if (top && t) { top.rec.text = top.rec.text ? `${top.rec.text} ${t}` : t; top.rec.hasText = true; }
      continue;
    }
    const tag = m[2].toLowerCase();
    if (m[1]) { while (stack.length) { const o = stack.pop(); if (o.tag === tag) break; } continue; }
    const attrs = m[3];
    const classes = ((attrs.match(/class="([^"]*)"/) || [])[1] || '').split(/\s+/).filter(Boolean);
    const id = (attrs.match(/id="([^"]*)"/) || [])[1];
    const decl = {};
    for (const [sel, d] of rules) if (selMatches(sel, tag, classes, id)) Object.assign(decl, d);
    for (const d of ((attrs.match(/style="([^"]*)"/) || [])[1] || '').split(';')) { const i = d.indexOf(':'); if (i > 0) decl[d.slice(0, i).trim().toLowerCase()] = d.slice(i + 1).trim(); }
    const sel = `${tag}${id ? `#${id}` : ''}${classes.map((c) => `.${c}`).join('')}`;
    const ls = px(decl['letter-spacing']);
    const rec = {
      tag, sel, text: '', hasText: false,
      upperTracked: decl['text-transform'] === 'uppercase' && ls > 0,
      mono: /mono/i.test(decl['font-family'] || ''),
      inCode: stack.some((s) => ['code', 'pre', 'kbd', 'samp'].includes(s.tag)) || ['code', 'pre', 'kbd', 'samp'].includes(tag),
      clipText: /text/.test(decl['background-clip'] || decl['-webkit-background-clip'] || ''),
      bgImage: decl['background-image'] || decl.background || '',
      radialGlow: /radial-gradient/.test(decl['background-image'] || decl.background || '') && /\d{2,}px/.test(decl['box-shadow'] || ''),
      transitionAll: /\ball\b/.test(decl.transition || decl['transition-property'] || ''),
      animName: decl['animation-name'] || ((decl.animation || '').split(/\s+/)[0] || 'none'),
      userContent: /\bdata-user-content\b/.test(attrs) || stack.some((x) => x.rec.userContent),
      zIndex: /^-?\d+$/.test(decl['z-index'] || '') ? Number(decl['z-index']) : null,
      _decl: decl,
    };
    const parent = stack[stack.length - 1];
    if (parent && /^h[1-6]$/.test(parent.tag) && !/^h[1-6]$/.test(tag)) {
      if (['em', 'i', 'b', 'strong', 'mark'].includes(tag) || decl.color || rec.clipText) parent.rec.accentedWord = true;
    }
    records.push(rec);
    if (!VOID.has(tag) && !/\/\s*$/.test(attrs)) stack.push({ tag, rec });
  }
  for (const r of records) delete r._decl;
  return records;
}

export function lintHtml(html) {
  const records = recordsFromHtml(html);
  const lightPage = !/<body[^>]*(background(?:-color)?\s*:\s*#(?:0|1)[0-9a-f]{2,5})/i.test(html);
  const findings = lintTells(records, { lightPage });
  findings.push(...auditGlyphs(records));
  for (const r of records) if (r.transitionAll) findings.push({ level: 'fail', id: 'transition-all', selector: r.sel, message: 'transition-property all; list the properties' });
  return findings;
}

// ---------- accent and colour inventory ----------

export function accentUsage(records, accent) {
  const hits = [];
  for (const r of records) {
    const where = [];
    if (r.hasText && r.color && sameColor(accent, r.color)) where.push('text');
    if (r.bgSelf && sameColor(accent, r.bgSelf)) where.push('background');
    if (r.borderColor && sameColor(accent, r.borderColor)) where.push('border');
    if (r.bgImage && /gradient/.test(r.bgImage) && r.bgImage.includes(rgbString(accent).replace(/^rgb\(/, '').split(')')[0].split(' / ')[0])) where.push('gradient');
    if (where.length) hits.push({ selector: r.sel, where });
  }
  return hits;
}

export function textColors(records) {
  const counts = {};
  for (const r of records) if (r.hasText && r.color) { const k = rgbString(r.color); counts[k] = (counts[k] || 0) + 1; }
  return Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([color, count]) => ({ color, count }));
}

// ---------- in-page collector (serialised into the browser) ----------

export function collectInPage(opts) {
  const cv = document.createElement('canvas');
  cv.width = cv.height = 1;
  const c2 = cv.getContext('2d', { willReadFrequently: true });
  const rgba = (col) => {
    const m = String(col).match(/^rgba?\(([^)]+)\)$/);
    if (m) { const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return [p[0], p[1], p[2], p[3] ?? 1]; }
    c2.clearRect(0, 0, 1, 1);
    c2.fillStyle = 'rgb(0, 0, 0)';
    c2.fillStyle = col;
    c2.fillRect(0, 0, 1, 1);
    const d = c2.getImageData(0, 0, 1, 1).data;
    return [d[0], d[1], d[2], d[3] / 255];
  };
  const over = (t, b) => { const a = t[3] + b[3] * (1 - t[3]); return a === 0 ? [0, 0, 0, 0] : [0, 1, 2].map((i) => (t[i] * t[3] + b[i] * b[3] * (1 - t[3])) / a).concat(a); };
  const visible = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const selOf = (el) => {
    const parts = [];
    for (let e = el, n = 0; e && e.nodeType === 1 && n < 3; e = e.parentElement, n++) {
      let p = e.tagName.toLowerCase();
      if (e.id) p += `#${e.id}`;
      else if (typeof e.className === 'string' && e.className.trim()) p += `.${e.className.trim().split(/\s+/).slice(0, 2).join('.')}`;
      parts.unshift(p);
      if (e.id) break;
    }
    return parts.join(' > ');
  };
  const background = (el) => {
    const layers = [];
    let unknown = false;
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage !== 'none') unknown = true;
      const c = rgba(cs.backgroundColor);
      if (c[3] > 0) layers.push(c);
      if (c[3] >= 1) break;
    }
    let col = [255, 255, 255, 1];
    for (let i = layers.length - 1; i >= 0; i--) col = over(layers[i], col);
    return { col, unknown };
  };
  const opacityOf = (el) => { let o = 1; for (let e = el; e; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity); return o; };
  const ownText = (el) => [...el.childNodes].filter((n) => n.nodeType === 3).map((n) => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
  const pxv = (v) => { const n = parseFloat(v); return Number.isFinite(n) ? n : null; };
  const SKIP = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'HEAD', 'META', 'LINK', 'TITLE', 'TEMPLATE', 'SVG', 'PATH']);
  const all = [...document.body.querySelectorAll('*')].filter((e) => !SKIP.has(e.tagName.toUpperCase()) && !e.closest('svg') && visible(e)).slice(0, opts.maxElements);
  const index = new Map(all.map((e, i) => [e, i]));
  const records = all.map((el) => {
    const cs = getComputedStyle(el);
    const tag = el.tagName.toLowerCase();
    const useInner = /^(h[1-6]|a|button)$/.test(tag);
    const text = useInner ? (el.innerText || '').replace(/\s+/g, ' ').trim() : ownText(el);
    const bg = background(el);
    const fg = rgba(cs.color);
    fg[3] *= opacityOf(el);
    const radius = ['borderTopLeftRadius', 'borderTopRightRadius', 'borderBottomRightRadius', 'borderBottomLeftRadius'].map((k) => pxv(cs[k]) || 0);
    let pIdx = null;
    for (let p = el.parentElement; p; p = p.parentElement) { if (index.has(p)) { const pr = ['borderTopLeftRadius', 'borderTopRightRadius', 'borderBottomRightRadius', 'borderBottomLeftRadius'].map((k) => pxv(getComputedStyle(p)[k]) || 0); if (Math.max(...pr) > 0 && getComputedStyle(p).overflow !== 'visible') { pIdx = index.get(p); break; } if (Math.max(...pr) > 0) { pIdx = index.get(p); break; } } }
    const spacing = [];
    for (const k of ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'marginTop', 'marginRight', 'marginBottom', 'marginLeft', 'rowGap', 'columnGap']) { const v = pxv(cs[k]); if (v !== null) spacing.push(Math.abs(Math.round(v * 100) / 100)); }
    const animDur = pxv(cs.animationDuration) || 0;
    const clip = (cs.webkitBackgroundClip || cs.backgroundClip) === 'text';
    let accentedWord = false;
    if (/^h[1-6]$/.test(tag)) {
      for (const ch of el.querySelectorAll('*')) { const k = getComputedStyle(ch); if (k.color !== cs.color || k.fontStyle !== cs.fontStyle || k.fontWeight !== cs.fontWeight || (k.webkitBackgroundClip || k.backgroundClip) === 'text') accentedWord = true; }
    }
    const isCell = tag === 'td' || tag === 'th' || el.getAttribute('role') === 'cell';
    return {
      sel: selOf(el), tag, text, hasText: text.length > 0 && (useInner || ownText(el).length > 0),
      color: fg, bg: bg.col, bgUnknown: bg.unknown && !!text, clipText: clip, bgSelf: rgba(cs.backgroundColor), borderColor: pxv(cs.borderTopWidth) > 0 ? rgba(cs.borderTopColor) : null,
      fontSize: pxv(cs.fontSize), fontWeight: cs.fontWeight, fontFamily: cs.fontFamily,
      lineHeight: cs.lineHeight === 'normal' ? null : pxv(cs.lineHeight), letterSpacing: cs.letterSpacing === 'normal' ? 0 : pxv(cs.letterSpacing) || 0,
      radius, shadow: cs.boxShadow, spacing, parentRadiusIdx: pIdx, parentKey: el.parentElement ? index.get(el.parentElement) ?? null : null,
      upperTracked: cs.textTransform === 'uppercase' && (cs.letterSpacing !== 'normal' && pxv(cs.letterSpacing) > 0),
      mono: /mono|menlo|consolas|courier/i.test(cs.fontFamily), inCode: !!el.closest('code, pre, kbd, samp'),
      userContent: !!el.closest('[data-user-content]'), zIndex: cs.position !== 'static' && /^-?\d+$/.test(cs.zIndex) ? Number(cs.zIndex) : null,
      bgImage: cs.backgroundImage, radialGlow: /radial-gradient/.test(cs.backgroundImage) && /\d{2,}px/.test(cs.boxShadow),
      animName: animDur > 0 ? cs.animationName : 'none', accentedWord,
      numericCell: isCell && /\d/.test(text) && /^[\s$€£+-]*[\d.,\s]+\s*[%A-Za-z]{0,3}$/.test(text),
      tabular: /tabular-nums/.test(cs.fontVariantNumeric) || /tnum/.test(cs.fontFeatureSettings),
    };
  });
  const targets = [...document.querySelectorAll('a[href], button, [role="button"], [role="link"], input:not([type="hidden"]), select, textarea, summary')]
    .filter(visible)
    .map((el) => {
      const r = el.getBoundingClientRect();
      const cs = getComputedStyle(el);
      const p = el.parentElement;
      const inline = cs.display === 'inline' && !!p && [...p.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
      const t = (el.getAttribute('type') || '').toLowerCase();
      return { sel: selOf(el), x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height, inline, uaControl: ['date', 'time', 'range', 'color', 'file', 'datetime-local', 'month', 'week'].includes(t) };
    });
  const overflow = [];
  const doc = document.documentElement;
  overflow.push({ sel: 'html', scrollWidth: doc.scrollWidth, clientWidth: doc.clientWidth, clips: false });
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.overflowX === 'auto' || cs.overflowX === 'scroll') continue;
    if (el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0) overflow.push({ sel: selOf(el), scrollWidth: el.scrollWidth, clientWidth: el.clientWidth, clips: cs.overflowX === 'hidden' || cs.overflowX === 'clip' });
  }
  const transitionAll = all.filter((el) => { const cs = getComputedStyle(el); return cs.transitionProperty.split(',').map((s) => s.trim()).includes('all') && cs.transitionDuration.split(',').some((d) => parseFloat(d) > 0); }).map(selOf);
  const running = document.getAnimations().filter((a) => a.playState === 'running').length;
  const pu = document.querySelector('[data-testid="product-ui"]');
  const h1 = document.querySelector('h1');
  const hero = h1 ? h1.closest('section, header, [data-hero]') || h1.parentElement : null;
  const heroButtons = hero ? [...hero.querySelectorAll('button, [role="button"], a[data-cta]')].filter(visible).length : 0;
  const spacingValues = records.flatMap((r) => r.spacing);
  let usesLayers = false;
  const unlayered = [];
  const walk = (rules, inLayer) => {
    for (const rule of rules) {
      const layer = typeof CSSLayerBlockRule !== 'undefined' && rule instanceof CSSLayerBlockRule;
      if (layer || (typeof CSSLayerStatementRule !== 'undefined' && rule instanceof CSSLayerStatementRule)) usesLayers = true;
      if (rule instanceof CSSStyleRule && !inLayer) unlayered.push(rule.selectorText);
      if (rule.cssRules && !(rule instanceof CSSStyleRule)) walk(rule.cssRules, inLayer || layer);
    }
  };
  for (const sheet of document.styleSheets) { try { walk(sheet.cssRules, false); } catch { /* cross-origin sheet */ } }
  const page = {
    transitionAll: [...new Set(transitionAll)], runningAnimations: running,
    productUi: pu ? { visible: visible(pu), top: pu.getBoundingClientRect().top + scrollY } : null, heroButtons,
    colorScheme: matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches, innerHeight,
    usesLayers, unlayered: [...new Set(unlayered)],
  };
  return { records, targets, overflow, page, spacingValues };
}

// ---------- assemble a report from a collection ----------

export function buildReport(collected, { tokens, marketing, reducedMotion }) {
  const findings = [];
  const c = auditContrast(collected.records);
  findings.push(...c.findings);
  if (tokens) findings.push(...auditTokens(collected.records, tokens));
  const ty = auditType(collected.records);
  findings.push(...ty.findings);
  const sh = auditShapes(collected.records);
  findings.push(...sh.findings);
  findings.push(...auditTargets(collected.targets));
  findings.push(...auditOverflow(collected.overflow));
  findings.push(...auditMotion(collected.page, { reducedMotion }));
  findings.push(...lintTells(collected.records, { lightPage: collected.page.colorScheme !== 'dark' }));
  findings.push(...auditGlyphs(collected.records));
  findings.push(...auditLayers(collected.page));
  if (marketing) findings.push(...auditMarketing(collected.page, collected.page.innerHeight));
  const scale = tokens && tokens.spacing ? spacingAudit(collected.spacingValues, tokens.spacing) : null;
  const accent = tokens && tokens.accent ? parseColor(tokens.accent) : null;
  const summary = { fail: findings.filter((f) => f.level === 'fail').length, warn: findings.filter((f) => f.level === 'warn').length, contrastChecked: c.checked };
  return {
    summary, findings,
    typeHistogram: ty.histogram, radii: sh.radii, shadows: sh.shadows, textColors: textColors(collected.records),
    spacing: scale ? { offScale: scale.off, shareInScale: Math.round(scale.share * 1000) / 1000 } : null,
    accentUsage: accent ? accentUsage(collected.records, accent) : null,
    page: collected.page,
  };
}

export function normalizeTokens(raw) {
  const t = { ...raw };
  if (t.colors) t.colors = t.colors.map((c) => parseColor(c)).filter(Boolean);
  return t;
}

// ---------- Playwright loading ----------

export async function loadPlaywright() {
  const req = createRequire(pathToFileURL(`${process.cwd()}/`));
  for (const name of ['playwright', 'playwright-core', '@playwright/test']) {
    try {
      const mod = await import(pathToFileURL(req.resolve(name)).href);
      const api = mod.chromium ? mod : mod.default;
      if (api && api.chromium) return api;
    } catch { /* try next */ }
  }
  return null;
}

const MISSING = 'Playwright is not installed in this project (looked for playwright, playwright-core, @playwright/test from the current directory).\n' +
  'Install it in the project, then its Chromium build (see https://playwright.dev/docs/intro), or run the checks by hand as described in references/measurement.md.';

async function launch(pw) {
  try { return await pw.chromium.launch(); } catch (e) {
    process.stderr.write(`Chromium could not start: ${String(e.message).split('\n')[0]}\nInstall the browser build with the project's Playwright, for example: npx playwright install chromium\n`);
    return null;
  }
}

export async function auditPage(page, { tokens, marketing, reducedMotion }) {
  const collected = await page.evaluate(collectInPage, { maxElements: 4000 });
  return buildReport(collected, { tokens, marketing, reducedMotion });
}

// ---------- self-test ----------

const BAD_HTML = `<!doctype html><html><head><style>
 body { background: white; color: rgb(17, 17, 17); font: 16px/1.5 Inter, sans-serif; }
 .eyebrow { text-transform: uppercase; letter-spacing: 0.12em; font-size: 12px; }
 h1 { font-size: 48px; line-height: 1.3; }
 .grad { background-image: linear-gradient(135deg, #7c3aed, #4f46e5); }
 .mono { font-family: 'JetBrains Mono', monospace; }
 .card { box-shadow: 0 1px 3px rgba(0,0,0,.1); border-radius: 12px; }
 .btn { transition: all .2s; }
</style></head><body>
<section class="grad"><p class="eyebrow">Features</p><h1>Ship <em>faster</em> with Acme</h1>
<h2>Welcome \u{1F680} John Doe</h2>
<a href="/a">Docs \u2192</a> <a href="/b">Pricing \u2192</a> <a href="/c">Start \u2192</a>
<p>Lorem ipsum dolor sit amet</p>
<p>Fast · Secure · Simple</p><p>Cheap · Quick · Easy</p>
<span>01</span><span>02</span><span>03</span>
<span class="mono">status ok</span><span class="mono">region eu</span><span class="mono">plan pro</span>
<button class="btn">Go</button>
<div class="card">One</div><div class="card">Two</div><div class="card">Three</div></section></body></html>`;

const GOOD_HTML = `<!doctype html><html><head><style>
 body { background: white; color: rgb(23, 23, 23); font: 16px/24px sans-serif; }
 h1 { font-size: 40px; line-height: 1.1; letter-spacing: -0.04em; }
 .btn { transition: opacity .15s, transform .15s; }
</style></head><body><h1>Create your first invoice</h1><p>Send it in under a minute.</p>
<p>Import \u2192 review \u2192 send. \u00A9 2026 Example\u2122</p>
<button class="btn">Create invoice</button><a href="/pricing">See pricing</a></body></html>`;

function check(name, cond, detail = '') {
  check.n = (check.n || 0) + 1;
  if (!cond) { check.failed = (check.failed || 0) + 1; process.stderr.write(`FAIL ${name}${detail ? `: ${detail}` : ''}\n`); } else process.stderr.write(`ok   ${name}\n`);
}
const near = (a, b, eps = 0.005) => Math.abs(a - b) <= eps;
const ids = (arr) => arr.map((f) => f.id);

export function runPureTests() {
  const W = [255, 255, 255, 1];
  const K = [0, 0, 0, 1];
  // Hand-computed from L = 0.2126 R + 0.7152 G + 0.0722 B and (L1 + 0.05) / (L2 + 0.05).
  check('black on white = 21:1', near(contrastRatio(K, W), 21, 1e-9));
  check('white on white = 1:1', near(contrastRatio(W, W), 1, 1e-9));
  check('#767676 on white = 4.542 (passes)', near(contrastRatio(parseColor('#767676'), W), 4.5422, 0.0005));
  check('#777777 on white = 4.478 (fails)', near(contrastRatio(parseColor('#777777'), W), 4.4781, 0.0005));
  check('#0000ff on white = 8.592', near(contrastRatio(parseColor('#0000ff'), W), 8.5925, 0.0005));
  check('#6b7280 on #111827 = 3.669 (dark pair)', near(contrastRatio(parseColor('#6b7280'), parseColor('#111827')), 3.6694, 0.0005));
  check('#777777 text fails 4.5', textContrast({ fg: parseColor('#777777'), bg: W, fontSize: 16, fontWeight: 400 }).pass === false);
  check('#767676 text passes 4.5', textContrast({ fg: parseColor('#767676'), bg: W, fontSize: 16, fontWeight: 400 }).pass === true);
  check('#777777 large text (24 px) passes 3:1', textContrast({ fg: parseColor('#777777'), bg: W, fontSize: 24, fontWeight: 400 }).pass === true);
  check('#777777 at 19 px weight 700 counts as large', textContrast({ fg: parseColor('#777777'), bg: W, fontSize: 19, fontWeight: 700 }).pass === true);
  check('#777777 at 19 px weight 400 is not large', textContrast({ fg: parseColor('#777777'), bg: W, fontSize: 19, fontWeight: 400 }).pass === false);
  check('4.499 prints as 4.49, never 4.50', fmt(4.499) === '4.49' && fmt(4.5) === '4.50');
  const half = over([0, 0, 0, 0.5], W);
  check('50% black over white composites to mid grey', near(half[0], 127.5, 1e-9) && half[3] === 1);
  check('parseColor reads rgb(), rgba(), space syntax and hex8', ['rgb(1, 2, 3)', 'rgba(1,2,3,0.5)', 'rgb(1 2 3 / 50%)', '#01020380'].every((c) => parseColor(c) !== null) && near(parseColor('rgb(1 2 3 / 50%)')[3], 0.5, 1e-9));
  check('parseColor expands 3-digit hex', JSON.stringify(parseColor(`#${'7'.repeat(3)}`)) === JSON.stringify(parseColor('#777777')));
  check('parseColor rejects oklch (needs canvas normalisation)', parseColor('oklch(0.5 0.1 200)') === null);

  const rec = (o) => ({ hasText: true, color: [23, 23, 23, 1], bg: W, fontSize: 16, fontWeight: '400', sel: 'p', ...o });
  const a = auditContrast([rec({ color: parseColor('#777777') }), rec({ color: parseColor('#767676') }), rec({ bgUnknown: true })]);
  check('auditContrast: one fail, one unknown-background warning', a.findings.filter((f) => f.level === 'fail').length === 1 && ids(a.findings).includes('contrast-unknown-background') && a.checked === 2);

  const sp = spacingAudit([4, 8, 8, 12, 13, 0, 16, 7], [4, 8, 12, 16]);
  check('spacingAudit lists off-scale 7 and 13, share 5/7', sp.off.join() === '7,13' && near(sp.share, 5 / 7, 1e-9));

  check('shadowLayers counts layers outside parentheses', shadowLayers('rgba(0, 0, 0, 0.1) 0px 1px 2px 0px') === 1 && shadowLayers('rgba(0,0,0,.1) 0 1px 2px, rgba(0,0,0,.1) 0 8px 16px') === 2 && shadowLayers('none') === 0);

  const tg = (o) => ({ sel: 'a', x: 0, y: 0, w: 16, h: 16, inline: false, uaControl: false, ...o });
  check('target 16x16 with a neighbour 4 px away fails', auditTargets([tg({ x: 0 }), tg({ sel: 'b', x: 20 })]).length === 2);
  check('16x16 targets with circles that only touch (24 px centres) pass', auditTargets([tg({ x: 0 }), tg({ sel: 'b', x: 24 })]).length === 0);
  check('target 16x16 alone passes (spacing exception)', auditTargets([tg({}), tg({ sel: 'b', x: 200 })]).length === 0);
  check('target 24x24 beside another passes', auditTargets([tg({ w: 24, h: 24 }), tg({ sel: 'b', x: 24, w: 24, h: 24 })]).length === 0);
  check('inline link in a sentence is exempt', auditTargets([tg({ inline: true }), tg({ sel: 'b', x: 18, inline: true })]).length === 0);

  const shapes = auditShapes([
    { sel: 'card', radius: [8, 8, 8, 8], shadow: 'none', parentKey: null, parentRadiusIdx: null },
    { sel: 'chip', radius: [12, 12, 12, 12], shadow: 'none', parentKey: 0, parentRadiusIdx: 0 },
  ]);
  check('auditShapes flags child radius 12 inside parent 8', ids(shapes.findings).includes('nested-radius'));
  const cards = [0, 1, 2].map((i) => ({ sel: `card${i}`, radius: [12, 12, 12, 12], shadow: 'rgba(0, 0, 0, 0.1) 0px 1px 3px 0px', parentKey: 9, parentRadiusIdx: null }));
  check('auditShapes flags one soft shadow on three sibling cards', ids(auditShapes(cards).findings).includes('tell-repeated-shadow'));

  const tokens = normalizeTokens({ fontSizes: [14, 16], spacing: [4, 8, 16], radii: [6, 12], fontWeights: [400, 600], colors: ['#171717'] });
  const off = auditTokens([rec({ fontSize: 15, spacing: [8, 10], radius: [6, 7] })], tokens);
  check('auditTokens reports fontSize 15, spacing 10, radius 7', ['off-token-fontSize', 'off-token-spacing', 'off-token-radius'].every((i) => ids(off).includes(i)) && off.length === 3);
  check('auditTokens passes values that are tokens', auditTokens([rec({ spacing: [8, 16], radius: [6, 12] })], tokens).length === 0);

  const big = auditType([{ hasText: true, fontSize: 48, lineHeight: 62.4, letterSpacing: 0, sel: 'h1' }, { hasText: true, fontSize: 48, lineHeight: 48, letterSpacing: -1.9, sel: 'h2' }]);
  check('auditType warns on an untuned 48 px heading only', big.findings.length === 1 && big.findings[0].selector === 'h1');
  check('auditType flags tabular-nums on numeric cells', ids(auditType([{ hasText: true, fontSize: 14, numericCell: true, tabular: false, sel: 'td' }]).findings).includes('tabular-nums'));

  check('auditOverflow: 211 px clipped fails, 1 px passes', auditOverflow([{ sel: 'card', scrollWidth: 586, clientWidth: 375, clips: true }, { sel: 'x', scrollWidth: 376, clientWidth: 375 }]).length === 1);
  check('auditMotion: transition all fails; running animation under reduce fails', auditMotion({ transitionAll: ['.btn'], runningAnimations: 2 }, { reducedMotion: true }).length === 2 && auditMotion({ transitionAll: [], runningAnimations: 2 }, { reducedMotion: false }).length === 0);
  check('auditMarketing: no product UI and three hero buttons fail', auditMarketing({ productUi: null, heroButtons: 3 }, 900).length === 2 && auditMarketing({ productUi: { visible: true, top: 527 }, heroButtons: 2 }, 900).length === 0);

  const bad = lintHtml(BAD_HTML);
  const want = ['tell-eyebrow', 'tell-accent-word', 'emoji-glyph', 'tell-placeholder-data', 'tell-arrow-links', 'tell-middle-dot-meta', 'tell-numbered-markers', 'tell-mono-labels', 'tell-purple-gradient', 'transition-all'];
  const missing = want.filter((w) => !ids(bad).includes(w));
  check('tell lint finds every planted tell in the bad sample', missing.length === 0, `missing: ${missing.join(', ')}`);
  const good = lintHtml(GOOD_HTML);
  check('tell lint finds nothing in the clean sample', good.length === 0, ids(good).join(', '));

  const g = (text, o = {}) => ({ text, sel: 'span', inCode: false, userContent: false, ...o });
  const glyphIds = (text, o) => ids(auditGlyphs([g(text, o)]));
  check('glyphs: a flag pair is an emoji', glyphIds('\u{1F1E9}\u{1F1EA} Deutsch').includes('emoji-glyph'));
  check('glyphs: an emoji-style check mark is an emoji', glyphIds('\u2705 Paid').includes('emoji-glyph'));
  check('glyphs: a text check mark forced to emoji style (FE0F) is an emoji', glyphIds('\u2714\uFE0F Paid').includes('emoji-glyph'));
  check('glyphs: a keycap is an emoji', glyphIds('1\uFE0F\u20E3 Step').includes('emoji-glyph'));
  check('glyphs: a text check mark before a label is a symbol icon', glyphIds('\u2714 Paid').includes('symbol-icon'));
  check('glyphs: a star rating is a symbol icon', glyphIds('\u2605\u2605\u2605\u2605\u2606').includes('symbol-icon'));
  check('glyphs: a close cross alone is a symbol icon', glyphIds('\u00D7').includes('symbol-icon'));
  check('glyphs: an arrow alone is a symbol icon', glyphIds('\u2192').includes('symbol-icon'));
  check('glyphs: (c), (tm) and an arrow inside a sentence pass', auditGlyphs([g('\u00A9 2026 Example\u2122'), g('Import \u2192 review \u2192 send')]).length === 0);
  check('glyphs: emoji in code and in user content pass', auditGlyphs([g('\u{1F680}', { inCode: true }), g('Great \u{1F389}', { userContent: true })]).length === 0);
  check('glyphs: data-user-content is read from HTML', ids(lintHtml('<html><body><div data-user-content><p>Thanks \u{1F389}</p></div><p>Plain</p></body></html>')).length === 0);
  check('layers: unlayered rules on a layered page warn', ids(auditLayers({ usesLayers: true, unlayered: [':focus-visible'] })).includes('unlayered-css'));
  check('layers: a page without layers does not warn', auditLayers({ usesLayers: false, unlayered: ['p'] }).length === 0);
  check('auditTokens reports a z-index outside the scale', ids(auditTokens([rec({ zIndex: 9999 }), rec({ zIndex: 50 })], normalizeTokens({ zIndex: [10, 50] }))).join() === 'off-token-zIndex');
}

const PAGE = (css, body, extra = '') => `<!doctype html><html lang="en"><head><meta charset="utf-8"><style>*{box-sizing:border-box}body{margin:0;font:16px/24px sans-serif;background:#fff;color:#171717}${css}</style></head><body>${body}${extra}</body></html>`;

export async function runBrowserTests(pw) {
  const browser = await launch(pw);
  if (!browser) { process.stderr.write('skip browser self-test: Chromium unavailable\n'); return false; }
  try {
    const run = async (html, { scheme, reduced, width = 1280, height = 800, marketing, tokens } = {}) => {
      const ctx = await browser.newContext({ viewport: { width, height }, colorScheme: scheme || 'light', reducedMotion: reduced ? 'reduce' : 'no-preference' });
      const page = await ctx.newPage();
      await page.setContent(html);
      const report = await auditPage(page, { tokens, marketing, reducedMotion: !!reduced });
      await ctx.close();
      return report;
    };
    const has = (r, id, level) => r.findings.some((f) => f.id === id && (!level || f.level === level));

    let r = await run(PAGE('.a{color:#777777}.b{color:#767676}.c{color:#777777;font-size:24px}', '<p class="a">Grey 777</p><p class="b">Grey 767676</p><p class="c">Large 777</p>'));
    const contrastFails = r.findings.filter((f) => f.id === 'contrast');
    check('browser: #777777 fails, #767676 and large #777777 pass', contrastFails.length === 1 && contrastFails[0].selector.includes('p.a') && contrastFails[0].message.startsWith('4.47:1'), JSON.stringify(contrastFails));

    const themed = '.m{color:#4b5563}@media (prefers-color-scheme:dark){body{background:#111827;color:#f9fafb}.m{color:#6b7280}}';
    r = await run(PAGE(themed, '<p class="m">Muted</p>'), { scheme: 'light' });
    check('browser: muted text passes in light (7.56:1)', !has(r, 'contrast'));
    r = await run(PAGE(themed, '<p class="m">Muted</p>'), { scheme: 'dark' });
    check('browser: same muted text fails in dark (3.66:1)', has(r, 'contrast', 'fail') && r.findings.find((f) => f.id === 'contrast').message.startsWith('3.66:1'));

    r = await run(PAGE('.p{color:#777777;background:rgba(0,0,0,.5)}', '<p class="p">Translucent</p>'));
    check('browser: translucent black over white is composited (#777777 on mid grey fails at 1.1:1)', has(r, 'contrast', 'fail') && r.findings.find((f) => f.id === 'contrast').message.startsWith('1.1'));

    r = await run(PAGE('.outer{border-radius:8px;padding:8px;background:#eee}.inner{border-radius:12px;background:#ddd;padding:8px}', '<div class="outer"><div class="inner">x</div></div>'));
    check('browser: nested radius 12 in 8 fails', has(r, 'nested-radius', 'fail'));

    r = await run(PAGE('.card{width:300px;overflow:hidden}.wide{width:520px;background:#eee}', '<div class="card"><div class="wide">wide</div></div>'));
    check('browser: overflow inside overflow:hidden card is found', has(r, 'overflow', 'fail'));

    r = await run(PAGE('a{display:inline-block;width:16px;height:16px;background:#ccc;margin-right:4px}', '<a href="#a"></a><a href="#b"></a>'));
    check('browser: two 16 px targets 4 px apart fail', has(r, 'target-size', 'fail'));
    r = await run(PAGE('a{display:inline-block;width:24px;height:24px;background:#ccc;margin-right:4px}', '<a href="#a"></a><a href="#b"></a>'));
    check('browser: two 24 px targets pass', !has(r, 'target-size'));

    r = await run(PAGE('.b{transition:all .2s;display:block;padding:8px}', '<button class="b">x</button>'));
    check('browser: transition all fails', has(r, 'transition-all', 'fail'));

    const anim = '@keyframes spin{to{transform:rotate(360deg)}}.s{width:20px;height:20px;background:#333333;animation:spin 1s linear infinite}@media (prefers-reduced-motion:reduce){.s{animation:none}}';
    r = await run(PAGE(anim, '<div class="s"></div>'), { reduced: true });
    check('browser: reduced-motion variant stops the animation', !has(r, 'reduced-motion'));
    r = await run(PAGE('@keyframes spin{to{transform:rotate(360deg)}}.s{width:20px;height:20px;background:#333333;animation:spin 1s linear infinite}', '<div class="s"></div>'), { reduced: true });
    check('browser: animation without reduced-motion variant fails', has(r, 'reduced-motion', 'fail'));

    r = await run(PAGE('.eye{text-transform:uppercase;letter-spacing:.12em;font-size:12px}h1{font-size:48px;line-height:1.3;margin:0}', '<p class="eye">Features</p><h1>Ship faster</h1>'));
    check('browser: eyebrow and untuned display heading warn', has(r, 'tell-eyebrow', 'warn') && has(r, 'untuned-display', 'warn'));

    r = await run(PAGE('td{font-size:14px}', '<table><tr><td>$1,200.00</td><td>12 items</td></tr></table>'));
    check('browser: numeric cell without tabular-nums warns', has(r, 'tabular-nums', 'warn'));

    r = await run(PAGE('.g{background:linear-gradient(135deg,#7c3aed,#4f46e5);color:#fff;padding:8px}', '<div class="g">Hero</div>'));
    check('browser: purple gradient on a light page warns', has(r, 'tell-purple-gradient', 'warn') && has(r, 'contrast-unknown-background', 'warn'));

    r = await run(PAGE('h1{margin:0}.b{display:inline-block;padding:4px 12px}', '<section><h1>Create invoices</h1><button class="b">Create</button><button class="b">Pricing</button><button class="b">Docs</button></section>'), { marketing: true });
    check('browser: marketing page without product UI and with three hero buttons fails', has(r, 'product-ui', 'fail') && has(r, 'hero-buttons', 'fail'));
    r = await run(PAGE('h1{margin:0}.b{display:inline-block;padding:4px 12px}', '<section><h1>Create invoices</h1><button class="b">Create</button></section><div data-testid="product-ui" style="margin-top:300px">UI</div>'), { marketing: true });
    check('browser: product UI at 360 px with one button passes', !has(r, 'product-ui') && !has(r, 'hero-buttons'));

    r = await run(PAGE('', '<p><span>\u{1F1E9}\u{1F1EA}</span> Deutsch</p><p>\u2713 Paid</p><p>Import \u2192 send</p>'));
    check('browser: flag emoji and check-mark status fail, arrow in prose passes', has(r, 'emoji-glyph', 'fail') && has(r, 'symbol-icon', 'fail') && r.findings.filter((x) => x.id === 'symbol-icon').length === 1);

    r = await run('<!doctype html><html><head><style>@layer base{a{color:#171717}}@layer utilities{.ring{outline:2px solid #171717}}:focus-visible{outline:3px solid red}</style></head><body><a class="ring" href="#x">Link</a></body></html>');
    check('browser: unlayered rule on a layered page warns', has(r, 'unlayered-css', 'warn'));
    r = await run('<!doctype html><html><head><style>@layer base{a{color:#171717}:focus-visible{outline:3px solid #171717}}</style></head><body><a href="#x">Link</a></body></html>');
    check('browser: everything layered does not warn', !has(r, 'unlayered-css'));

    r = await run(PAGE('p{font-size:15px;margin:0;padding:10px}', '<p>Hello</p>'), { tokens: normalizeTokens({ fontSizes: [14, 16], spacing: [4, 8, 16], radii: [6, 12] }) });
    check('browser: token list rejects 15 px text and 10 px padding', has(r, 'off-token-fontSize', 'fail') && has(r, 'off-token-spacing', 'fail'));
    return true;
  } finally {
    await browser.close();
  }
}

async function selfTest() {
  runPureTests();
  const pw = await loadPlaywright();
  if (pw) await runBrowserTests(pw); else process.stderr.write('skip browser self-test: Playwright not installed here (pure checks above still ran)\n');
  const failed = check.failed || 0;
  process.stderr.write(`${check.n - failed} of ${check.n} checks passed\n`);
  return failed === 0 ? 0 : 1;
}

// ---------- CLI ----------

function parseArgs(argv) {
  const o = { scheme: 'light', reducedMotion: false, viewport: '1440x900' };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = () => { if (i + 1 >= argv.length || argv[i + 1].startsWith('--')) throw new Error(`${a} needs a value`); return argv[++i]; };
    if (a === '--url') o.url = val();
    else if (a === '--tokens') o.tokens = val();
    else if (a === '--scheme') o.scheme = val();
    else if (a === '--viewport') o.viewport = val();
    else if (a === '--reduced-motion') o.reducedMotion = true;
    else if (a === '--marketing') o.marketing = true;
    else if (a === '--self-test') o.selfTest = true;
    else if (a === '--help' || a === '-h') o.help = true;
    else throw new Error(`unknown option ${a}`);
  }
  return o;
}

const USAGE = 'usage: node design_audit.mjs --url URL [--tokens tokens.json] [--scheme light|dark] [--reduced-motion] [--viewport WxH] [--marketing]\n       node design_audit.mjs --self-test\n';

async function main() {
  let o;
  try { o = parseArgs(process.argv.slice(2)); } catch (e) { process.stderr.write(`${e.message}\n${USAGE}`); return 2; }
  if (o.help) { process.stdout.write(USAGE); return 0; }
  if (o.selfTest) return selfTest();
  if (!o.url) { process.stderr.write(USAGE); return 2; }
  if (!['light', 'dark'].includes(o.scheme)) { process.stderr.write('--scheme must be light or dark\n'); return 2; }
  const vp = o.viewport.match(/^(\d+)x(\d+)$/);
  if (!vp) { process.stderr.write('--viewport must look like 1440x900\n'); return 2; }
  let tokens = null;
  if (o.tokens) {
    try { tokens = normalizeTokens(JSON.parse(readFileSync(resolve(o.tokens), 'utf8'))); } catch (e) { process.stderr.write(`cannot read tokens file: ${e.message}\n`); return 2; }
  }
  const pw = await loadPlaywright();
  if (!pw) { process.stderr.write(`${MISSING}\n`); return 2; }
  const browser = await launch(pw);
  if (!browser) return 2;
  try {
    const ctx = await browser.newContext({ viewport: { width: +vp[1], height: +vp[2] }, colorScheme: o.scheme, reducedMotion: o.reducedMotion ? 'reduce' : 'no-preference' });
    const page = await ctx.newPage();
    await page.goto(o.url, { waitUntil: 'load' });
    await page.evaluate(async () => { await document.fonts.ready; });
    const report = await auditPage(page, { tokens, marketing: o.marketing, reducedMotion: o.reducedMotion });
    report.input = { url: o.url, scheme: o.scheme, reducedMotion: o.reducedMotion, viewport: o.viewport };
    process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
    process.stderr.write(`${report.summary.fail} fail, ${report.summary.warn} warn, ${report.summary.contrastChecked} text elements checked for contrast\n`);
    return report.summary.fail > 0 ? 1 : 0;
  } finally {
    await browser.close();
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().then((c) => process.exit(c), (e) => { process.stderr.write(`${e.stack || e}\n`); process.exit(2); });
}
