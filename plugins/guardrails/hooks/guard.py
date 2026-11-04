#!/usr/bin/env python3
"""Claude Code hook: enforce the attempt cap and block check bypasses.

One script for four hook events; it reads the event JSON on stdin.

- PostToolUseFailure (Bash): a failed command that is not a read-only probe counts as one attempt.
  The count is fed back as "attempt k/CAP"; at the cap the agent is told to stop and hand off.
- PostToolUse (Bash): a passing check (test, lint, type check, build, validator) resets the count.
- UserPromptSubmit: the owner replied, so the count starts again.
- PreToolUse (Bash, Edit, Write, MultiEdit, NotebookEdit): denies commands that skip or silence
  checks (--no-verify, core.hooksPath, HUSKY=0, "check || true"), and at the cap denies every
  edit and every command that is not a read-only probe.

Environment: GUARDRAILS_ATTEMPT_CAP (default 10). State lives in CLAUDE_PLUGIN_DATA, else in the
temp directory, one file per session. Any internal error exits 0 without output, so a broken hook
never blocks a session. Run with --self-test to check the logic offline.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import tempfile
import time
from pathlib import Path

try:
    import fcntl  # POSIX only; without it, state writes are unlocked.
except ImportError:  # pragma: no cover
    fcntl = None

DEFAULT_CAP = 10
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
OPERATORS = {"&&", "||", ";", "|", "&", "|&", ";;", "(", ")"}
WRAPPERS = {"sudo", "time", "nohup", "env", "command", "builtin", "exec", "nice"}
PROBES = {
    "grep", "egrep", "fgrep", "rg", "ag", "ls", "find", "fd", "test", "[", "[[", "diff", "cmp", "cat",
    "head", "tail", "less", "wc", "which", "type", "whereis", "file", "stat", "echo", "printf", "true",
    "false", "pwd", "cd", "sleep", "sort", "uniq", "cut", "tr", "awk", "jq", "yq", "tree", "du", "df",
    "ps", "pgrep", "id", "whoami", "date", "env", "printenv", "realpath", "readlink", "basename",
    "dirname", "column", "nl", "od", "xxd", "hexdump", "sha256sum", "md5sum",
}
GIT_PROBES = {"status", "diff", "log", "show", "grep", "rev-parse", "branch", "ls-files", "blame", "describe",
              "remote", "config", "cat-file", "merge-base", "shortlog", "reflog", "tag", "stash"}
CHECK_RE = re.compile(
    r"(?:^|[\s/])(?:pest|phpunit|paratest|pytest|tox|nox|jest|vitest|mocha|playwright|phpstan|psalm|"
    r"eslint|tsc|vue-tsc|svelte-check|ruff|mypy|pyright|flake8|pint|rubocop|rspec|golangci-lint|"
    r"staticcheck|shellcheck|hadolint|actionlint|zizmor|gitleaks|lint\.py)(?:\s|$)"
    r"|\b(?:go\s+(?:test|vet|build)|cargo\s+(?:test|build|check|clippy|nextest)|artisan\s+test|"
    r"(?:npm|pnpm|yarn|bun)\s+(?:run\s+)?[\w:.-]*(?:test|lint|check|build|typecheck)[\w:.-]*|"
    r"make(?:\s+[\w.-]+)?|dotnet\s+(?:test|build)|mvn\s+\S*(?:test|verify)|gradle\w*\s+\S*(?:test|check|build)|"
    r"plugin\s+validate)\b|(?:^|\s)--self-test(?:\s|$)"
)
SILENCERS = {"true", ":"}


# ---------------------------------------------------------------- command parsing

def tokens(command: str) -> list[str]:
    try:
        lex = shlex.shlex(command, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        return list(lex)
    except ValueError:
        return re.findall(r"&&|\|\||[;|&()]|[^\s;|&()]+", command)


def segments(command: str) -> list[tuple[list[str], str]]:
    """Split into simple commands; each comes with the operator that follows it."""
    out: list[tuple[list[str], str]] = []
    cur: list[str] = []
    for tok in tokens(command.replace("\n", " ; ")):
        if tok in OPERATORS:
            if cur:
                out.append((cur, tok))
            cur = []
        else:
            cur.append(tok)
    if cur:
        out.append((cur, ""))
    return out


def strip_prefix(seg: list[str]) -> tuple[list[str], dict[str, str]]:
    """Drop leading VAR=value assignments and wrappers like sudo; return the rest and the assignments."""
    assigns: dict[str, str] = {}
    i = 0
    while i < len(seg):
        tok = seg[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok):
            k, _, v = tok.partition("=")
            assigns[k] = v
        elif tok in WRAPPERS:
            pass
        elif tok.startswith("-") and i > 0 and seg[i - 1] in WRAPPERS:
            pass
        else:
            break
        i += 1
    return seg[i:], assigns


def head(seg: list[str]) -> str:
    rest, _ = strip_prefix(seg)
    return os.path.basename(rest[0]) if rest else ""


def is_probe_segment(seg: list[str]) -> bool:
    rest, _ = strip_prefix(seg)
    if not rest:
        return True
    h = os.path.basename(rest[0])
    if h == "sed":
        return not any(t == "-i" or t.startswith("-i") or t == "--in-place" for t in rest[1:])
    if h == "git":
        sub = next((t for t in rest[1:] if not t.startswith("-")), "")
        return sub in GIT_PROBES
    return h in PROBES


def probe_only(command: str) -> bool:
    segs = segments(command)
    return bool(segs) and all(is_probe_segment(s) for s, _ in segs)


def is_check(command: str) -> bool:
    return any(not is_probe_segment(s) and CHECK_RE.search(" ".join(s)) for s, _ in segments(command))


def bypass_reason(command: str) -> str | None:
    segs = segments(command)
    for idx, (seg, op) in enumerate(segs):
        rest, assigns = strip_prefix(seg)
        name = os.path.basename(rest[0]) if rest else ""
        if name == "git":
            if "--no-verify" in rest:
                return "--no-verify skips the repository's hooks"
            for i, t in enumerate(rest):
                if t == "-c" and i + 1 < len(rest) and rest[i + 1].startswith("core.hooksPath"):
                    return "-c core.hooksPath replaces the repository's hooks"
                if t.startswith("core.hooksPath=") and i > 0 and rest[i - 1] == "-c":
                    return "-c core.hooksPath replaces the repository's hooks"
            for k in ("HUSKY", "LEFTHOOK"):
                if assigns.get(k) == "0":
                    return f"{k}=0 switches off the repository's hooks"
            if "SKIP" in assigns or "PRE_COMMIT_ALLOW_NO_CONFIG" in assigns:
                return "an environment switch skips pre-commit hooks"
            sub_i = next((i for i, t in enumerate(rest[1:], 1) if not t.startswith("-")), None)
            if sub_i is not None and rest[sub_i] == "commit":
                skip_next = False
                for t in rest[sub_i + 1:]:
                    if skip_next:
                        skip_next = False
                        continue
                    if re.fullmatch(r"-[A-Za-z]+", t):
                        if "n" in t:
                            return "git commit -n skips the pre-commit and commit-msg hooks"
                        if t[-1] in "mFcCt":
                            skip_next = True
        if op == "||" and idx + 1 < len(segs) and CHECK_RE.search(" ".join(seg)) and not is_probe_segment(seg):
            nxt, _ = strip_prefix(segs[idx + 1][0])
            if nxt and (nxt[0] in SILENCERS or nxt[:2] == ["exit", "0"]):
                return f"'|| {' '.join(nxt[:2])}' turns a failing check into a pass"
    return None


# ---------------------------------------------------------------- state

def cap() -> int:
    try:
        return max(1, int(os.environ.get("GUARDRAILS_ATTEMPT_CAP", DEFAULT_CAP)))
    except ValueError:
        return DEFAULT_CAP


def state_dir() -> Path:
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(tempfile.gettempdir(), "claude-guardrails")
    p = Path(base) / "attempts"
    p.mkdir(parents=True, exist_ok=True)
    return p


def state_file(session: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session or "unknown")[:120]
    return state_dir() / f"{safe}.json"


class State:
    """Per-session counters, one per agent (main thread or subagent)."""

    def __init__(self, session: str):
        self.path = state_file(session)
        self.fh = open(self.path, "a+", encoding="utf-8")
        if fcntl:
            fcntl.flock(self.fh, fcntl.LOCK_EX)
        self.fh.seek(0)
        try:
            self.data = json.loads(self.fh.read() or "{}")
        except ValueError:
            self.data = {}

    def get(self, agent: str) -> dict:
        return self.data.setdefault(agent, {"attempts": 0, "last": []})

    def save(self) -> None:
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write(json.dumps(self.data))
        self.fh.flush()

    def close(self) -> None:
        self.fh.close()


def prune(max_age_days: int = 7) -> None:
    cutoff = time.time() - max_age_days * 86400
    for f in state_dir().glob("*.json"):
        try:
            if f.stat().st_mtime < cutoff:
                f.unlink()
        except OSError:
            pass


# ---------------------------------------------------------------- events

def agent_key(ev: dict) -> str:
    return str(ev.get("agent_id") or "main")


def short(command: str, n: int = 80) -> str:
    one = " ".join(command.split())
    return one if len(one) <= n else one[: n - 1] + "…"


def deny(reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": reason}}


def context(event: str, text: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}


def stop_text(k: int, c: int, last: list[str]) -> str:
    tried = "; ".join(last[-3:]) if last else "n/a"
    return (f"guardrails: attempt cap reached ({k}/{c} failed attempts since the owner's last message; last: {tried}). "
            "Stop fixing. Undo the changes you cannot explain, then write the stop report: the symptom, one line "
            "per attempt with its result, what is known, and the one question for the owner. Edits and commands "
            "other than read-only probes are blocked until the owner replies.")


def handle(ev: dict) -> dict | None:
    name = ev.get("hook_event_name", "")
    session = str(ev.get("session_id") or "unknown")
    tool = ev.get("tool_name", "")
    tin = ev.get("tool_input") or {}
    command = tin.get("command", "") if isinstance(tin, dict) else ""
    c = cap()

    if name == "UserPromptSubmit":
        st = State(session)
        try:
            st.data = {}
            st.save()
        finally:
            st.close()
        prune()
        return None

    if name == "PreToolUse":
        if tool == "Bash":
            reason = bypass_reason(command)
            if reason:
                return deny(f"guardrails: blocked, {reason}. Fix the cause the check reports instead. If the owner "
                            "has explicitly allowed skipping this check, ask them to run the command themselves.")
        if tool == "Bash" or tool in EDIT_TOOLS:
            st = State(session)
            try:
                a = st.get(agent_key(ev))
            finally:
                st.close()
            if a["attempts"] >= c and not (tool == "Bash" and probe_only(command)):
                return deny(stop_text(a["attempts"], c, a["last"]))
        return None

    if tool != "Bash" or not command:
        return None

    if name == "PostToolUse":
        if is_check(command):
            st = State(session)
            try:
                a = st.get(agent_key(ev))
                if a["attempts"]:
                    a["attempts"], a["last"] = 0, []
                    st.save()
            finally:
                st.close()
        return None

    if name == "PostToolUseFailure":
        if ev.get("is_interrupt") or probe_only(command):
            return None
        st = State(session)
        try:
            a = st.get(agent_key(ev))
            a["attempts"] += 1
            a["last"] = (a["last"] + [short(command, 60)])[-5:]
            st.save()
            k = a["attempts"]
        finally:
            st.close()
        if k >= c:
            return context(name, stop_text(k, c, a["last"]))
        msg = (f"guardrails: attempt {k}/{c} since the owner's last message ({short(command)}). Read the whole "
               "error before the next change; do not rerun the same command unchanged.")
        if k >= 3:
            msg += (" If the last attempts produced no new fact (same error, same log line), stop now, undo what "
                    "you cannot explain and ask the owner.")
        return context(name, msg)

    return None


def main(argv: list[str] | None = None) -> int:
    if "--self-test" in (sys.argv[1:] if argv is None else argv):
        return self_test()
    try:
        ev = json.loads(sys.stdin.read() or "{}")
        out = handle(ev)
    except Exception:  # never break the session because the hook failed
        return 0
    if out:
        sys.stdout.write(json.dumps(out))
    return 0


# ---------------------------------------------------------------- self-test

def self_test() -> int:
    fails: list[str] = []

    def check(label: str, got, want) -> None:
        if got != want:
            fails.append(f"{label}: got {got!r}, want {want!r}")

    blocked = [
        "git commit --no-verify -m 'wip'",
        "cd app && git commit -am wip -n",
        "git commit -nm 'x'",
        "git push --no-verify origin main",
        "HUSKY=0 git commit -m x",
        "SKIP=eslint git commit -m x",
        "git -c core.hooksPath=/dev/null commit -m x",
        "npm test || true",
        "php artisan test --compact || :",
        "docker exec app sh -c 'cd /app && vendor/bin/pest' || exit 0",
        "pytest -q tests || true",
    ]
    allowed = [
        "git commit -m 'explain the -n flag'",
        "git commit -m '--no-verify is bad'",
        "git commit -F msg.txt",
        "git log -n 5",
        "grep -n foo file || true",
        "npm test",
        "test -f a || touch a",
        "echo '--no-verify'",
        "ls nope || true",
    ]
    for cmd in blocked:
        check(f"blocks {cmd!r}", bool(bypass_reason(cmd)), True)
    for cmd in allowed:
        check(f"allows {cmd!r}", bypass_reason(cmd), None)

    check("probe grep", probe_only("grep -rn foo src | head"), True)
    check("probe git diff", probe_only("cd x && git diff --stat"), True)
    check("not probe sed -i", probe_only("sed -i 's/a/b/' f"), False)
    check("not probe test runner", probe_only("cd /app && php artisan test"), False)
    check("check pest", is_check("docker exec php sh -c 'cd /app && ./vendor/bin/pest tests/X'"), True)
    check("check pnpm", is_check("pnpm run i18n:check"), True)
    check("check self-test", is_check("python3 tools/x.py --self-test"), True)
    check("check make", is_check("make build"), True)
    check("not check curl", is_check("curl -sf https://example.org"), False)
    check("not check cat tests", is_check("cat tests/Feature/A.php"), False)

    with tempfile.TemporaryDirectory() as tmp:
        os.environ["CLAUDE_PLUGIN_DATA"] = tmp
        os.environ["GUARDRAILS_ATTEMPT_CAP"] = "10"
        sid = "self-test-session"

        def ev(event: str, tool: str = "Bash", command: str = "", **extra) -> dict | None:
            e = {"hook_event_name": event, "session_id": sid, "tool_name": tool,
                 "tool_input": {"command": command} if tool == "Bash" else {"file_path": "a.py"}}
            e.update(extra)
            return handle(e)

        def ctx(out) -> str:
            return (out or {}).get("hookSpecificOutput", {}).get("additionalContext", "")

        def denied(out) -> bool:
            return (out or {}).get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

        check("probe failure not counted", ev("PostToolUseFailure", command="grep -q x f"), None)
        check("interrupt not counted", ev("PostToolUseFailure", command="npm test", is_interrupt=True), None)
        out = ev("PostToolUseFailure", command="npm test")
        check("first attempt counted", "attempt 1/10" in ctx(out), True)
        check("passing check resets", ev("PostToolUse", command="npm test"), None)
        out = ev("PostToolUseFailure", command="npm test")
        check("count restarts after pass", "attempt 1/10" in ctx(out), True)
        ev("PostToolUse", command="curl -sf https://example.org")
        out = ev("PostToolUseFailure", command="npm test")
        check("non-check success does not reset", "attempt 2/10" in ctx(out), True)
        out = ev("PostToolUseFailure", command="npm test")
        check("warns from the third attempt", "stop now" in ctx(out), True)
        for _ in range(7):
            out = ev("PostToolUseFailure", command="npm test")
        check("cap reached at 10", "attempt cap reached" in ctx(out), True)
        check("edit blocked at cap", denied(ev("PreToolUse", tool="Edit")), True)
        check("command blocked at cap", denied(ev("PreToolUse", command="npm test")), True)
        check("probe allowed at cap", ev("PreToolUse", command="git diff --stat"), None)
        check("subagent has its own count", ev("PreToolUse", tool="Edit", agent_id="sub-1"), None)
        check("owner reply resets", ev("UserPromptSubmit", tool=""), None)
        check("edit allowed after reply", ev("PreToolUse", tool="Edit"), None)
        check("bypass denied", denied(ev("PreToolUse", command="git commit --no-verify -m x")), True)
        os.environ["GUARDRAILS_ATTEMPT_CAP"] = "2"
        ev("PostToolUseFailure", command="go test ./...")
        out = ev("PostToolUseFailure", command="go test ./...")
        check("cap from environment", "attempt cap reached" in ctx(out), True)
        os.environ.pop("CLAUDE_PLUGIN_DATA", None)
        os.environ.pop("GUARDRAILS_ATTEMPT_CAP", None)

    check("garbage input exits 0", _run_main_with("not json"), 0)

    if fails:
        for f in fails:
            print("FAIL", f)
        print(f"self-test: {len(fails)} failure(s)")
        return 1
    print("self-test: ok")
    return 0


def _run_main_with(stdin_text: str) -> int:
    import io
    old_in, old_out = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = io.StringIO(stdin_text), io.StringIO()
    try:
        return main([])
    finally:
        sys.stdin, sys.stdout = old_in, old_out


if __name__ == "__main__":
    sys.exit(main())
