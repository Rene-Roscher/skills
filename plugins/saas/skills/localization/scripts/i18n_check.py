#!/usr/bin/env python3
"""Check locale files and source code for user-facing text that cannot be localized well.

Locale files: JSON (vue-i18n, i18next nested or flat), Laravel JSON lang files, and Laravel PHP array
lang files when `php` is on PATH (they are executed with `php -n` to read the array; pass --no-php to
skip them). Checks key parity, placeholder parity, plural forms per language (vue-i18n pipes, Laravel
pipes, i18next suffixes, ICU plural), pseudo-plurals such as "Server(s)", empty and untranslated values.

Source scan (.vue .ts .tsx .js .jsx .mjs .php .blade.php .go), heuristic, warnings only: a count
concatenated with a noun, hand-written plurals, pseudo-plurals in string literals, hard-coded text in
Vue templates and Blade views, literal text in toasts, flashes and aborts, raw exception messages
shown to users, sentences joined from translated fragments. Silence one line with a comment on the
same or the previous line: `i18n-allow: reason` (a reason is required).

Usage:
  i18n_check.py [PATH ...] [--source-locale en] [--plural-rules pl,ru] [--exclude GLOB] [--no-source]
                [--no-locales] [--no-php] [--strict] [--quiet] [--counts]
  i18n_check.py --self-test

Output: `path:line: error|warning CODE message`, then a summary on stderr.

Exit codes:
  0  no errors (warnings may be printed)
  1  at least one error, a warning under --strict, or a failed self-test
  2  usage error: a path does not exist, or nothing to check was found

Python 3.9 or later, standard library only.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

# --- language data ------------------------------------------------------------------------------------

# CLDR cardinal plural categories (CLDR 47, cross-checked with Intl.PluralRules on ICU 77.1, 2026-11-04).
# https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html
CLDR = {
    "ar": "zero one two few many other", "bg": "one other", "cs": "one few many other", "da": "one other",
    "de": "one other", "el": "one other", "en": "one other", "es": "one many other", "et": "one other",
    "fi": "one other", "fr": "one many other", "ga": "one two few many other", "hr": "one few other",
    "hu": "one other", "it": "one many other", "ja": "other", "lt": "one few many other",
    "lv": "zero one other", "mt": "one two few many other", "nb": "one other", "nl": "one other",
    "pl": "one few many other", "pt": "one many other", "ro": "one few other", "ru": "one few many other",
    "sk": "one few many other", "sl": "one two few other", "sv": "one other", "tr": "one other",
    "uk": "one few many other",
}
CLDR = {k: v.split() for k, v in CLDR.items()}

# Categories an integer count reaches (Intl.PluralRules over 0..1100 and 10^6, 2*10^6, 10^7). In pl, ru
# and uk "other" is for fractions only; in cs and sk "many" is for fractions only.
INTEGER = {
    "ar": "zero one two few many other", "cs": "one few other", "sk": "one few other",
    "es": "one other many", "fr": "one other many", "it": "one other many", "pt": "one other many",
    "ga": "one two few many other", "hr": "one few other", "ja": "other", "lt": "one few other",
    "lv": "zero one other", "mt": "one two few many other", "pl": "one few many", "ro": "one few other",
    "ru": "one few many", "sl": "one two few other", "uk": "one few many",
}
INTEGER = {k: INTEGER.get(k, " ".join(v)).split() for k, v in CLDR.items()}
# "many" in these languages is reached only from 1,000,000 up: a missing form is a warning.
MILLIONS_ONLY_MANY = {"es", "fr", "it", "pt"}
# CLDR puts 0 in "one" here; vue-i18n's built-in rule (11.x) puts 0 in the plural form.
ZERO_IS_ONE = {"fr", "pt"}

# Segments Laravel's MessageSelector::getPluralIndex can select (laravel/framework 12.53.0,
# src/Illuminate/Translation/MessageSelector.php, run over 0..1100 and 10^6). Unknown locales,
# including hyphenated ones such as de-DE, always get segment 0.
LARAVEL_SEGMENTS = {
    "ar": 6, "bg": 2, "cs": 3, "da": 2, "de": 2, "el": 2, "en": 2, "es": 2, "et": 2, "fi": 2, "fr": 2,
    "ga": 3, "hr": 3, "hu": 2, "it": 2, "ja": 1, "lt": 3, "lv": 3, "mt": 4, "nb": 2, "nl": 2, "pl": 3,
    "pt": 2, "ro": 3, "ru": 3, "sk": 3, "sl": 4, "sv": 2, "tr": 1, "uk": 3,
}

ISO639_1 = set("""aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu cv
cy da de dv dz ee el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he hi ho hr ht hu hy hz ia id ie
ig ii ik io is it iu ja jv ka kg ki kj kk kl km kn ko kr ks ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk
ml mn mr ms mt my na nb nd ne ng nl nn no nr nv ny oc oj om or os pa pi pl ps pt qu rm rn ro ru rw sa sc sd se
sg si sk sl sm sn so sq sr ss st su sv sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo
xh yi yo za zh zu""".split())
LOCALE_RE = re.compile(r"^([a-z]{2,3})(?:[-_](?:[A-Za-z]{2}|\d{3}|[A-Z][a-z]{3}|ploc[am]?|X[AB]))*$")
LOCALE_DIR_NAMES = {"lang", "langs", "locales", "locale", "i18n", "l10n", "translations", "messages"}
PSEUDO_LOCALES = {"qps", "qps-ploc", "qps-plocm", "qps-ploca", "en-XA", "en-XB"}

# Laravel ships English lines for these files inside the framework, so lang/en may hold fewer keys.
LARAVEL_FRAMEWORK_FILES = {"auth.php", "pagination.php", "passwords.php", "validation.php"}

SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".nuxt", ".output", "coverage", "storage",
             "__pycache__", ".venv", "bootstrap", "public", ".idea", ".vscode", "tmp", "cache"}
SOURCE_EXT = (".vue", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".php", ".go")
SKIP_SOURCE_SUFFIX = (".d.ts", ".min.js", ".spec.ts", ".test.ts", ".spec.js", ".test.js", "_test.go",
                      "Test.php")


def is_locale(name: str) -> bool:
    if name in PSEUDO_LOCALES:
        return True
    m = LOCALE_RE.match(name)
    return bool(m) and m.group(1) in ISO639_1


def base_lang(locale: str) -> str:
    return re.split(r"[-_]", locale, maxsplit=1)[0].lower()


def is_pseudo(locale: str) -> bool:
    return locale in PSEUDO_LOCALES or base_lang(locale) == "qps"


# --- findings -----------------------------------------------------------------------------------------

class Report:
    def __init__(self, root: Path):
        self.root = root
        self.items: list[tuple[str, int, str, str, str]] = []
        self.notes: list[str] = []
        self._once: set[str] = set()

    def rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return p.as_posix()

    def add(self, path, line, level, code, msg):
        self.items.append((self.rel(path) if isinstance(path, Path) else path, line, level, code, msg))

    def err(self, path, line, code, msg):
        self.add(path, line, "error", code, msg)

    def warn(self, path, line, code, msg):
        self.add(path, line, "warning", code, msg)

    def once(self, key: str) -> bool:
        if key in self._once:
            return False
        self._once.add(key)
        return True

    @property
    def errors(self):
        return sum(1 for i in self.items if i[2] == "error")

    @property
    def warnings(self):
        return sum(1 for i in self.items if i[2] == "warning")


# --- value analysis -----------------------------------------------------------------------------------

LETTER = "A-Za-zÀ-ÖØ-öø-ÿĀ-žА-я"
# "Server(s)", "Zertifikat(e)", "Datei(en)", "item(s)", "Server/n", "Zertifikat/e", "item/s"
PSEUDO_PAREN_RE = re.compile(rf"(?<![.\w$])[{LETTER}]{{3,}}\((?:s|e|en|n|es|er|nen|ies)\)")
PSEUDO_SLASH_RE = re.compile(rf"\b([{LETTER}]{{3,}})/(s|e|en|n|es)\b(?![/\w])")
SLASH_S_UNITS = {"bytes", "byte", "bit", "bits", "kbit", "mbit", "gbit", "req", "ops", "frames", "fps",
                 "mib", "kib", "gib", "events", "requests", "anfragen", "zugriffe", "calls", "checks"}


def pseudo_plurals(text: str) -> list[str]:
    hits = [m.group(0) for m in PSEUDO_PAREN_RE.finditer(text) if m.group(0).lower() != "http(s)"]
    for m in PSEUDO_SLASH_RE.finditer(text):
        word, suffix = m.group(1), m.group(2)
        if suffix == "s" and (word.lower() in SLASH_S_UNITS or word.isupper() or word.lower().endswith(("s", "bit"))):
            continue  # "MB/s", "Requests/s": a rate, not a plural
        hits.append(m.group(0))
    return hits


VUE_LITERAL_RE = re.compile(r"\{\s*'[^']*'\s*\}")
ICU_HEAD_RE = re.compile(r"\{\s*([A-Za-z_]\w*)\s*,\s*(plural|selectordinal|select)\s*,")
ICU_TOKEN_RE = re.compile(r"offset:\s*\d+|=-?\d+(?:\.\d+)?|[A-Za-z_]\w*")
PH_BRACE_RE = re.compile(r"\{\s*([A-Za-z_][\w.]*|\d+)\s*\}")
PH_DOUBLE_RE = re.compile(r"\{\{\s*-?\s*([A-Za-z_][\w.]*)\s*(?:,[^}]*)?\}\}")
PH_COLON_RE = re.compile(r"(?<![\w:\\]):([A-Za-z_][A-Za-z0-9_]*)")
CODEISH_VALUE_RE = re.compile(r"://|@|\$|=|`|<[a-z/]|-----|\\")
CODEISH_KEY_RE = re.compile(r"placeholder|(?:^|_)ph(?:_|$)|url|example|env|snippet|code|command|regex", re.I)
LARAVEL_COND_RE = re.compile(r"^\s*[\{\[][-?\d|*,.]*[\}\]]")


def icu_blocks(msg: str):
    """Yield (argument, kind, selectors, ok) for each ICU plural/select argument, nested ones included."""
    for m in ICU_HEAD_RE.finditer(msg):
        i, n, sels, ok = m.end(), len(msg), [], True
        while i < n:
            while i < n and msg[i].isspace():
                i += 1
            if i >= n or msg[i] == "}":
                break
            t = ICU_TOKEN_RE.match(msg, i)
            if not t:
                ok = False
                break
            i = t.end()
            if t.group(0).startswith("offset:"):
                continue
            while i < n and msg[i].isspace():
                i += 1
            if i >= n or msg[i] != "{":
                ok = False
                break
            depth, j = 0, i
            while j < n:
                if msg[j] == "{":
                    depth += 1
                elif msg[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            if depth != 0:
                ok = False
                break
            sels.append(t.group(0))
            i = j + 1
        if i >= n:
            ok = False  # no closing brace for the argument
        yield m.group(1), m.group(2), sels, ok


def placeholders(value: str, laravel: bool) -> set[str]:
    if laravel:  # Laravel knows only :name; {0} and [2,*] are plural intervals
        v = "|".join(LARAVEL_COND_RE.sub("", seg) for seg in value.split("|"))
        return {":" + m.group(1).lower() for m in PH_COLON_RE.finditer(v)}
    v = VUE_LITERAL_RE.sub("", value)
    names = {m.group(1) for m in ICU_HEAD_RE.finditer(v)}
    names |= {"{{" + m.group(1) for m in PH_DOUBLE_RE.finditer(v)}
    names |= {m.group(1) for m in PH_BRACE_RE.finditer(PH_DOUBLE_RE.sub("", v))}
    return names


def pipe_forms(value: str) -> list[str]:
    """vue-i18n plural forms: split on '|' outside literal interpolation such as {'|'}."""
    return [f.strip() for f in VUE_LITERAL_RE.sub("_", value).split("|")]


def words(value: str) -> int:
    v = PH_DOUBLE_RE.sub(" ", value)
    v = PH_BRACE_RE.sub(" ", v)
    v = PH_COLON_RE.sub(" ", v)
    return len(re.findall(rf"[{LETTER}]{{3,}}", v))


# --- locale files -------------------------------------------------------------------------------------

def flatten(obj, prefix=()):
    out = {}
    if isinstance(obj, dict) and obj:
        for k, v in obj.items():
            out.update(flatten(v, prefix + (str(k),)))
    elif isinstance(obj, list) and obj:
        for i, v in enumerate(obj):
            out.update(flatten(v, prefix + (str(i),)))
    else:
        out[prefix] = obj
    return out


def key_line(lines: list[str], parts: tuple) -> int:
    idx = 0
    for part in parts:
        rx = re.compile(r"[\"']" + re.escape(part) + r"[\"']\s*(?::|=>)")
        for j in range(idx, len(lines)):
            if rx.search(lines[j]):
                idx = j
                break
        else:
            return idx + 1
    return idx + 1


PHP_LOADER = r"""
$out = [];
foreach (array_slice($argv, 1) as $f) {
    try { $v = (static function ($__f) { return include $__f; })($f); $out[$f] = is_array($v) ? $v : null; }
    catch (\Throwable $e) { $out[$f] = null; }
}
echo json_encode($out, JSON_UNESCAPED_UNICODE | JSON_PARTIAL_OUTPUT_ON_ERROR);
"""


def load_php(files: list[Path]) -> dict[str, object]:
    php = shutil.which("php")
    if not php or not files:
        return {}
    out: dict[str, object] = {}
    for start in range(0, len(files), 200):
        chunk = [str(f.resolve()) for f in files[start:start + 200]]
        try:
            res = subprocess.run([php, "-n", "-d", "display_errors=stderr", "-r", PHP_LOADER, *chunk],
                                 capture_output=True, timeout=120, check=False)
            out.update(json.loads(res.stdout.decode("utf-8") or "{}"))
        except (OSError, subprocess.TimeoutExpired, ValueError):
            pass
    return out


def discover_locales(root: Path) -> dict[tuple[str, str], dict[str, Path]]:
    """Group locale files: (group dir, relative file) -> {locale: path}."""
    groups: dict[tuple[str, str], dict[str, Path]] = defaultdict(dict)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        d = Path(dirpath)
        named = [f for f in filenames if f.endswith(".json") and is_locale(f[:-5])]
        if len(named) >= 2 or (named and d.name in LOCALE_DIR_NAMES):
            for f in named:
                groups[(str(d), "[locale].json")][f[:-5]] = d / f
        loc_dirs = [x for x in dirnames if is_locale(x)]
        if len(loc_dirs) >= 2 or (loc_dirs and d.name in LOCALE_DIR_NAMES):
            for ld in loc_dirs:
                for sub, _, files in os.walk(d / ld):
                    for f in files:
                        if f.endswith((".json", ".php")):
                            p = Path(sub) / f
                            groups[(str(d), (p.relative_to(d / ld)).as_posix())][ld] = p
            dirnames[:] = [x for x in dirnames if x not in loc_dirs]
    return groups


def plural_base_key(key: tuple) -> tuple[tuple, str | None]:
    last = key[-1]
    m = re.match(r"^(.*?)_(zero|one|two|few|many|other)$", last)
    if m and "_ordinal" not in last:
        return key[:-1] + (m.group(1),), m.group(2)
    return key, None


def check_locales(root: Path, rep: Report, source_locale: str | None, use_php: bool,
                  declared_rules: set[str]) -> int:
    groups = discover_locales(root)
    php_files = [p for g in groups.values() for p in g.values() if p.suffix == ".php"]
    php_data: dict[str, object] = {}
    if php_files:
        if not use_php:
            rep.notes.append(f"{len(php_files)} PHP lang file(s) not checked (--no-php)")
        elif not shutil.which("php"):
            rep.notes.append(f"{len(php_files)} PHP lang file(s) not checked (php is not on PATH)")
        else:
            php_data = load_php(php_files)
    checked_files = 0
    dir_locales: dict[str, set[str]] = defaultdict(set)
    layout = lambda relf: "named" if relf == "[locale].json" else "dirs"  # noqa: E731
    for (gdir, relf), by_locale in groups.items():
        dir_locales[gdir + layout(relf)] |= set(by_locale)
    for (gdir, relf), by_locale in sorted(groups.items()):
        for loc in sorted(dir_locales[gdir + layout(relf)] - set(by_locale)):
            if is_pseudo(loc) or (relf in LARAVEL_FRAMEWORK_FILES and base_lang(loc) == "en"):
                continue
            first = by_locale[sorted(by_locale)[0]]
            rep.err(first, 1, "I02", f"{relf} exists for {', '.join(sorted(by_locale))} but not for {loc}")
        laravel = relf.endswith(".php") or (relf == "[locale].json" and Path(gdir).name in {"lang", "langs"})
        data: dict[str, dict[tuple, object]] = {}
        lines: dict[str, list[str]] = {}
        for loc, path in sorted(by_locale.items()):
            if path.suffix == ".php":
                raw = php_data.get(str(path.resolve()))
                if raw is None:
                    if php_data:
                        rep.warn(path, 1, "I10", "PHP lang file could not be loaded; not checked")
                    continue
                if raw == [] or raw == {}:
                    raw = {}
            else:
                try:
                    raw = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, ValueError) as e:
                    rep.err(path, 1, "I01", f"cannot parse: {e}")
                    continue
            if not isinstance(raw, (dict, list)):
                rep.err(path, 1, "I01", "top level is not an object")
                continue
            data[loc] = flatten(raw) if raw else {}
            data[loc].pop((), None)
            try:
                lines[loc] = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                lines[loc] = []
            checked_files += 1
        if not data:
            continue
        framework = relf in LARAVEL_FRAMEWORK_FILES
        check_group(rep, by_locale, data, lines, laravel, source_locale, declared_rules, framework)
    return checked_files


def check_group(rep, by_locale, data, lines, laravel, source_locale, declared_rules, framework=False):
    locales = sorted(data)
    src = source_locale if source_locale in data else ("en" if "en" in data else locales[0])
    i18next = False
    for d in data.values():
        cats_by_base: dict[tuple, set[str]] = defaultdict(set)
        for k in d:
            b, cat = plural_base_key(k)
            if cat:
                cats_by_base[b].add(cat)
        if any("other" in c and len(c) > 1 for c in cats_by_base.values()):
            i18next = True

    # normalized keys: i18next plural suffixes collapse to their base key
    norm: dict[str, dict[tuple, list[tuple]]] = {}
    for loc in locales:
        groups: dict[tuple, list[tuple]] = defaultdict(list)
        for k in data[loc]:
            base, cat = plural_base_key(k) if i18next else (k, None)
            groups[base if cat else k].append(k)
        norm[loc] = groups

    for loc in locales:
        path, ln, base = by_locale[loc], lines[loc], base_lang(loc)
        d = data[loc]
        if loc != src and not is_pseudo(loc):
            missing = sorted(set(norm[src]) - set(norm[loc]))
            extra = sorted(set(norm[loc]) - set(norm[src]))
            for k in missing:
                rep.err(path, 1, "I02", f"key '{'.'.join(k)}' exists in {src} but not in {loc}")
            for k in ([] if framework and base_lang(src) == "en" else extra):
                rep.err(path, key_line(ln, k), "I03", f"key '{'.'.join(k)}' exists in {loc} but not in {src}")

        for nk, keys in norm[loc].items():
            values = [d[k] for k in keys]
            line = key_line(ln, keys[0])
            dotted = ".".join(nk)
            for k, v in zip(keys, values):
                if v is None or (isinstance(v, str) and not v.strip()) or v in ({}, []):
                    rep.err(path, key_line(ln, k), "I07", f"'{'.'.join(k)}' is empty")
            strings = [v for v in values if isinstance(v, str)]
            if not strings:
                continue
            joined = " | ".join(strings)
            for hit in pseudo_plurals(joined):
                rep.err(path, line, "I06", f"'{dotted}' has the pseudo-plural '{hit}'; use plural forms")

            # placeholder parity against the source locale
            if loc != src and nk in norm[src] and not is_pseudo(loc):
                src_vals = [data[src][k] for k in norm[src][nk] if isinstance(data[src][k], str)]
                a = set().union(*(placeholders(v, laravel) for v in src_vals)) if src_vals else set()
                b = set().union(*(placeholders(v, laravel) for v in strings))
                if a != b:
                    miss, more = sorted(a - b), sorted(b - a)
                    parts = ([f"missing {', '.join(miss)}"] if miss else []) + ([f"extra {', '.join(more)}"] if more else [])
                    rep.err(path, line, "I04", f"'{dotted}' placeholders differ from {src}: {'; '.join(parts)}")
                if (len(src_vals) == 1 and len(strings) == 1 and src_vals[0] == strings[0]
                        and base_lang(src) != base and words(strings[0]) >= 3
                        and not CODEISH_VALUE_RE.search(strings[0]) and not CODEISH_KEY_RE.search(dotted)):
                    rep.warn(path, line, "I08", f"'{dotted}' is identical to {src}; untranslated?")

            if base not in CLDR or is_pseudo(loc):
                continue
            # ICU plural arguments
            for s in strings:
                for arg, kind, sels, ok in icu_blocks(s):
                    if not ok:
                        rep.err(path, line, "I05", f"'{dotted}': ICU argument '{arg}' does not parse")
                        continue
                    if kind == "select":
                        if "other" not in sels:
                            rep.err(path, line, "I05", f"'{dotted}': ICU select '{arg}' has no 'other'")
                        continue
                    if "other" not in sels:
                        rep.err(path, line, "I05", f"'{dotted}': ICU {kind} '{arg}' has no 'other' case")
                    if kind == "selectordinal":
                        continue
                    for cat in INTEGER[base]:
                        if cat not in sels and cat != "other":
                            level = "warn" if (cat == "many" and base in MILLIONS_ONLY_MANY) else "err"
                            getattr(rep, level)(path, line, "I05", f"'{dotted}': ICU plural '{arg}' lacks "
                                                f"'{cat}', which {loc} uses for whole numbers")
                    for cat in sels:
                        if not cat.startswith("=") and cat not in CLDR[base]:
                            rep.warn(path, line, "I05", f"'{dotted}': '{cat}' is never selected in {loc}")
            if any(ICU_HEAD_RE.search(s) for s in strings):
                continue
            # i18next suffix plurals
            if i18next and plural_base_key(keys[0])[1]:
                cats = {plural_base_key(k)[1] for k in keys} - {None}
                if cats:
                    for cat in INTEGER[base]:
                        if cat not in cats:
                            level = "warn" if (cat == "many" and base in MILLIONS_ONLY_MANY) else "err"
                            getattr(rep, level)(path, line, "I05", f"'{dotted}' lacks the _{cat} form {loc} needs")
                    for cat in sorted(cats - set(CLDR[base]) - {"zero"}):
                        rep.warn(path, line, "I05", f"'{dotted}_{cat}' is never selected in {loc}")
                continue
            s = strings[0]
            if laravel:
                check_laravel_pipes(rep, path, line, dotted, loc, base, s)
            elif "|" in VUE_LITERAL_RE.sub("", s):
                check_vue_pipes(rep, path, line, dotted, loc, base, s, src, data, norm, nk, declared_rules)
            elif loc != src and nk in norm[src]:
                sv = data[src].get(norm[src][nk][0])
                if isinstance(sv, str) and not laravel and len(pipe_forms(sv)) > 1:
                    rep.warn(path, line, "I05", f"'{dotted}' has plural forms in {src} but one form in {loc}; "
                                                "fine only if every count reads the same")


def check_vue_pipes(rep, path, line, dotted, loc, base, s, src, data, norm, nk, declared_rules):
    forms = pipe_forms(s)
    need = len([c for c in INTEGER[base] if not (c == "many" and base in MILLIONS_ONLY_MANY)])
    if len(forms) < need:
        rep.err(path, line, "I05", f"'{dotted}' has {len(forms)} plural forms; {loc} needs {need} "
                                   f"({', '.join(INTEGER[base])})")
    elif need <= 2 and len(forms) > 3:
        rep.warn(path, line, "I05", f"'{dotted}': forms after the third are never selected by the default rule")
    if (need > 2 or base in ZERO_IS_ONE) and base not in declared_rules and rep.once("I09" + base):
        why = ("0 is 'one' in CLDR " + base) if base in ZERO_IS_ONE else f"{loc} has {need} integer forms"
        rep.warn(path, line, "I09", f"vue-i18n 11.x picks plural forms by an English rule unless pluralRules has "
                                    f"an entry for {base} ({why}); declare it with --plural-rules {base}")
    if loc != src and nk in norm[src]:
        sv = data[src].get(norm[src][nk][0])
        if isinstance(sv, str) and len(pipe_forms(sv)) == 1:
            rep.warn(path, line, "I05", f"'{dotted}' has plural forms in {loc} but one form in {src}")


def check_laravel_pipes(rep, path, line, dotted, loc, base, s):
    segs = s.split("|")
    if len(segs) < 2:
        return
    conds = [bool(LARAVEL_COND_RE.match(x)) for x in segs]
    if any(conds) and not all(conds):
        rep.err(path, line, "I05", f"'{dotted}' mixes interval and plain segments; Laravel then picks plain "
                                   "segments by index and shows the wrong form. Give every segment an interval")
        return
    if all(conds):
        return
    if "-" in loc:
        if rep.once("I05-hyphen" + loc):
            rep.err(path, line, "I05", f"Laravel's plural selector does not know the locale '{loc}' and always "
                                       f"picks the first segment; use '{loc.replace('-', '_')}' or '{base}'")
        return
    need = LARAVEL_SEGMENTS.get(base)
    if need and len(segs) < need:
        rep.err(path, line, "I05", f"'{dotted}' has {len(segs)} segments; Laravel selects {need} for {loc}, "
                                   "a missing segment falls back to the first one")


# --- source scan --------------------------------------------------------------------------------------

ALLOW_RE = re.compile(r"i18n-allow:\s*\S")
DEV_LINE_RE = re.compile(r"\b(?:console\.\w+|Log::\w+|logger\(|->(?:debug|info|notice|warning|error|critical)\("
                         r"|log\.\w+\(|slog\.\w+\(|fmt\.Errorf|errors\.New|t\.(?:Errorf|Fatalf|Logf)|panic\("
                         r"|throw new \w*Exception|\$this->(?:info|line|comment|warn|error)\()")
COMMENT_RE = re.compile(r"^\s*(?://|#(?!\[)|\*|/\*|<!--|\{\{--)")
COUNTISH_RE = re.compile(r"(?:count|total|length|size|num|amount|qty|anzahl|menge)\w*\W*$|^\s*\$?n\s*$", re.I)
NOUN = rf"[{LETTER}]{{2,}}"
UNIT_WORDS = {"ms", "px", "em", "rem", "vh", "vw", "kb", "mb", "gb", "tb", "min", "sec", "fps", "pt", "x"}
STRING_RE = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\\n]|\\.)*)`")
KEYISH_RE = re.compile(r"^[\w-]+(?:\.[\w-]+)+$|^[\w-]+::[\w.-]+$|^[a-z0-9]+(?:[-_][a-z0-9]+)+$")

S01_RES = [
    re.compile(r"\$\{\s*([^}]+?)\s*\}\s+(" + NOUN + ")"),                                   # `${count} items`
    re.compile(r"([\w$.?\[\]()>-]+)\s*\+\s*['\"`]\s+(" + NOUN + ")"),                       # count + ' items'
    re.compile(r"(\$[\w>()\[\]'\"-]+|count\(\$\w+\))\s*\.\s*['\"]\s+(" + NOUN + ")"),       # $count . ' Server'
    re.compile(r"\"[^\"\n]*?\{?(\$[\w>-]+)\}?\s+(" + NOUN + ")[^\"\n]*\""),                 # "{$count} Server"
    re.compile(r"\{\{\s*([^}]+?)\s*\}\}\s+(" + NOUN + ")"),                                  # {{ n }} Server
    re.compile(r"(?:Sprintf|Printf|sprintf|printf)\(\s*[\"'`][^\"'`\n]*?(%d)\s+(" + NOUN + ")"),  # "%d servers"
    re.compile(r"(strconv\.Itoa\([^)]*\)|fmt\.Sprint\([^)]*\))\s*\+\s*\"\s+(" + NOUN + ")"),
    # a count glued to a translated fragment: `${n} ` + t('...'), $count . ' ' . __('...')
    re.compile(r"(?:\$\{\s*([^}]+?)\s*\}\s*`|([\w$.?\[\]()>-]+))\s*\+\s*(\$?t|i18n\.t|__|trans)\("),
    re.compile(r"(\$[\w>()\[\]-]+)\s*\.\s*(?:['\"]\s*['\"]\s*\.\s*)?(__|trans)\("),
]
# two translations joined into one sentence
S07_RE = re.compile(r"\b(?:\$?t|__|trans)\([^()]*\)(?:\s*(?:\+|\.)\s*(?:['\"`][^'\"`]*['\"`]|[\w$>-]+))*?"
                    r"\s*(?:\+|\.)\s*(?:\$?t|__|trans)\(")
S02_RES = [  # count === 1 ? 'Server' : 'Servers' (both branches share a word stem)
    re.compile(r"(?:===?|!==?|<=?|>=?)\s*1\s*\)?\s*\?\s*['\"`]([^'\"`\n]*?([A-Za-zÀ-ÿ]{3})[^'\"`\n]*)['\"`]"
               r"\s*:\s*['\"`][^'\"`\n]*?\2"),
    re.compile(r"\b(?:Str::plural|str_plural|Str::pluralStudly|pluralize)\s*\("),
]
S05_RES = [
    re.compile(r"\b(?:toast|notify|notification|snackbar|alert|confirm|flash)(?:\.\w+)?\(\s*(['\"`])(.*?)\1"),
    re.compile(r"->with\(\s*['\"](?:success|error|status|message|warning|info|flash|toast|notice)['\"]\s*,\s*"
               r"(['\"])(.*?)\1"),
    re.compile(r"\babort\(\s*\d{3}\s*,\s*(['\"])(.*?)\1"),
    re.compile(r"(?:withErrors|withMessages)\(\s*\[\s*['\"][\w.*]+['\"]\s*=>\s*(['\"])(.*?)\1"),
]
S06_PHP_RE = re.compile(r"(?<!__\()(?<!trans\()\$\w+->getMessage\(\)")
S06_PHP_CTX_RE = re.compile(r"response\(|->json\(|->with\(|withErrors|withMessages|abort\(|toast|flash|Notification")
S06_JS_RE = re.compile(r"\b(?:toast|notify|alert|snackbar|flash|message)\w*(?:\.\w+)?\([^\n]*?"
                       r"\b(?:e|err|error|ex|exception)\.message\b")
S06_GO_RE = re.compile(r"http\.Error\([^,]+,\s*\w+\.Error\(\)")
ATTR_RE = re.compile(r"(?<![:@#\w.-])(placeholder|title|alt|aria-label|label|tooltip|description|hint|heading|"
                     r"subtitle|empty-text|confirm-text|cancel-text|submit-text|helper-text)\s*=\s*\"([^\"]*)\"")
TEXT_RE = re.compile(rf"[{LETTER}]{{2,}}")
UNIT_TOKENS = {"ms", "s", "min", "h", "px", "kb", "mb", "gb", "tb", "kib", "mib", "gib", "std", "sek", "km", "kg"}
EXAMPLE_VALUE_RE = re.compile(r"://|@|-----|^\s*[\w.+-]+\.(?:com|org|net|de|io)\b")


def readable_words(text: str) -> list[str]:
    """Words a translator would touch: not units, not acronyms such as PDF or HTTP."""
    return [w for w in TEXT_RE.findall(text)
            if w.lower() not in UNIT_TOKENS and not (w.isupper() and len(w) <= 6)]


def allowed(lines: list[str], idx: int) -> bool:
    return any(0 <= j < len(lines) and ALLOW_RE.search(lines[j]) for j in (idx, idx - 1))


def blank(s: str, start: int, end: int) -> str:
    return s[:start] + re.sub(r"[^\n]", " ", s[start:end]) + s[end:]


def blank_all(s: str, rx: re.Pattern) -> str:
    for m in reversed(list(rx.finditer(s))):
        s = blank(s, m.start(), m.end())
    return s


def markup_parts(s: str):
    """Yield (kind, offset, text) for text nodes and tags, tracking quotes inside tags."""
    i, n, text_start = 0, len(s), 0
    while i < n:
        if s[i] == "<" and i + 1 < n and (s[i + 1].isalpha() or s[i + 1] in "/!"):
            if i > text_start:
                yield "text", text_start, s[text_start:i]
            j, quote = i + 1, None
            while j < n:
                c = s[j]
                if quote:
                    if c == quote:
                        quote = None
                elif c in "\"'":
                    quote = c
                elif c == ">":
                    break
                j += 1
            yield "tag", i, s[i:j + 1]
            i = text_start = j + 1
            continue
        i += 1
    if text_start < n:
        yield "text", text_start, s[text_start:]


BLOCK_RES = [re.compile(r"<(script|style|code|pre|kbd|svg|samp)\b.*?</\1\s*>", re.S | re.I),
             re.compile(r"<!--.*?-->", re.S)]
MUSTACHE_RE = re.compile(r"\{\{.*?\}\}|\{!!.*?!!\}", re.S)
BLADE_RES = [re.compile(r"\{\{--.*?--\}\}", re.S), re.compile(r"@php\b.*?@endphp", re.S),
             re.compile(r"<\?php.*?(?:\?>|\Z)", re.S), re.compile(r"@verbatim\b.*?@endverbatim", re.S),
             re.compile(r"@\w+\s*(?:\((?:[^()'\"]|'[^']*'|\"[^\"]*\"|\((?:[^()]|\([^()]*\))*\))*\))?")]


def template_text(rep, path, lines, region: str, offset_line: int, blade: bool):
    s = region
    if blade:
        for rx in BLADE_RES:
            s = blank_all(s, rx)
    for rx in BLOCK_RES:
        s = blank_all(s, rx)
    for m in MUSTACHE_RE.finditer(s):
        for lit in STRING_RE.finditer(m.group(0)):
            for hit in pseudo_plurals(next(g for g in lit.groups() if g is not None)):
                ln = offset_line + s.count("\n", 0, m.start())
                if not allowed(lines, ln - 1):
                    rep.warn(path, ln, "S03", f"pseudo-plural '{hit}' in a template expression")
    s = blank_all(s, MUSTACHE_RE)
    for kind, off, text in markup_parts(s):
        if kind == "text":
            if not readable_words(text) or EXAMPLE_VALUE_RE.search(text.strip()):
                continue
            for hit in pseudo_plurals(text):
                ln = offset_line + s.count("\n", 0, off + text.find(hit))
                if not allowed(lines, ln - 1):
                    rep.warn(path, ln, "S03", f"pseudo-plural '{hit}' in markup text")
            for m in TEXT_RE.finditer(text):
                if text[:m.start()].rstrip().endswith("&") and text[m.end():m.end() + 1] == ";":
                    continue  # an entity such as &nbsp;
                if m.group(0) not in readable_words(m.group(0)):
                    continue
                ln = offset_line + s.count("\n", 0, off + m.start())
                if not allowed(lines, ln - 1):
                    snippet = " ".join(text.split())[:50]
                    rep.warn(path, ln, "S04", f"hard-coded text in markup: '{snippet}'")
                break
        else:
            for m in ATTR_RE.finditer(text):
                val = m.group(2)
                if readable_words(val) and not KEYISH_RE.match(val) and not EXAMPLE_VALUE_RE.search(val):
                    ln = offset_line + s.count("\n", 0, off + m.start())
                    if not allowed(lines, ln - 1):
                        rep.warn(path, ln, "S04", f"hard-coded {m.group(1)}=\"{' '.join(val.split())[:40]}\"")


def scan_source(path: Path, rep: Report) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    lines = text.splitlines()
    name = path.name
    blade = name.endswith(".blade.php")
    vue = name.endswith(".vue")
    php = name.endswith(".php") and not blade
    go = name.endswith(".go")

    code_lines = set(range(len(lines)))
    if vue:
        m = re.search(r"<template\b[^>]*>(.*)</template>", text, re.S)
        if m:
            start_line = text.count("\n", 0, m.start(1))
            template_text(rep, path, lines, m.group(1), start_line + 1, blade=False)
            end_line = text.count("\n", 0, m.end(1))
            code_lines -= set(range(start_line, end_line + 1))
    elif blade:
        template_text(rep, path, lines, text, 1, blade=True)

    for i, line in enumerate(lines):
        if COMMENT_RE.match(line) or DEV_LINE_RE.search(line) or allowed(lines, i):
            continue
        n = i + 1
        in_code = i in code_lines
        # S01: a count concatenated with a noun
        for rx in S01_RES:
            m = rx.search(line)
            if not m:
                continue
            groups = [g for g in m.groups() if g is not None]
            expr, noun = groups[0], groups[-1]
            if noun.lower() in UNIT_WORDS:
                continue
            if expr != "%d" and not COUNTISH_RE.search(expr):
                continue
            if rx is S01_RES[4] and in_code and not (blade or vue):
                continue
            rep.warn(path, n, "S01", f"count next to a noun ('{m.group(0).strip()[:60]}'); use one plural message")
            break
        if S07_RE.search(line):
            rep.warn(path, n, "S07", "sentence joined from translated fragments; use one message with placeholders")
        if not in_code:
            continue
        for rx in S02_RES:
            if rx.search(line):
                rep.warn(path, n, "S02", "hand-written plural; use the plural mechanism of the i18n layer")
                break
        for m in STRING_RE.finditer(line):
            lit = re.sub(r"\$\{[^}]*\}", " ", next(g for g in m.groups() if g is not None))
            for hit in pseudo_plurals(lit):
                rep.warn(path, n, "S03", f"pseudo-plural '{hit}' in a string literal")
        for rx in S05_RES:
            m = rx.search(line)
            if m and readable_words(m.group(2)) and not KEYISH_RE.match(m.group(2)):
                rep.warn(path, n, "S05", f"literal user text '{m.group(2)[:50]}'; use a translation key")
                break
        if (php and S06_PHP_RE.search(line) and S06_PHP_CTX_RE.search(line)) or \
                (not php and not go and S06_JS_RE.search(line)) or (go and S06_GO_RE.search(line)):
            rep.warn(path, n, "S06", "raw exception message shown to the user; map it to a code and a translated text")


def walk_sources(root: Path):
    if root.is_file():
        yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
                             and d not in LOCALE_DIR_NAMES - {"messages"}
                             and d not in {"tests", "test", "__tests__", "fixtures", "migrations", "seeders",
                                           "factories", "actions", "routes", "wayfinder"})
        for f in sorted(filenames):
            if f.endswith(SOURCE_EXT) and not f.endswith(SKIP_SOURCE_SUFFIX):
                yield Path(dirpath) / f


# --- run ----------------------------------------------------------------------------------------------

def run(paths: list[Path], args) -> tuple[Report, int, int]:
    root = Path(os.path.commonpath([str(p.resolve()) for p in paths])) if paths else Path.cwd()
    if root.is_file():
        root = root.parent
    rep = Report(root)
    declared = {x.strip() for x in (args.plural_rules or "").split(",") if x.strip()}
    nfiles = nsrc = 0
    for p in paths:
        if not args.no_locales and p.is_dir():
            nfiles += check_locales(p, rep, args.source_locale, not args.no_php, declared)
        if not args.no_source:
            locale_files = {q.resolve() for g in discover_locales(p).values() for q in g.values()} if p.is_dir() else set()
            for f in walk_sources(p):
                if f.resolve() in locale_files:
                    continue
                if any(fnmatch.fnmatch(rep.rel(f), pat) for pat in args.exclude or []):
                    continue
                scan_source(f, rep)
                nsrc += 1
    return rep, nfiles, nsrc


def emit(rep: Report, quiet: bool, counts: bool, nfiles: int, nsrc: int) -> None:
    order = {"error": 0, "warning": 1}
    for path, line, level, code, msg in sorted(rep.items, key=lambda x: (order[x[2]], x[0], x[1], x[3])):
        if quiet and level != "error":
            continue
        print(f"{path}:{line}: {level} {code} {msg}")
    sys.stdout.flush()
    if counts:
        for (level, code), c in sorted(Counter((i[2], i[3]) for i in rep.items).items()):
            print(f"  {code} {level}: {c}", file=sys.stderr)
    for note in rep.notes:
        print(f"note: {note}", file=sys.stderr)
    print(f"{rep.errors} error(s), {rep.warnings} warning(s); {nfiles} locale file(s), {nsrc} source file(s)",
          file=sys.stderr)


# --- self-test ----------------------------------------------------------------------------------------

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def self_test() -> int:
    fails: list[str] = []

    def check(ok, msg):
        if not ok:
            fails.append(msg)

    # 1. units: pseudo-plurals, placeholders, ICU parsing, pipes
    check(pseudo_plurals("1 Server(s) gefunden") == ["Server(s)"], "pseudo: Server(s)")
    check(pseudo_plurals("Zertifikat(e) und Datei(en)") == ["Zertifikat(e)", "Datei(en)"], "pseudo: (e), (en)")
    check(pseudo_plurals("3 item/s") == ["item/s"], "pseudo: item/s")
    check(pseudo_plurals("12 MB/s, 40 Requests/s, 1 Tbit/s, fn(e), fmt.format(s)") == [],
          "pseudo: rates, short calls and method calls are not plurals")
    check(bool(S02_RES[0].search("n === 1 ? 'Server' : 'Servers'")) and
          not S02_RES[0].search("x === 1 ? 'true' : 'false'"), "S02: plural ternary yes, boolean ternary no")
    for line, want in [("t('a.prefix') + ' ' + name + t('a.suffix')", True), ("__('a') . ' ' . __('b')", True),
                       ("{{ t('x') }} {{ t('y') }}", False), ("$t('servers.title').toUpperCase()", False),
                       ("const a = t('x'); const b = t('y')", False)]:
        check(bool(S07_RE.search(line)) == want, f"S07: {line}")
    check(placeholders("Hallo {name}, {{count}} neu", False) == {"name", "{{count"},
          f"placeholders: {placeholders('Hallo {name}, {{count}} neu', False)}")
    check(placeholders("{0} Keine|[2,*] :Count Server, Hinweis: um 10:30", True) == {":count"},
          "placeholders: Laravel intervals, label colon and time are not placeholders")
    check(placeholders("Schreib an support{'@'}example.com", False) == set(),
          "placeholders: literal interpolation is not a placeholder")
    blocks = list(icu_blocks("{count, plural, =0 {Keine Server} one {# Server} other {# Server}}"))
    check(blocks == [("count", "plural", ["=0", "one", "other"], True)], f"icu: {blocks}")
    nested = list(icu_blocks("{g, select, female {{n, plural, one {# x} other {# y}}} other {z}}"))
    check([b[:3] for b in nested] == [("g", "select", ["female", "other"]), ("n", "plural", ["one", "other"])],
          f"icu nested: {nested}")
    check(list(icu_blocks("{n, plural, one {# x} other {# y}"))[0][3] is False, "icu: unbalanced must not parse")
    check(pipe_forms("a {'|'} b | c") == ["a _ b", "c"], "pipes: literal pipe is not a separator")
    check(INTEGER["pl"] == ["one", "few", "many"] and INTEGER["de"] == ["one", "other"], "cldr: integer table")

    # 2. the bad fixture: every expected finding is reported
    class A:  # parsed arguments
        source_locale = None
        plural_rules = ""
        exclude = []
        no_source = no_locales = no_php = False

    rep, nfiles, nsrc = run([FIXTURES / "bad"], A)
    E, W = "error", "warning"
    expect = [  # (file, code, level, text the message must contain)
        ("js/locales/de/servers.json", "I02", E, "'list.legacy'"),
        ("js/locales/de/servers.json", "I03", E, "'list.extra'"),
        ("js/locales/de/servers.json", "I04", E, "missing count"),
        ("js/locales/de/servers.json", "I06", E, "Zertifikat(e)"),
        ("js/locales/de/servers.json", "I07", E, "list.empty"),
        ("js/locales/de/servers.json", "I08", W, "list.summary"),
        ("js/locales/en/billing.json", "I02", E, "exists for en but not for pl"),
        ("js/locales/pl/servers.json", "I05", E, "needs 3"),
        ("js/locales/pl/servers.json", "I09", W, "pluralRules"),
        ("js/locales/fr/servers.json", "I05", E, "has no 'other'"),
        ("i18next/de/translation.json", "I06", E, "Datei(en)"),
        ("i18next/pl/translation.json", "I05", E, "_few"),
        ("lang/de.json", "I04", E, "missing :count"),
        ("lang/de.json", "I06", E, "Server(n)"),
        ("src/ServerList.vue", "S01", W, "servers.length }} Server"),
        ("src/ServerList.vue", "S01", W, "${servers.length} Zertifikat"),
        ("src/ServerList.vue", "S02", W, "hand-written"),
        ("src/ServerList.vue", "S03", W, "markup text"),
        ("src/ServerList.vue", "S03", W, "template expression"),
        ("src/ServerList.vue", "S04", W, "placeholder="),
        ("src/ServerList.vue", "S04", W, "'Löschen'"),
        ("src/ServerList.vue", "S05", W, "Server wurde"),
        ("src/ServerList.vue", "S06", W, "raw exception"),
        ("src/servers.ts", "S01", W, "count + ' servers"),
        ("src/servers.ts", "S03", W, "item(s)"),
        ("src/servers.ts", "S01", W, "${count} ` + t("),
        ("src/servers.ts", "S07", W, "joined from translated"),
        ("src/ServerController.php", "S01", W, "$count . ' Server"),
        ("src/ServerController.php", "S02", W, "hand-written"),
        ("src/ServerController.php", "S05", W, "Dafür fehlt"),
        ("src/ServerController.php", "S06", W, "raw exception"),
        ("src/servers.blade.php", "S01", W, "count() }} Server"),
        ("src/servers.blade.php", "S04", W, "Alle Server"),
        ("src/report.go", "S01", W, "%d servers"),
        ("src/report.go", "S06", W, "raw exception"),
    ]
    if shutil.which("php"):
        expect += [
            ("lang/de/servers.php", "I05", E, "mixes interval"),
            ("lang/pl/servers.php", "I05", E, "Laravel selects 3"),
            ("lang/de/servers.php", "I02", E, "'legacy'"),
            ("lang/de/validation.php", "I02", E, "not for pl"),
        ]
        check(not any("validation.php" in i[4] and "not for en" in i[4] for i in rep.items),
              "laravel: lang/en may omit framework files such as validation.php")
    else:
        check(any("not checked" in n for n in rep.notes), "php missing: a 'not checked' note is expected")
    for f, code, level, text in expect:
        check(any(i[0] == f and i[3] == code and i[2] == level and text in i[4] for i in rep.items),
              f"bad fixture: expected {level} {code} containing {text!r} in {f}")
    check(not any(i[0] == "src/ServerList.vue" and "Brand" in i[4] for i in rep.items),
          "allow comment: the allowed line must not be reported")
    check(not any(i[3] == "I04" for i in rep.items if i[0] == "lang/de/servers.php"),
          "laravel: interval prefixes such as {1} are not placeholders")

    # 3. the clean fixture: nothing at all (false-positive guard)
    rep2, _, _ = run([FIXTURES / "clean"], A)
    for i in rep2.items:
        fails.append(f"clean fixture: unexpected {i[2]} {i[3]} in {i[0]}:{i[1]}: {i[4]}")

    # 4. --plural-rules silences the vue-i18n rule notice
    class B(A):
        plural_rules = "pl,fr"

    rep3, _, _ = run([FIXTURES / "bad"], B)
    check(not any(i[3] == "I09" for i in rep3.items), "--plural-rules must silence I09")

    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print("i18n_check.py self-test: ok (pseudo-plurals, placeholders, ICU, pipes, CLDR table, key parity, "
          "plural forms for vue-i18n, i18next, ICU and Laravel, source heuristics, allow comment, clean fixture)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="i18n_check.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", type=Path, help="directories or files to check (default: .)")
    ap.add_argument("--source-locale", help="locale the others are compared with (default: en, else the first)")
    ap.add_argument("--plural-rules", help="comma list of languages with a registered vue-i18n pluralRules entry")
    ap.add_argument("--no-source", action="store_true", help="skip the source scan")
    ap.add_argument("--no-locales", action="store_true", help="skip locale files")
    ap.add_argument("--no-php", action="store_true", help="never execute PHP lang files")
    ap.add_argument("--exclude", action="append", metavar="GLOB",
                    help="skip source files whose path matches, e.g. 'resources/views/admin/*' (repeatable)")
    ap.add_argument("--strict", action="store_true", help="warnings fail too")
    ap.add_argument("-q", "--quiet", action="store_true", help="print errors only")
    ap.add_argument("--counts", action="store_true", help="print a count per finding code")
    ap.add_argument("--self-test", action="store_true", help="run offline checks against fixtures and exit")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    paths = args.paths or [Path(".")]
    for p in paths:
        if not p.exists():
            print(f"i18n_check.py: {p} does not exist", file=sys.stderr)
            return 2
    rep, nfiles, nsrc = run(paths, args)
    if nfiles == 0 and nsrc == 0 and not rep.items:
        print("i18n_check.py: no locale files and no source files found", file=sys.stderr)
        return 2
    emit(rep, args.quiet, args.counts, nfiles, nsrc)
    if rep.errors or (args.strict and rep.warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
