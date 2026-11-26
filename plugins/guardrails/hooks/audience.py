#!/usr/bin/env python3
"""Warn when an edit puts team-facing text into a file customers read (audience-gate, core plugin).

PostToolUse on Edit, Write and MultiEdit. If the edited file is a locale or content file, the hook checks only
the text the edit added for the clearest audience leaks: roadmap talk (coming in phase 3, in a later version,
not built yet, backlog), provenance notes (according to the code, source: the configuration), feature flags,
placeholders such as [Version] in angle brackets, and TODO markers. Findings come back as additional context,
so the agent sees them before review. The hook never blocks: code comments and tests use the same words.

Locale and content files: .json, .yml, .yaml, .po under a folder named i18n, locales, locale, lang, langs,
translations or messages; .md and .mdx under content, docs, pages, blog or help; any file whose name is a
locale code (de.json, en-US.yml); and page data in code (.ts, .tsx, .js, .jsx, .mjs under a folder named data,
content, copy or texts), where only the prose inside string literals is checked, never comments or code.

The rule list is a deliberate subset of audience_scan.py in the core plugin; the full scan runs on the build.

Usage: audience.py (reads the hook event as JSON on stdin) | audience.py --self-test
Python 3.8 or later, standard library only. Any internal error exits 0 without output.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import PurePath

I = re.I
LOCALE_DIRS = {"i18n", "locales", "locale", "lang", "langs", "translations", "messages"}
CONTENT_DIRS = {"content", "docs", "pages", "blog", "help"}
LOCALE_NAME = re.compile(r"^[a-z]{2}([-_][A-Za-z]{2})?\.(json|ya?ml|po)$")
DATA_DIRS = {"data", "content", "copy", "texts"}
CODE_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs")
STRING = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\]|\\.)*)`", re.S)

RULES = [
    ("roadmap or plan", [
        re.compile(r"\b(Phase|Ausbaustufe|Meilenstein|Sprint|milestone)\s+\d+\b", I),
        re.compile(r"\bkommt (bald|später|demnächst|in Kürze|mit (Version|v?\d|Phase))", I),
        re.compile(r"\b(in|mit) (einer|der) (späteren|kommenden|nächsten) (Version|Ausbaustufe|Release|Fassung)\b", I),
        re.compile(r"\bnoch nicht (gebaut|implementiert|umgesetzt|fertig)\b", I),
        re.compile(r"\b(bald|demnächst|in Kürze) (verfügbar|erhältlich|da)\b|\bavailable soon\b", I),
        re.compile(r"\bcoming (soon|later|in (a|the|version|v?\d|Q[1-4])|with (version|v?\d|phase))", I),
        re.compile(r"\b(in|with) (a|the) (later|future|upcoming|next) (version|release|update|phase)\b", I),
        re.compile(r"\bnot yet (built|implemented|shipped)\b", I),
        re.compile(r"\b(on (the|our) roadmap|auf der Roadmap)\b", I),
        re.compile(r"\b(goes|go|is|sits) (in|into) the backlog\b|\b(wandert|kommt|landet) (erst ?mal |vorerst )?"
                   r"(in den|im) Backlog\b", I),
        re.compile(r"\b(MVP|TBD)\b"),
    ]),
    ("provenance note", [
        re.compile(r"\b(laut|gemäß) (dem |der )?(Quell)?(Code|Konfiguration|Tarifkonfiguration|Spec)\b", I),
        re.compile(r"\bwie (er|sie|es) im (Quell)?[Cc]ode steh", I),
        re.compile(r"\b(according to|as configured in|checked against) (the |our )?(code|codebase|source code|"
                   r"config(uration)?|plan configuration|spec)\b", I),
        re.compile(r"\b(Quelle|Source):\s*(die |the )?[\w-]*(konfiguration|configuration|code)\b", I),
    ]),
    ("feature flag", [re.compile(r"\b(feature[- ]?flag|rollout[- ]?(switch|flag|schalter)|behind a (flag|switch))\b",
                                 I)]),
    ("placeholder", [re.compile(r"<[A-Z][A-Za-z]{2,30}>"), re.compile(r"\blorem ipsum\b", I)]),
    ("work marker", [re.compile(r"\b(TODO|FIXME|XXX)\b")]),
]


def is_reader_file(path: str) -> bool:
    p = PurePath(path)
    dirs = {part.lower() for part in p.parts[:-1]}
    suffix = p.suffix.lower()
    if suffix in (".json", ".yml", ".yaml", ".po") and (dirs & LOCALE_DIRS or LOCALE_NAME.match(p.name)):
        return True
    if suffix in CODE_SUFFIXES:
        return bool(dirs & DATA_DIRS) and not re.search(r"\.(test|spec)\.", p.name)
    return suffix in (".md", ".mdx") and bool(dirs & CONTENT_DIRS)


def added_text(tool: str, tin: dict) -> str:
    if tool == "Write":
        return str(tin.get("content") or "")
    if tool == "Edit":
        return str(tin.get("new_string") or "")
    if tool == "MultiEdit":
        return "\n".join(str(e.get("new_string") or "") for e in tin.get("edits") or [])
    return ""


def prose_strings(text: str) -> str:
    """Keep only string literals that read like sentences: comments and identifiers are written for the team."""
    text = re.sub(r"(?s)/\*.*?\*/", " ", text)
    text = re.sub(r"(?m)(^|[^:'\"`])//.*$", r"\1", text)
    parts = (next(g for g in m.groups() if g is not None) for m in STRING.finditer(text))
    return "\n".join(p for p in parts if len(p.split()) >= 3)


def strip_code(text: str, path: str) -> str:
    if PurePath(path).suffix.lower() in CODE_SUFFIXES:
        return prose_strings(text)
    if PurePath(path).suffix.lower() in (".md", ".mdx"):
        text = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1", " ", text)
        text = re.sub(r"`[^`\n]*`", " ", text)
    return text


def findings(text: str) -> list:
    out = []
    for label, patterns in RULES:
        for pat in patterns:
            m = pat.search(text)
            if m:  # one finding per kind is enough to send the agent back to the text
                start, end = max(0, m.start() - 50), min(len(text), m.end() + 50)
                out.append(f"{label}: …{' '.join(text[start:end].split())}…")
                break
    return out


def handle(ev: dict) -> dict | None:
    if ev.get("hook_event_name") != "PostToolUse":
        return None
    tool = ev.get("tool_name") or ""
    tin = ev.get("tool_input") or {}
    path = str(tin.get("file_path") or "")
    if tool not in ("Edit", "Write", "MultiEdit") or not path or not is_reader_file(path):
        return None
    hits = findings(strip_code(added_text(tool, tin), path))
    if not hits:
        return None
    text = (f"audience check on {PurePath(path).name}: this file is read by customers, and the edit added text "
            "that reads as written for the team. Rewrite it to what the reader can do today, or move the note "
            "into a code comment or the commit message (skill audience-gate):\n- " + "\n- ".join(hits[:8]))
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}


def self_test() -> int:
    ok = True

    def check(label: str, got, want) -> None:
        nonlocal ok
        if got != want:
            ok = False
            print(f"self-test: {label}: got {got!r}, want {want!r}")

    def ev(tool: str, path: str, **tin):
        return handle({"hook_event_name": "PostToolUse", "tool_name": tool,
                       "tool_input": {"file_path": path, **tin}})

    def warned(out) -> bool:
        return bool(out and "audience check" in out["hookSpecificOutput"]["additionalContext"])

    check("phase in locale", warned(ev("Edit", "app/i18n/de.json", new_string='"sso": "SSO kommt mit Phase 3."')),
          True)
    check("later release", warned(ev("Write", "locales/en/faq.json",
                                      content='{"a": "Support follows in a later release."}')), True)
    check("provenance", warned(ev("Edit", "lang/en.json", new_string='"x": "As configured in the code."')), True)
    check("placeholder", warned(ev("Edit", "content/docs/setup.md", new_string="Replace <Version> first.")), True)
    check("todo", warned(ev("MultiEdit", "i18n/en.json", edits=[{"new_string": '"t": "TODO wording"'}])), True)
    check("flag", warned(ev("Edit", "messages/de.json", new_string='"x": "behind a feature flag"')), True)
    check("soon available", warned(ev("Edit", "locales/de/integrations.json", new_string='"x": "Bald verfügbar"')), True)
    check("page data string", warned(ev("Edit", "data/solutions/pricing.de.ts",
                                        new_string="body: ['Diese Seite listet den Tarif so, wie er im Code steht.'],")),
          True)
    check("page data comment ignored", ev("Edit", "data/tools/agent.ts",
                                          new_string="// TODO: coming in phase 3\nexport const NAME = 'agent'"), None)
    check("page data identifier ignored", ev("Write", "data/plans.ts",
                                             content="export const flags = { featureFlag: true, phase: 3 }"), None)
    check("component file ignored", ev("Edit", "app/components/Pricing.ts",
                                       new_string="const label = 'coming in phase 3 for sure'"), None)
    check("code file ignored", ev("Edit", "src/billing.py", new_string="# TODO: coming in phase 3"), None)
    check("test ignored", ev("Edit", "tests/test_copy.py", new_string="assert 'phase 3' not in page"), None)
    check("clean locale", ev("Edit", "i18n/de.json", new_string='"ok": "Deine Buchung ist bestätigt."'), None)
    check("code block ignored", ev("Edit", "content/guide.md",
                                   new_string="```bash\ncurl https://example.com/<Token>\n```"), None)
    check("escalation stage allowed", ev("Edit", "i18n/en.json", new_string='"s": "Escalation stage 2"'), None)
    out = ev("Edit", "i18n/de.json", new_string='"sso": "SSO kommt mit Phase 3."')
    check("one finding per kind", out["hookSpecificOutput"]["additionalContext"].count("roadmap or plan"), 1)
    check("other event", handle({"hook_event_name": "PreToolUse", "tool_name": "Edit",
                                 "tool_input": {"file_path": "i18n/de.json", "new_string": "Phase 3"}}), None)
    print("self-test: " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv: list | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--self-test"]:
        return self_test()
    try:
        out = handle(json.loads(sys.stdin.read() or "{}"))
    except Exception:
        return 0
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
