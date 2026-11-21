#!/usr/bin/env node
/**
 * Measure motion with Playwright, headless, in Chromium, Firefox and WebKit. Import what you need:
 *
 *   import { launch, sample, settled, overshoot, boxes, shift, drag, presentation, frames,
 *            rubberBand, catchTest, pointerLog } from './probe.mjs';
 *
 * Playwright is resolved from the project under test (the current directory, or PLAYWRIGHT_FROM),
 * so the probe uses the project's pinned version and its installed browsers. Set
 * PROBE_CHROMIUM_CHANNEL=chrome to drive an installed Chrome instead of the bundled Chromium.
 *
 *   node probe.mjs --self-test     checks the pure helpers; needs no browser
 */
import { createRequire } from 'node:module';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

let playwright;

async function loadPlaywright() {
    if (!playwright) {
        const from = process.env.PLAYWRIGHT_FROM ?? process.cwd();
        const require = createRequire(join(from, 'probe-resolve.js'));
        const mod = await import(pathToFileURL(require.resolve('playwright')).href);
        playwright = mod.chromium ? mod : mod.default;
    }
    return playwright;
}

/**
 * Start chromium, firefox or webkit headless. Firefox refuses a dev server that announces itself on
 * [::] (Vite with --host) unless the pref below is set.
 */
export async function launch(name = 'chromium', options = {}) {
    const engine = (await loadPlaywright())[name];
    if (!engine) {
        throw new Error(`unknown engine ${name}; use chromium, firefox or webkit`);
    }
    const extra =
        name === 'chromium' && process.env.PROBE_CHROMIUM_CHANNEL
            ? { channel: process.env.PROBE_CHROMIUM_CHANNEL }
            : name === 'firefox'
              ? { firefoxUserPrefs: { 'network.socket.ip_addr_any.disabled': false } }
              : {};
    return engine.launch({ headless: true, ...extra, ...options });
}

/** Sample an element every frame for `ms`: box, opacity and translate. Read peaks from this. */
export function sample(page, selector, ms = 1000) {
    return page.evaluate(
        ({ selector, ms }) =>
            new Promise((resolve) => {
                const out = [];
                const t0 = performance.now();
                const step = () => {
                    const el = document.querySelector(selector);
                    if (el) {
                        const r = el.getBoundingClientRect();
                        const cs = getComputedStyle(el);
                        const [tx = 0, ty = 0] = cs.translate === 'none' ? [] : cs.translate.split(' ').map(parseFloat);
                        out.push({ t: Math.round(performance.now() - t0), x: r.x, y: r.y, w: r.width, h: r.height, opacity: Number(cs.opacity), tx, ty });
                    }
                    if (performance.now() - t0 < ms) {
                        requestAnimationFrame(step);
                    } else {
                        resolve(out);
                    }
                };
                requestAnimationFrame(step);
            }),
        { selector, ms },
    );
}

/**
 * Wait until no finite animation or transition runs on the element and its subtree. Infinite loops
 * (spinners) never end and are skipped; `ignore` skips more, such as a countdown bar.
 */
export function settled(page, selector, { timeout = 5000, subtree = true, ignore = null } = {}) {
    return page.waitForFunction(
        ({ selector, subtree, ignore }) => {
            const el = document.querySelector(selector);
            if (!el) {
                return false;
            }
            return el.getAnimations({ subtree }).every((animation) => {
                const target = animation.effect?.target;
                if (ignore && target?.matches?.(ignore)) {
                    return true;
                }
                const timing = animation.effect?.getComputedTiming?.();
                return animation.playState !== 'running' || !timing || timing.iterations === Infinity || timing.endTime === Infinity;
            });
        },
        { selector, subtree, ignore },
        { timeout, polling: 'raf' },
    );
}

/** Overshoot in percent of the travel from `from` to `to`, for one key of the samples. */
export function overshoot(samples, key, from, to) {
    const travel = to - from;
    if (!travel) {
        return 0;
    }
    const beyond = samples.reduce((max, s) => Math.max(max, (s[key] - to) / travel), 0);
    return Math.round(beyond * 1000) / 10;
}

/** Boxes of several elements, to compare before and after an action. */
export function boxes(page, selectors) {
    return page.evaluate(
        (selectors) =>
            Object.fromEntries(
                selectors.map((s) => {
                    const el = document.querySelector(s);
                    if (!el) {
                        return [s, null];
                    }
                    const r = el.getBoundingClientRect();
                    return [s, { x: r.x, y: r.y, w: r.width, h: r.height }];
                }),
            ),
        selectors,
    );
}

/** Largest change in px per element between two boxes() snapshots. Anything above 0 moved. */
export function shift(before, after) {
    return Object.fromEntries(
        Object.keys(before).map((k) => {
            const a = before[k];
            const b = after[k];
            if (!a || !b) {
                return [k, null];
            }
            return [k, Math.round(Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y), Math.abs(a.w - b.w), Math.abs(a.h - b.h)) * 10) / 10];
        }),
    );
}

/** Drag with the mouse at a chosen speed. holdMs: stand still before letting go, so it is no throw. */
export async function drag(page, from, to, { ms = 300, steps = 12, holdMs = 0, release = true } = {}) {
    await page.mouse.move(from.x, from.y);
    await page.mouse.down();
    for (let i = 1; i <= steps; i++) {
        await page.mouse.move(from.x + ((to.x - from.x) * i) / steps, from.y + ((to.y - from.y) * i) / steps);
        await page.waitForTimeout(ms / steps);
    }
    if (holdMs) {
        await page.waitForTimeout(holdMs);
    }
    if (release) {
        await page.mouse.up();
    }
}

/** The translate on screen right now (the presentation value), in px. */
export function presentation(page, selector) {
    return page.evaluate((s) => {
        const t = getComputedStyle(document.querySelector(s)).translate;
        const [x = 0, y = 0] = t === 'none' ? [] : t.split(' ').map(parseFloat);
        return { x, y };
    }, selector);
}

/** Wait n animation frames. */
export function frames(page, n = 2) {
    return page.evaluate(
        (n) =>
            new Promise((resolve) => {
                let i = 0;
                const tick = () => (++i >= n ? resolve() : requestAnimationFrame(tick));
                requestAnimationFrame(tick);
            }),
        n,
    );
}

/**
 * Rubber band: 1:1 up to `free` px, then an exponential approach to `reach` px. `shown` maps pointer
 * distance to the offset on screen; `pointer` is its inverse, used when a moving element is caught.
 */
export function rubberBand({ free = 16, reach = 72, soft = 60 } = {}) {
    return {
        shown: (d) => (d <= free ? d : free + (reach - free) * (1 - Math.exp(-(d - free) / soft))),
        pointer: (s) => (s <= free ? s : free - soft * Math.log(1 - (Math.min(s, reach - 0.01) - free) / (reach - free))),
    };
}

/**
 * Log pointer events with a capture listener. If a drag never ends, read this before trusting the run:
 * a missing pointerup means the input never reached the page, and the run is inconclusive.
 */
export async function pointerLog(page) {
    await page.evaluate(() => {
        window.__pointerLog = [];
        for (const type of ['pointerdown', 'pointerup', 'pointercancel', 'gotpointercapture', 'lostpointercapture']) {
            window.addEventListener(type, (e) => window.__pointerLog.push({ type, t: Math.round(performance.now()), id: e.pointerId }), { capture: true });
        }
    });
    return () => page.evaluate(() => window.__pointerLog);
}

/**
 * Catch a draggable element while it springs back, and measure whether anything jumps.
 *
 * For each wait: `prepare()` puts a fresh element on screen, the element is pulled by `pull` px and held
 * still (no throw), released, and pressed again `wait` ms later. A capture listener reads the state at the
 * press, before the component's own handler runs. Reported per wait, in px unless noted:
 *   shown      the offset on screen at the press
 *   drift      how far the element moved while the pointer held still for two frames (expected 0)
 *   moveError  distance from the curve's prediction after 5 px of pointer travel (expected 0)
 *   dependents the largest change of any dependent element while held still: box in px, opacity
 *   settled    the offset 900 ms after letting go (expected 0)
 */
export async function catchTest(page, selector, { prepare, pull = 50, waits = [40, 70, 120, 200], curve = rubberBand(), dependents = [] } = {}) {
    await page.evaluate(
        ({ selector, dependents }) => {
            const offset = (el) => {
                const t = el ? getComputedStyle(el).translate : 'none';
                const [x = 0, y = 0] = !t || t === 'none' ? [] : t.split(' ').map(parseFloat);
                return [x, y];
            };
            window.__catchState = () => ({
                offset: offset(document.querySelector(selector)),
                dependents: dependents.map((s) => {
                    const el = document.querySelector(s);
                    if (!el) {
                        return null;
                    }
                    const r = el.getBoundingClientRect();
                    return { x: r.x, y: r.y, w: r.width, h: r.height, o: Number(getComputedStyle(el).opacity) };
                }),
            });
            window.__catchPresses = [];
            window.addEventListener('pointerdown', () => window.__catchPresses.push(window.__catchState()), { capture: true });
        },
        { selector, dependents },
    );
    const state = () => page.evaluate(() => window.__catchState());
    const center = async () => {
        const b = await page.locator(selector).first().boundingBox();
        return { x: b.x + b.width / 2, y: b.y + b.height / 2 };
    };

    const rows = [];
    for (const wait of waits) {
        if (prepare) {
            await prepare();
        }
        const start = await center();
        await drag(page, start, { x: start.x + pull, y: start.y }, { ms: 200, steps: 20, holdMs: 150 });
        await page.waitForTimeout(wait);
        const grab = await center();
        await page.mouse.move(grab.x, grab.y);
        const index = await page.evaluate(() => window.__catchPresses.length);
        await page.mouse.down();
        await frames(page, 2);
        const held = await state();
        await page.mouse.move(grab.x + 5, grab.y);
        await frames(page, 2);
        const moved = await state();
        const pressed = await page.evaluate((i) => window.__catchPresses[i], index);
        await page.mouse.up();
        await page.waitForTimeout(900);
        const after = await state();
        if (!pressed) {
            rows.push({ wait, inconclusive: 'the press never reached the page' });
            continue;
        }

        const [x, y] = pressed.offset;
        const shown = Math.hypot(x, y);
        const reach = curve.pointer(shown);
        const px = (shown > 0.01 ? (x / shown) * reach : 0) + 5;
        const py = shown > 0.01 ? (y / shown) * reach : 0;
        const d = Math.hypot(px, py);
        const expected = [(px / d) * curve.shown(d), (py / d) * curve.shown(d)];
        const round = (n) => Math.round(n * 10) / 10;
        rows.push({
            wait,
            shown: round(shown),
            drift: round(Math.hypot(held.offset[0] - x, held.offset[1] - y)),
            moveError: round(Math.hypot(moved.offset[0] - expected[0], moved.offset[1] - expected[1])),
            dependents: pressed.dependents.map((a, i) => {
                const b = held.dependents[i];
                if (!a || !b) {
                    return null;
                }
                return { box: round(Math.max(Math.abs(a.x - b.x), Math.abs(a.y - b.y), Math.abs(a.w - b.w), Math.abs(a.h - b.h))), opacity: Math.round(Math.abs(a.o - b.o) * 100) / 100 };
            }),
            settled: round(Math.hypot(...after.offset)),
        });
    }
    return rows;
}

function selfTest() {
    const failures = [];
    let checks = 0;
    const check = (ok, message) => {
        checks++;
        if (!ok) {
            failures.push(message);
        }
    };

    const samples = [{ w: 44 }, { w: 120 }, { w: 212 }, { w: 205 }, { w: 200 }];
    check(overshoot(samples, 'w', 44, 200) === 7.7, `overshoot ${overshoot(samples, 'w', 44, 200)}, expected 7.7`);
    check(overshoot(samples, 'w', 44, 44) === 0, 'overshoot without travel is not 0');

    const moved = shift({ a: { x: 0, y: 0, w: 10, h: 10 }, b: null }, { a: { x: 0, y: 3, w: 10, h: 10 }, b: { x: 0, y: 0, w: 1, h: 1 } });
    check(moved.a === 3 && moved.b === null, `shift ${JSON.stringify(moved)}, expected a 3 and b null`);

    const band = rubberBand();
    for (const d of [0, 8, 16, 30, 60, 120]) {
        check(Math.abs(band.pointer(band.shown(d)) - d) < 1e-6, `rubber band inverse is off at ${d} px`);
    }
    check(band.shown(500) < 72, 'rubber band passes its reach');
    check(band.shown(10) === 10, 'rubber band is not 1:1 inside the free distance');

    if (failures.length) {
        console.error(failures.map((f) => `FAIL ${f}`).join('\n'));
        process.exitCode = 1;
        return;
    }
    console.log(`self-test passed (${checks} checks)`);
}

const invokedDirectly = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (invokedDirectly && process.argv.includes('--self-test')) {
    selfTest();
}
