#!/usr/bin/env python3
"""Check a package.json against the frontend favorites in references/libraries.md.

Usage:
  check_frontend_deps.py [PACKAGE_JSON ...] [--allow PKG[,PKG...]]
  check_frontend_deps.py --self-test

PACKAGE_JSON defaults to ./package.json. --allow names packages an owner profile, AGENTS.md or an
ADR approved; they never count as a finding.

Checks (code, level, what fails):
  F01 error    a package on the avoid list (moment, deprecated or renamed packages, unmaintained
               flag or toast packages, emoji-flag polyfills, a Precognition add-on that Inertia 3
               already contains)
  F02 error    two libraries for one need: toasts, icons, charts, UI primitives, dates, tables,
               client state, i18n, flags
  F03 warning  a need covered only by a library that is not the favorite (an ADR or the owner
               profile names it, or the favorite replaces it)

Dependencies and devDependencies are both read. Packages of one family (echarts with vue-echarts,
date-fns with @date-fns/tz) count as one library.

Output: one finding per line as "path: level code message". Exit 0 when there is no error, 1
otherwise, 2 on a usage error. Python 3.8 or later, standard library only, no network.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

# need -> (favorite family name, {family name: set of packages})
NEEDS: dict[str, tuple[str, dict[str, set[str]]]] = {
    "UI primitives": ("reka-ui", {
        "reka-ui": {"reka-ui"},
        "headlessui": {"@headlessui/vue"},
        "primevue": {"primevue"},
        "vuetify": {"vuetify"},
        "element-plus": {"element-plus"},
        "naive-ui": {"naive-ui"},
        "quasar": {"quasar"},
        "ant-design-vue": {"ant-design-vue"},
        "ark-ui": {"@ark-ui/vue"},
    }),
    "icons": ("lucide", {
        "lucide": {"@lucide/vue"},
        "heroicons": {"@heroicons/vue"},
        "fontawesome": {"@fortawesome/vue-fontawesome", "@fortawesome/fontawesome-svg-core"},
        "mdi": {"@mdi/js", "@mdi/font"},
        "iconify": {"@iconify/vue", "unplugin-icons"},
        "tabler": {"@tabler/icons-vue"},
        "phosphor": {"@phosphor-icons/vue"},
    }),
    "toasts": ("vue-sonner", {
        "vue-sonner": {"vue-sonner"},
        "vue3-toastify": {"vue3-toastify"},
        "notivue": {"notivue"},
        "vue3-notification": {"@kyvg/vue3-notification"},
        "vue-toast-notification": {"vue-toast-notification"},
    }),
    "charts": ("echarts", {
        "echarts": {"echarts", "vue-echarts"},
        "chartjs": {"chart.js", "vue-chartjs"},
        "apexcharts": {"apexcharts", "vue3-apexcharts"},
        "unovis": {"@unovis/vue", "@unovis/ts"},
        "highcharts": {"highcharts", "highcharts-vue"},
        "plotly": {"plotly.js", "plotly.js-dist", "plotly.js-dist-min"},
    }),
    "dates": ("date-fns", {
        "date-fns": {"date-fns", "@date-fns/tz", "@date-fns/utc"},
        "dayjs": {"dayjs"},
        "luxon": {"luxon"},
    }),
    "tables": ("tanstack-table", {
        "tanstack-table": {"@tanstack/vue-table"},
        "ag-grid": {"ag-grid-vue3", "ag-grid-community"},
        "vue-good-table": {"vue-good-table-next"},
    }),
    "client state": ("pinia", {
        "pinia": {"pinia"},
    }),
    "i18n": ("vue-i18n", {
        "vue-i18n": {"vue-i18n", "@intlify/unplugin-vue-i18n"},
        "i18next": {"i18next", "i18next-vue"},
        "fluent": {"@fluent/vue", "@fluent/bundle"},
    }),
    "flags": ("flag-icons", {
        "flag-icons": {"flag-icons"},
        "country-flag-icons": {"country-flag-icons"},
    }),
}

AVOID: dict[str, str] = {
    "moment": "legacy and in maintenance mode; use Intl, then date-fns",
    "moment-timezone": "legacy; use Intl with timeZone, then @date-fns/tz",
    "lucide-vue-next": "deprecated on npm; use @lucide/vue",
    "radix-vue": "renamed to reka-ui; use reka-ui",
    "vuex": "Pinia is the official store; use pinia for UI state only",
    "vue-toastification": "no release for Vue 3 since 2022; use vue-sonner",
    "vue-country-flag-next": "no release since 2022; use SVG flags or flag-icons",
    "country-flag-emoji-polyfill": "draws flags as emoji; use SVG flags or flag-icons",
}

PRECOGNITION_ADDON = "laravel-precognition-vue-inertia"


def major(spec: str) -> int | None:
    m = re.search(r"(\d+)", spec or "")
    return int(m.group(1)) if m else None


def check(pkg: dict, allow: set[str]) -> list[tuple[str, str, str]]:
    deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies"):
        deps.update(pkg.get(key) or {})
    names = set(deps) - allow
    out: list[tuple[str, str, str]] = []
    for name in sorted(names & set(AVOID)):
        out.append(("error", "F01", f"{name}: {AVOID[name]}"))
    inertia = major(deps.get("@inertiajs/vue3", ""))
    if PRECOGNITION_ADDON in names and inertia is not None and inertia >= 3:
        out.append(("error", "F01", f"{PRECOGNITION_ADDON}: Inertia 3 has Precognition built in "
                                    "(useForm().withPrecognition(), <Form> validate); remove the add-on"))
    for need, (favorite, families) in NEEDS.items():
        present = {fam: sorted(pkgs & names) for fam, pkgs in families.items() if pkgs & names}
        approved = {fam for fam, pkgs in families.items() if pkgs & allow & set(deps)}
        if len(present) + len(approved - set(present)) > 1:
            listed = ", ".join(p for fam in sorted(present) for p in present[fam])
            if approved:
                listed += ", approved: " + ", ".join(sorted(p for fam in approved for p in families[fam] & allow))
            out.append(("error", "F02", f"two libraries for {need}: {listed}; keep one"))
        elif present and favorite not in present and not approved:
            fam = next(iter(present))
            out.append(("warning", "F03", f"{need} through {', '.join(present[fam])}, not the favorite "
                                          f"{', '.join(sorted(families[favorite]))}; name the ADR or profile "
                                          "that chose it, or pass --allow"))
    return out


def self_test() -> int:
    cases = [
        ("favorites are clean", {"dependencies": {"reka-ui": "^2.11", "@lucide/vue": "^1.70", "vue-sonner": "^2",
                                                  "echarts": "^6", "vue-echarts": "^8", "date-fns": "^4",
                                                  "@date-fns/tz": "^1", "pinia": "^4", "vue-i18n": "^11",
                                                  "@tanstack/vue-table": "^9", "@inertiajs/vue3": "^3"}},
         set(), [], ["F01", "F02", "F03"]),
        ("moment is avoided", {"dependencies": {"moment": "^2"}}, set(), ["F01"], []),
        ("deprecated lucide", {"dependencies": {"lucide-vue-next": "^1"}}, set(), ["F01"], []),
        ("renamed radix-vue", {"devDependencies": {"radix-vue": "^1"}}, set(), ["F01"], []),
        ("emoji flag polyfill", {"dependencies": {"country-flag-emoji-polyfill": "^0.1"}}, set(), ["F01"], []),
        ("precognition add-on on inertia 3", {"dependencies": {"@inertiajs/vue3": "^3.11.0",
                                                               "laravel-precognition-vue-inertia": "^0.8"}},
         set(), ["F01"], []),
        ("precognition add-on on inertia 2 is fine", {"dependencies": {"@inertiajs/vue3": "^2.0.0",
                                                                       "laravel-precognition-vue-inertia": "^0.8"}},
         set(), [], ["F01"]),
        ("two toast libraries", {"dependencies": {"vue-sonner": "^2", "notivue": "^2"}}, set(), ["F02"], ["F03"]),
        ("two icon sets", {"dependencies": {"@lucide/vue": "^1", "@heroicons/vue": "^2"}}, set(), ["F02"], []),
        ("second chart library across deps", {"dependencies": {"echarts": "^6", "vue-echarts": "^8"},
                                              "devDependencies": {"@unovis/vue": "^1"}}, set(), ["F02"], []),
        ("family counts once", {"dependencies": {"echarts": "^6", "vue-echarts": "^8"}}, set(), [], ["F02"]),
        ("dates: dayjs next to date-fns", {"dependencies": {"date-fns": "^4", "dayjs": "^1"}}, set(), ["F02"], []),
        ("non-favorite alone warns", {"dependencies": {"chart.js": "^4", "vue-chartjs": "^5"}}, set(), ["F03"],
         ["F02"]),
        ("allow silences the non-favorite", {"dependencies": {"chart.js": "^4"}}, {"chart.js"}, [], ["F03"]),
        ("allow does not hide a duplicate", {"dependencies": {"chart.js": "^4", "echarts": "^6"}}, {"chart.js"},
         ["F02"], []),
        ("allow covers the whole family", {"dependencies": {"chart.js": "^4", "vue-chartjs": "^5"}}, {"chart.js"},
         [], ["F02", "F03"]),
        ("allow of a package not installed changes nothing", {"dependencies": {"echarts": "^6"}}, {"chart.js"},
         [], ["F02", "F03"]),
        ("allow silences avoid list", {"dependencies": {"moment": "^2"}}, {"moment"}, [], ["F01"]),
        ("i18n duplicate", {"dependencies": {"vue-i18n": "^11", "i18next": "^25"}}, set(), ["F02"], []),
        ("flags duplicate", {"dependencies": {"flag-icons": "^7", "country-flag-icons": "^1"}}, set(), ["F02"], []),
    ]
    failed = 0
    for name, pkg, allow, expect, absent in cases:
        got = {code for _, code, _ in check(pkg, allow)}
        if not set(expect) <= got or got & set(absent):
            failed += 1
            print(f"FAIL {name}: got {sorted(got)}, want {sorted(expect)}, not {sorted(absent)}")
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "package.json"
        p.write_text(json.dumps({"dependencies": {"moment": "^2"}}), encoding="utf-8")
        if main([str(p)], quiet=True) != 1:
            failed += 1
            print("FAIL exit code 1 on an error")
        p.write_text(json.dumps({"dependencies": {"vue-sonner": "^2"}}), encoding="utf-8")
        if main([str(p)], quiet=True) != 0:
            failed += 1
            print("FAIL exit code 0 when clean")
        if main([str(Path(t) / "missing.json")], quiet=True) != 2:
            failed += 1
            print("FAIL exit code 2 on a missing file")
    total = len(cases) + 3
    if failed:
        print(f"self-test: {failed} of {total} case(s) failed")
        return 1
    print(f"self-test: {total} case(s) ok")
    return 0


def main(argv: list[str], quiet: bool = False) -> int:
    if "--self-test" in argv:
        return self_test()
    args = list(argv)
    allow: set[str] = set()
    if "--allow" in args:
        i = args.index("--allow")
        if i + 1 >= len(args):
            print("--allow needs a value", file=sys.stderr)
            return 2
        allow = {a.strip() for a in args[i + 1].split(",") if a.strip()}
        del args[i:i + 2]
    paths = [Path(a) for a in args] or [Path("package.json")]
    errors = warns = 0
    for path in paths:
        try:
            pkg = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            if not quiet:
                print(f"cannot read {path}: {e}", file=sys.stderr)
            return 2
        for level, code, msg in check(pkg, allow):
            errors += level == "error"
            warns += level == "warning"
            if not quiet:
                print(f"{path}: {level} {code} {msg}")
    if not quiet:
        print(f"{errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
