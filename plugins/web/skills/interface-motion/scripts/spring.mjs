#!/usr/bin/env node
/**
 * Spring to CSS linear(). No dependencies; runs in Node and in the browser.
 *
 * Parameters follow Apple's spring model: a perceptual duration in seconds and a bounce from -1 to 1,
 * or the physics triplet stiffness, damping and mass. An optional release velocity is given in progress
 * units per second: the gesture's speed in px/s divided by the px the element still has to travel.
 *
 * The browser plays the result as an ordinary CSS transition. Nothing runs per frame.
 *
 *   node spring.mjs 0.35 0              duration, bounce
 *   node spring.mjs 0.35 0.2 --v 3      with a release velocity
 *   node spring.mjs --k 300 --d 24      stiffness, damping (mass 1)
 *   node spring.mjs --self-test         proves the math below
 */

/** Natural frequency w0 (rad/s) and damping ratio zeta. */
export function params({ duration, bounce = 0, stiffness, damping, mass = 1 } = {}) {
    if (stiffness !== undefined) {
        if (!(stiffness > 0) || !(damping >= 0) || !(mass > 0)) {
            throw new Error('stiffness and mass must be positive, damping at least 0');
        }
        return { w0: Math.sqrt(stiffness / mass), zeta: damping / (2 * Math.sqrt(stiffness * mass)) };
    }
    if (!(duration > 0)) {
        throw new Error('a duration in seconds, or stiffness and damping, is required');
    }
    if (!(bounce > -1 && bounce < 1)) {
        throw new Error('bounce must be between -1 and 1');
    }
    // Mass 1, stiffness (2 pi / duration)^2, damping ratio 1 - bounce (or 1 / (1 + bounce) below 0).
    return { w0: (2 * Math.PI) / duration, zeta: bounce >= 0 ? 1 - bounce : 1 / (1 + bounce) };
}

/** Progress x(t) from 0 to 1 with initial velocity v0 in progress units per second. */
export function position(w0, zeta, v0 = 0) {
    if (zeta < 1) {
        const wd = w0 * Math.sqrt(1 - zeta * zeta);
        return (t) => 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + ((zeta * w0 - v0) / wd) * Math.sin(wd * t));
    }
    if (zeta === 1) {
        return (t) => 1 - Math.exp(-w0 * t) * (1 + (w0 - v0) * t);
    }
    const s = w0 * Math.sqrt(zeta * zeta - 1);
    const r1 = -zeta * w0 + s;
    const r2 = -zeta * w0 - s;
    const c1 = (v0 + r2) / (r1 - r2);
    const c2 = -1 - c1;
    return (t) => 1 + c1 * Math.exp(r1 * t) + c2 * Math.exp(r2 * t);
}

/**
 * @returns {{ easing: string, ms: number, overshoot: number, duration: number, bounce: number }}
 *   easing: the linear() function. ms: time until the spring stays within 0.2 % of the target; use it as
 *   transition-duration. overshoot: the peak beyond the target as a fraction of the distance.
 *   duration and bounce: the same spring in Apple's terms.
 */
export function spring(options = {}) {
    const { w0, zeta } = params(options);
    const x = position(w0, zeta, options.velocity ?? 0);

    let settle = 0;
    let peak = 0;
    for (let t = 0; t <= 3; t += 1 / 240) {
        const value = x(t);
        if (Math.abs(1 - value) > 0.002) {
            settle = t;
        }
        peak = Math.max(peak, value);
    }
    settle = Math.max(settle, 0.08);

    const steps = Math.max(16, Math.min(72, Math.ceil(settle * 60)));
    const points = [];
    for (let i = 0; i <= steps; i++) {
        points.push(Math.round(x((i / steps) * settle) * 10000) / 10000);
    }
    points[0] = 0;
    points[steps] = 1;

    return {
        easing: `linear(${points.join(', ')})`,
        ms: Math.round(settle * 1000),
        overshoot: Math.max(0, peak - 1),
        duration: (2 * Math.PI) / w0,
        bounce: zeta <= 1 ? 1 - zeta : 1 / zeta - 1,
    };
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

    const smooth = spring({ duration: 0.35, bounce: 0 });
    check(smooth.overshoot === 0, `bounce 0 overshoots (${smooth.overshoot})`);
    check(smooth.ms > 350 && smooth.ms < 600, `bounce 0 settles after ${smooth.ms} ms, expected 350 to 600`);

    const bouncy = spring({ duration: 0.36, bounce: 0.31 });
    const zeta = 0.69;
    const closedForm = Math.exp((-Math.PI * zeta) / Math.sqrt(1 - zeta * zeta));
    check(Math.abs(bouncy.overshoot - closedForm) < 0.005, `bounce 0.31 overshoots ${bouncy.overshoot}, closed form ${closedForm}`);

    const physical = spring({ stiffness: 300, damping: 24 });
    check(Math.abs(physical.duration - (2 * Math.PI) / Math.sqrt(300)) < 1e-9, 'stiffness 300 maps to the wrong duration');
    check(Math.abs(physical.bounce - (1 - 24 / (2 * Math.sqrt(300)))) < 1e-9, 'damping 24 maps to the wrong bounce');

    for (const result of [smooth, bouncy, physical]) {
        const values = result.easing.slice(7, -1).split(', ').map(Number);
        check(result.easing.startsWith('linear(0, ') && result.easing.endsWith(', 1)'), `easing does not run from 0 to 1: ${result.easing.slice(0, 40)}`);
        check(values.length >= 17 && values.length <= 73, `easing has ${values.length} points, expected 17 to 73`);
        check(values.every(Number.isFinite), 'easing contains a value that is not a number');
    }

    const resting = position(params({ duration: 0.35, bounce: 0.2 }).w0, 0.8, 0);
    const thrown = position(params({ duration: 0.35, bounce: 0.2 }).w0, 0.8, 3);
    check(thrown(0.02) > resting(0.02), 'a release velocity does not speed up the start');

    const flat = spring({ duration: 0.4, bounce: -0.3 });
    const flatValues = flat.easing.slice(7, -1).split(', ').map(Number);
    check(flat.overshoot === 0, 'a negative bounce overshoots');
    check(flatValues.every((v, i) => i === 0 || v >= flatValues[i - 1]), 'a negative bounce is not monotonic');

    let threw = false;
    try {
        spring({ duration: 0.3, bounce: 1.5 });
    } catch {
        threw = true;
    }
    check(threw, 'bounce 1.5 was accepted');

    if (failures.length) {
        console.error(failures.map((f) => `FAIL ${f}`).join('\n'));
        process.exitCode = 1;
        return;
    }
    console.log(`self-test passed (${checks} checks)`);
}

function cli(args) {
    if (args.includes('--self-test')) {
        selfTest();
        return;
    }
    const value = (name) => {
        const i = args.indexOf(name);
        return i === -1 ? undefined : Number(args[i + 1]);
    };
    const flagged = new Set(['--k', '--d', '--m', '--v']);
    const positional = args.filter((arg, i) => !flagged.has(arg) && !flagged.has(args[i - 1])).map(Number);
    const options =
        value('--k') !== undefined
            ? { stiffness: value('--k'), damping: value('--d'), mass: value('--m') ?? 1 }
            : { duration: positional[0], bounce: positional[1] ?? 0 };
    options.velocity = value('--v') ?? 0;
    const result = spring(options);
    console.log(
        `duration ${result.duration.toFixed(3)} s, bounce ${result.bounce.toFixed(2)}, ` +
            `overshoot ${(result.overshoot * 100).toFixed(1)} %, settles after ${result.ms} ms`,
    );
    console.log(`transition: transform ${result.ms}ms ${result.easing};`);
}

const invokedDirectly =
    typeof process !== 'undefined' && process.argv?.[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href;
if (invokedDirectly) {
    cli(process.argv.slice(2));
}
