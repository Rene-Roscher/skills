#!/usr/bin/env python3
"""Remind the agent to audit a rendered surface it just edited (design-quality, web plugin).

PostToolUse on Edit, Write and MultiEdit. When the edited file is something that renders for a person (a
component, a stylesheet, a page template, Markdown under a content folder, a mail template), the hook adds a
reminder as context: open the rendered page and audit it before reporting. Content edits count, because they
feel like text work and are the ones that slip through. The reminder comes once per file per session, and the
full checklist only with the first one, so a long session is not flooded. The hook never blocks.

Rendered files: .vue, .svelte, .astro, .css, .scss, .sass, .less, .html, .mjml; .tsx and .jsx under a folder
named components, pages, layouts, views, app or src; .md and .mdx under content, docs, pages, blog or help;
.blade.php, .twig and .hbs under a folder named views, templates, mail, mails, emails or email. Test and story
files are ignored.

Usage: surface.py (reads the hook event as JSON on stdin) | surface.py --self-test
Python 3.8 or later, standard library only. Any internal error exits 0 without output.
State lives in CLAUDE_PLUGIN_DATA, else the temp directory, one file per session, removed after seven days.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path, PurePath

ALWAYS = (".vue", ".svelte", ".astro", ".css", ".scss", ".sass", ".less", ".html", ".mjml")
COMPONENT_SUFFIXES = (".tsx", ".jsx")
COMPONENT_DIRS = {"components", "pages", "layouts", "views", "app", "src"}
CONTENT_SUFFIXES = (".md", ".mdx")
CONTENT_DIRS = {"content", "docs", "pages", "blog", "help"}
TEMPLATE_SUFFIXES = (".blade.php", ".twig", ".hbs")
TEMPLATE_DIRS = {"views", "templates", "mail", "mails", "emails", "email"}
IGNORED = re.compile(r"\.(test|spec|stories|story)\.", re.I)
IGNORED_DIRS = {"node_modules", "vendor", "dist", "build", ".nuxt", ".output", "tests", "__tests__"}

CHECKLIST = (
    "Before you report this change, open the rendered page in a headless browser and audit it (skill "
    "design-quality): light and dark, 390 px width; text contrast (accent colour used as text included); "
    "characters per line on real prose; no horizontal overflow; overlays centred, inside the viewport, closing on "
    "Escape with focus returned; and for content, rendered headings against the source. Fix what you find in "
    "the touched surface, and report anything outside it as a proposal with before and after screenshots."
)


def is_surface(path: str) -> bool:
    p = PurePath(path)
    name = p.name.lower()
    dirs = {part.lower() for part in p.parts[:-1]}
    if IGNORED.search(name) or dirs & IGNORED_DIRS:
        return False
    if name.endswith(TEMPLATE_SUFFIXES):
        return bool(dirs & TEMPLATE_DIRS)
    suffix = p.suffix.lower()
    if suffix in ALWAYS:
        return True
    if suffix in COMPONENT_SUFFIXES:
        return bool(dirs & COMPONENT_DIRS)
    if suffix in CONTENT_SUFFIXES:
        return bool(dirs & CONTENT_DIRS)
    return False


def state_dir() -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(tempfile.gettempdir(), "claude-guardrails")
    p = Path(base) / "surfaces"
    p.mkdir(parents=True, exist_ok=True)
    return p


def prune(max_age_days: int = 7) -> None:
    cutoff = time.time() - max_age_days * 86400
    for f in state_dir().glob("*.json"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            pass


def seen_before(session: str, path: str) -> tuple:
    """Record the path for this session; return (already seen, first reminder of the session)."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session or "unknown")[:120]
    f = state_dir() / f"{safe}.json"
    try:
        seen = json.loads(f.read_text(encoding="utf-8") or "[]")
    except (OSError, ValueError):
        seen = []
    if path in seen:
        return True, False
    first = not seen
    seen.append(path)
    f.write_text(json.dumps(seen[-500:]), encoding="utf-8")
    return False, first


def handle(ev: dict) -> dict | None:
    if ev.get("hook_event_name") != "PostToolUse":
        return None
    tool = ev.get("tool_name") or ""
    path = str((ev.get("tool_input") or {}).get("file_path") or "")
    if tool not in ("Edit", "Write", "MultiEdit") or not path or not is_surface(path):
        return None
    seen, first = seen_before(str(ev.get("session_id") or "unknown"), path)
    if seen:
        return None
    name = PurePath(path).name
    if first:
        text = f"design check: {name} renders for people. {CHECKLIST}"
    else:
        text = f"design check: {name} renders too; include its page in the audit before you report."
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}


def self_test() -> int:
    ok = True

    def check(label: str, got, want) -> None:
        nonlocal ok
        if got != want:
            ok = False
            print(f"self-test: {label}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as tmp:
        os.environ["CLAUDE_PLUGIN_DATA"] = tmp

        def ev(path: str, tool: str = "Edit", sid: str = "s1", event: str = "PostToolUse"):
            out = handle({"hook_event_name": event, "session_id": sid, "tool_name": tool,
                          "tool_input": {"file_path": path, "new_string": "x"}})
            return out["hookSpecificOutput"]["additionalContext"] if out else None

        first = ev("app/components/Sidebar.vue")
        check("vue warns with checklist", bool(first and "390 px" in first), True)
        check("same file again is quiet", ev("app/components/Sidebar.vue"), None)
        second = ev("app/assets/css/docs.css")
        check("second file short", bool(second and "390 px" not in second and "docs.css" in second), True)
        check("content markdown", bool(ev("content/02.monitoring/http.md", "Write")), True)
        check("mail template", bool(ev("resources/views/mail/invoice.blade.php")), True)
        check("tsx component", bool(ev("src/components/Table.tsx", "MultiEdit")), True)
        check("other session gets checklist", "390 px" in (ev("app/components/Sidebar.vue", sid="s2") or ""), True)
        check("readme outside content ignored", ev("README.md"), None)
        check("php ignored", ev("app/Http/Controllers/HomeController.php"), None)
        check("blade outside views ignored", ev("app/Support/stub.blade.php"), None)
        check("test ignored", ev("app/components/Sidebar.spec.vue"), None)
        check("story ignored", ev("src/components/Button.stories.tsx"), None)
        check("node_modules ignored", ev("node_modules/pkg/style.css"), None)
        check("tests dir ignored", ev("tests/Browser/fixture.html"), None)
        check("ts utility ignored", ev("app/composables/useTheme.ts"), None)
        check("other event", ev("app/components/Nav.vue", event="PreToolUse"), None)
        check("read tool ignored", ev("app/components/Nav.vue", tool="Read"), None)
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
    print("self-test: " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv: list | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--self-test"]:
        return self_test()
    try:
        prune()
        out = handle(json.loads(sys.stdin.read() or "{}"))
    except Exception:
        return 0
    if out:
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
