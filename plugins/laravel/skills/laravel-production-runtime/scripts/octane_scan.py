#!/usr/bin/env python3
"""Find request, user and tenant state that survives into the next request or job in a Laravel app.

Under Octane, FrankenPHP worker mode, Swoole, RoadRunner and `queue:work`, one PHP process serves many
requests or jobs. This scanner reads PHP source at token level and reports state that one request or job
can leave behind for the next one. Read-only. Python 3.10 or later, standard library only. When a `php`
binary (PHP 8.0 or later) is on PATH, the source is tokenized with PHP's own `token_get_all()`; otherwise
a built-in tokenizer runs. The summary line names the mode that ran.

Usage:
  octane_scan.py [ROOT] [--include DIR ...] [--tokenizer auto|php|python] [--json] [--min-severity LEVEL]
  octane_scan.py --self-test

ROOT is the Laravel app root (default: the current directory). Scanned: app/, routes/, bootstrap/app.php,
config/octane.php, plus every --include directory (for example packages/ or modules/). vendor/ and tests/
are never scanned.

Rules:
  OS01  static property written at runtime (`static::$x =`, `self::$x[] =`, `Name::$cache[$k] =`)
  OS02  `static $var` inside a function or method that keeps per-call data
  OS03  singleton (`->singleton()`, `#[Singleton]`, `$singletons`, `withSingletons()`, boot-time
        `->instance(X::class, new Y)`) whose constructor reads the request, auth, session, the current
        user or a tenant, directly or through what it injects; container or config injection (medium)
  OS04  controller constructor that reads request or auth, or injects a service that does or that memoizes
  OS05  `->instance('key', ...)` keys versus `config/octane.php` `flush`, in both directions
  OS06  `spl_object_id()` / `spl_object_hash()` used as identity
  OS07  process-wide writes: `$GLOBALS[...] =`, runtime `define()`, `ini_set()`, `setlocale()`,
        `date_default_timezone_set()`, `putenv()` in request or job code
  OS08  middleware that binds context with `->instance()` without `forgetInstance()` before an early return
  OS09  job that binds container instances, logs a user in or writes config without resetting in `finally`

Severity: blocker = request, user or tenant data reaches shared state; high = a pattern that leaks unless
proven otherwise; medium and low = heuristics. Suppress one finding with a comment on the same or the
previous line: `// octane-scan: allow OS01 [reason]`. The reason is required; an allow comment without
one is ignored and the finding says so.

Exit codes:
  0  no blocker or high finding
  1  at least one blocker or high finding (or a self-test failure)
  2  usage error (missing root, no app/ directory, bad arguments, php forced but unusable)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

TOOL = "laravel-production-runtime/octane_scan.py 1.0"
SEVERITIES = ["blocker", "high", "medium", "low"]
FAILING = {"blocker", "high"}
RULES = {
    "OS01": "static property written at runtime",
    "OS02": "function-level static variable keeps per-call data",
    "OS03": "singleton constructor captures request, user or tenant state",
    "OS04": "controller constructor holds request state",
    "OS05": "container instance key and octane.flush disagree",
    "OS06": "object handle used as identity",
    "OS07": "process-wide state written at runtime",
    "OS08": "middleware binds context without forgetting it first",
    "OS09": "job binds context without resetting it in finally",
}
FIX = {
    "OS01": "Move the memo to instance state on a scoped() binding, or key it by a token stamped on the "
            "current request; reset statics only in boot code.",
    "OS02": "Drop the function-level static; memoize on a scoped() binding or pass the data per call.",
    "OS03": "Bind with scoped(), or keep the singleton stateless and pass the request, user or tenant per "
            "call (or inject a resolver closure such as fn () => request()).",
    "OS04": "Resolve request-dependent services at call time (method injection or app() inside the method); "
            "read auth and request inside the action, not the constructor.",
    "OS05": "List every key the app binds with ->instance() in octane.flush and nothing else; never list "
            "framework or package managers.",
    "OS06": "Stamp a random token on the request ($request->attributes) and compare that; PHP reuses freed "
            "object handles.",
    "OS07": "Set process-wide values once at boot, or restore them in finally; pass per-user values (time "
            "zone, locale) explicitly.",
    "OS08": "Call app()->forgetInstance() for the key at the start of handle(), before any early return.",
    "OS09": "Bind inside try and forget the instance, log out or restore config in finally.",
}

ALLOW_RE = re.compile(r"octane-scan:\s*allow\s+(OS\d{2})\b[ \t]*([^\r\n]*?)\s*(?:\*/)?\s*$", re.M)
MIN_REASON = 8

# Types whose instance is per request. Fully qualified, lowercase, no leading backslash. The auth and
# session managers are absent on purpose: Octane (2.17.5, FlushAuthenticationState, FlushSessionState)
# resets the same manager object every request, so holding the manager reads current state. A resolved
# guard holds its user, and a request or route object is replaced per request.
REQUEST_TYPES = {
    "illuminate\\http\\request", "symfony\\component\\httpfoundation\\request",
    "illuminate\\foundation\\http\\formrequest",
    "illuminate\\contracts\\auth\\guard", "illuminate\\contracts\\auth\\statefulguard",
    "illuminate\\contracts\\auth\\authenticatable", "illuminate\\foundation\\auth\\user",
    "illuminate\\auth\\sessionguard", "illuminate\\auth\\requestguard", "illuminate\\auth\\tokenguard",
    "illuminate\\routing\\route",
}
CONTAINER_TYPES = {
    "illuminate\\contracts\\foundation\\application", "illuminate\\foundation\\application",
    "illuminate\\contracts\\container\\container", "illuminate\\container\\container",
    "illuminate\\contracts\\config\\repository", "illuminate\\config\\repository",
}
REQUEST_ATTRS = {"currentuser", "authenticated", "auth", "context", "routeparameter"}
ATTR_NS = "illuminate\\container\\attributes\\"
MANAGER_KEYS = {
    "laravel\\socialite\\contracts\\factory", "socialite", "filesystem", "files", "cache", "cache.store",
    "mail.manager", "mailer", "illuminate\\contracts\\notifications\\dispatcher",
    "illuminate\\notifications\\channelmanager", "illuminate\\broadcasting\\broadcastmanager",
    "illuminate\\contracts\\broadcasting\\factory", "illuminate\\filesystem\\filesystemmanager",
    "illuminate\\contracts\\filesystem\\factory", "illuminate\\cache\\cachemanager", "illuminate\\mail\\mailmanager",
    "db", "queue", "auth", "session", "log", "events", "router", "view", "translator", "config",
}
FACADES = {"auth": "illuminate\\support\\facades\\auth", "request": "illuminate\\support\\facades\\request",
           "session": "illuminate\\support\\facades\\session"}
TAINT_HELPERS = {"request", "auth", "session"}
TAINT_KEYS = {"request", "auth.driver"}
SUPERGLOBALS = {"$_server", "$_get", "$_post", "$_cookie", "$_request", "$_session", "$_files"}
TENANT_WORDS = {"tenant", "tenants", "tenancy", "organization", "organizations", "organisation",
                "organisations", "org", "orgs", "workspace", "workspaces"}
CURRENT_WORDS = {"user", "team", "account", "org", "company", "customer", "project", "member"}
DB_HINTS_STATIC = {"query", "find", "findorfail", "where", "first", "all", "firstwhere", "findmany", "get",
                   "pluck", "select", "table"}
DB_HINTS_METHOD = {"get", "first", "find", "findorfail", "pluck", "count", "load", "loadmissing", "sum",
                   "exists", "firstorfail", "value", "paginate", "cursor", "lazy"}
ASSIGN_OPS = {"=", ".=", "+=", "-=", "*=", "/=", "%=", "**=", "??=", "|=", "&=", "^=", "<<=", ">>="}
MODIFIERS = {"public", "protected", "private", "static", "final", "abstract", "readonly", "var"}
OPENERS = {"(": ")", "[": "]", "{": "}", "#[": "]"}
CLOSERS = {")", "]", "}"}
BOOT_METHODS = {"register", "boot", "booted", "booting", "bootstrap", "configure", "provides"}
REGISTRY_METHOD_RE = re.compile(r"^(register|extend|add|push|boot)", re.I)
RESET_METHOD_RE = re.compile(r"^(flush|reset|forget|clear|teardown|purge|restore)", re.I)
GLOBAL_WRITERS = {"ini_set", "ini_alter", "setlocale", "date_default_timezone_set", "putenv"}

# --- tokens -------------------------------------------------------------------------------------------


@dataclass
class Tok:
    kind: str          # name, var, str, istr, num, op, comment
    text: str
    line: int
    value: str | None = None   # unquoted content of a constant string

    @property
    def low(self) -> str:
        return self.text.lower()


NAME_RE = re.compile(r"\\?[A-Za-z_\x80-\U0010ffff][\w\x80-\U0010ffff]*(?:\\[A-Za-z_\x80-\U0010ffff][\w\x80-\U0010ffff]*)*")
NUM_RE = re.compile(r"0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+|(?:\d[\d_]*)?\.?\d[\d_]*(?:[eE][+-]?\d+)?")
OPS = sorted("""<<= >>= **= ... <=> === !== ??= ?-> -> => :: == != <> <= >= && || ?? ++ -- += -= *= /= .= %= &= |= ^=
<< >> ** #[""".split(), key=len, reverse=True)
ISTR_VAR_RE = re.compile(r"(?<!\\)\$([A-Za-z_]\w*)(?:->(\w+))?")
HEREDOC_RE = re.compile(r"<<<[ \t]*([\"']?)([A-Za-z_\x80-\U0010ffff][\w\x80-\U0010ffff]*)\1\r?\n")


def _unquote(text: str) -> str:
    body = text[1:-1]
    if text[0] == "'":
        return body.replace("\\\\", "\0").replace("\\'", "'").replace("\0", "\\")
    return body.replace("\\\\", "\0").replace('\\"', '"').replace("\\$", "$").replace("\0", "\\")


def _interpolates(body: str) -> bool:
    i = 0
    while i < len(body):
        c = body[i]
        if c == "\\":
            i += 2
            continue
        if c == "$" and i + 1 < len(body) and (body[i + 1].isalpha() or body[i + 1] in "_{"):
            return True
        if c == "{" and i + 1 < len(body) and body[i + 1] == "$":
            return True
        i += 1
    return False


def py_tokenize(src: str) -> list[Tok]:
    """Tokenize PHP source. Mirrors the parts of token_get_all() this scanner relies on."""
    toks: list[Tok] = []
    i, n, line = 0, len(src), 1
    html = True
    while i < n:
        if html:
            m = re.compile(r"<\?php(?=\s)|<\?=", re.I).search(src, i)
            end = n if m is None else m.end()
            line += src.count("\n", i, end)
            i = end
            html = False
            continue
        c = src[i]
        if c in " \t\r\n\f\v":
            j = i
            while j < n and src[j] in " \t\r\n\f\v":
                j += 1
            line += src.count("\n", i, j)
            i = j
            continue
        if src.startswith("?>", i):
            toks.append(Tok("op", ";", line))
            i += 2
            if src.startswith("\r\n", i):
                i += 2
                line += 1
            elif i < n and src[i] == "\n":
                i += 1
                line += 1
            html = True
            continue
        if src.startswith("#[", i):
            toks.append(Tok("op", "#[", line))
            i += 2
            continue
        if c == "#" or src.startswith("//", i):
            j = i
            while j < n and src[j] != "\n" and not src.startswith("?>", j):
                j += 1
            toks.append(Tok("comment", src[i:j], line))
            i = j
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            toks.append(Tok("comment", src[i:j], line))
            line += src.count("\n", i, j)
            i = j
            continue
        if c in "'\"`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            j = min(j + 1, n)
            text = src[i:j]
            if c == "'" or (c == '"' and not _interpolates(text[1:-1])):
                toks.append(Tok("str", text, line, _unquote(text)))
            else:
                toks.append(Tok("istr", text, line))
            line += src.count("\n", i, j)
            i = j
            continue
        if src.startswith("<<<", i):
            m = HEREDOC_RE.match(src, i)
            if m:
                close = re.compile(r"(?m)^[ \t]*" + re.escape(m.group(2)) + r"(?![\w\x80-\U0010ffff])")
                cm = close.search(src, m.end())
                j = n if cm is None else cm.end()
                toks.append(Tok("istr", src[i:j], line))
                line += src.count("\n", i, j)
                i = j
                continue
        if c == "$" and i + 1 < n and (src[i + 1].isalpha() or src[i + 1] == "_" or ord(src[i + 1]) >= 0x80):
            m = NAME_RE.match(src, i + 1)
            toks.append(Tok("var", "$" + m.group(0).split("\\")[0], line))
            i = i + 1 + len(m.group(0).split("\\")[0])
            continue
        if c.isalpha() or c == "_" or ord(c) >= 0x80 or (c == "\\" and i + 1 < n and (src[i + 1].isalpha() or src[i + 1] == "_")):
            m = NAME_RE.match(src, i)
            toks.append(Tok("name", m.group(0), line))
            i = m.end()
            continue
        if c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit()):
            m = NUM_RE.match(src, i)
            if m and m.end() > i:
                toks.append(Tok("num", m.group(0), line))
                i = m.end()
                continue
        for op in OPS:
            if src.startswith(op, i):
                toks.append(Tok("op", op, line))
                i += len(op)
                break
        else:
            toks.append(Tok("op", c, line))
            i += 1
    return toks


PHP_TOKENIZER = r"""
$files = preg_split('/\R/', trim(stream_get_contents(STDIN)));
foreach ($files as $f) {
    if ($f === '') { continue; }
    $src = @file_get_contents($f);
    if ($src === false) { echo json_encode(['f' => $f, 'e' => 'unreadable']), "\n"; continue; }
    $out = []; $cur = 1;
    foreach (token_get_all($src) as $t) {
        if (is_array($t)) { $cur = $t[2]; $name = token_name($t[0]); $text = $t[1]; }
        else { $name = ''; $text = $t; }
        if ($name !== 'T_WHITESPACE') { $out[] = [$name, $text, $cur]; }
        $cur += substr_count($text, "\n");
    }
    echo json_encode(['f' => $f, 't' => $out], JSON_INVALID_UTF8_SUBSTITUTE | JSON_PARTIAL_OUTPUT_ON_ERROR), "\n";
}
"""


def php_normalize(raw: list) -> list[Tok]:
    toks: list[Tok] = []
    i = 0
    while i < len(raw):
        name, text, line = raw[i]
        if name in ("T_OPEN_TAG", "T_OPEN_TAG_WITH_ECHO", "T_INLINE_HTML", "T_WHITESPACE"):
            i += 1
            continue
        if name == "T_CLOSE_TAG":
            toks.append(Tok("op", ";", line))
        elif name == "" and text in ('"', "`"):
            j = i + 1
            while j < len(raw) and not (raw[j][0] == "" and raw[j][1] == text):
                j += 1
            toks.append(Tok("istr", "".join(r[1] for r in raw[i:j + 1]), line))
            i = j + 1
            continue
        elif name == "T_START_HEREDOC":
            j = i + 1
            while j < len(raw) and raw[j][0] != "T_END_HEREDOC":
                j += 1
            toks.append(Tok("istr", "".join(r[1] for r in raw[i:j + 1]), line))
            i = j + 1
            continue
        elif name in ("T_COMMENT", "T_DOC_COMMENT"):
            toks.append(Tok("comment", text, line))
        elif name == "T_VARIABLE":
            toks.append(Tok("var", text, line))
        elif name == "T_CONSTANT_ENCAPSED_STRING":
            toks.append(Tok("str", text, line, _unquote(text)))
        elif name in ("T_LNUMBER", "T_DNUMBER"):
            toks.append(Tok("num", text, line))
        elif name == "T_ATTRIBUTE":
            toks.append(Tok("op", "#[", line))
        elif name.endswith("_CAST"):
            inner = text.strip("()").strip()
            toks += [Tok("op", "(", line), Tok("name", inner, line), Tok("op", ")", line)]
        elif name and NAME_RE.fullmatch(text):
            toks.append(Tok("name", text, line))
        else:
            toks.append(Tok("op", text, line))
        i += 1
    return toks


def php_binary() -> tuple[str, str] | None:
    """Return (path, version) of a usable PHP 8 binary with token_get_all(), else None."""
    php = shutil.which("php")
    if not php:
        return None
    probe = "echo (PHP_VERSION_ID >= 80000 && function_exists('token_get_all')) ? PHP_VERSION : 'no';"
    for args in ([php, "-n", "-r", probe], [php, "-r", probe]):
        try:
            out = subprocess.run(args, capture_output=True, text=True, timeout=20).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            continue
        if out and out != "no" and re.match(r"^\d+\.\d+", out):
            return args[0] if args[1] != "-n" else php + "\0-n", out
    return None


def php_tokenize_files(php: str, paths: list[Path]) -> dict[Path, list[Tok]]:
    cmd = php.split("\0") + ["-d", "memory_limit=-1", "-r", PHP_TOKENIZER]
    result: dict[Path, list[Tok]] = {}
    for k in range(0, len(paths), 400):
        batch = paths[k:k + 400]
        proc = subprocess.run(cmd, input="\n".join(str(p) for p in batch), capture_output=True, text=True,
                              timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(f"php tokenizer failed: {proc.stderr.strip()[:200]}")
        by_name = {str(p): p for p in batch}
        for raw_line in proc.stdout.splitlines():
            if not raw_line.strip():
                continue
            rec = json.loads(raw_line)
            p = by_name.get(rec["f"])
            if p is not None and "t" in rec:
                result[p] = php_normalize(rec["t"])
    return result


# --- structure ----------------------------------------------------------------------------------------


@dataclass
class Func:
    name: str | None
    kind: str                     # method, function, closure, arrow
    start: int
    params: tuple[int, int]
    body: tuple[int, int] | None  # inclusive token indices of { } (arrow: expression start, end exclusive)
    is_static: bool
    cls: "Cls | None" = None


@dataclass
class Cls:
    fqn: str
    short: str
    kind: str
    model: "Model"
    start: int
    body: tuple[int, int]
    attrs: list[str] = field(default_factory=list)
    extends: str | None = None
    implements: list[str] = field(default_factory=list)
    methods: dict[str, Func] = field(default_factory=dict)

    @property
    def line(self) -> int:
        return self.model.code[self.start].line


class Model:
    """One PHP file: tokens without comments, bracket matches, imports, classes and functions."""

    def __init__(self, rel: str, toks: list[Tok], lines: list[str]):
        self.rel = rel
        self.lines = lines
        self.comments = [t for t in toks if t.kind == "comment"]
        self.code = [t for t in toks if t.kind != "comment"]
        self.match: dict[int, int] = {}
        self.namespace = ""
        self.imports: dict[str, str] = {}
        self.classes: list[Cls] = []
        self.funcs: list[Func] = []
        self._match_brackets()
        self._parse()

    # brackets
    def _match_brackets(self) -> None:
        stack: list[int] = []
        for i, t in enumerate(self.code):
            if t.kind != "op":
                continue
            if t.text in OPENERS:
                stack.append(i)
            elif t.text in CLOSERS and stack:
                j = stack.pop()
                self.match[j] = i
                self.match[i] = j

    def tok(self, i: int) -> Tok:
        return self.code[i] if 0 <= i < len(self.code) else Tok("op", "", 0)

    def is_op(self, i: int, *texts: str) -> bool:
        t = self.tok(i)
        return t.kind == "op" and t.text in texts

    def is_name(self, i: int, *names: str) -> bool:
        t = self.tok(i)
        return t.kind == "name" and t.low.lstrip("\\") in names

    def close(self, i: int) -> int:
        return self.match.get(i, i)

    # names
    def resolve(self, name: str) -> str:
        if name.startswith("\\"):
            return name[1:].lower()
        low = name.lower()
        if low in ("self", "static", "parent"):
            return low
        head, _, rest = low.partition("\\")
        if head in self.imports:
            return self.imports[head] + ("\\" + rest if rest else "")
        return (self.namespace.lower() + "\\" + low) if self.namespace else low

    def resolve_class_const(self, i: int) -> str | None:
        """For tokens `Name :: class` starting at i, return the resolved FQN."""
        if self.tok(i).kind == "name" and self.is_op(i + 1, "::") and self.is_name(i + 2, "class"):
            return self.resolve(self.tok(i).text)
        return None

    def expr_end(self, i: int, limit: int) -> int:
        j = i
        while j < limit:
            t = self.code[j]
            if t.kind == "op":
                if t.text in OPENERS:
                    j = self.close(j) + 1
                    continue
                if t.text in (";", ",") or t.text in CLOSERS:
                    return j
            j += 1
        return limit

    def args(self, open_idx: int) -> list[tuple[int, int]]:
        """Argument ranges [a, b) inside the parentheses or brackets that open at open_idx."""
        end = self.close(open_idx)
        out, a, j = [], open_idx + 1, open_idx + 1
        while j < end:
            t = self.code[j]
            if t.kind == "op" and t.text in OPENERS:
                j = self.close(j) + 1
                continue
            if t.kind == "op" and t.text == ",":
                out.append((a, j))
                a = j + 1
            j += 1
        if a < end:
            out.append((a, end))
        return out

    def is_call(self, i: int) -> bool:
        """Global function call: name ( , not a method, static call, declaration or `new`."""
        if self.tok(i).kind != "name" or not self.is_op(i + 1, "("):
            return False
        prev = self.tok(i - 1)
        if prev.kind == "op" and prev.text in ("->", "?->", "::"):
            return False
        return not (prev.kind == "name" and prev.low in ("function", "fn", "new", "const"))

    def snippet(self, line: int) -> str:
        text = self.lines[line - 1].strip() if 0 < line <= len(self.lines) else ""
        return text if len(text) <= 160 else text[:157] + "..."

    # parsing
    def _parse(self) -> None:
        code = self.code
        n = len(code)
        i = 0
        while i < n:
            t = code[i]
            if t.kind == "name":
                low = t.low
                prev = self.tok(i - 1)
                after_arrow = prev.kind == "op" and prev.text in ("->", "?->", "::")
                if low == "namespace" and not after_arrow and self.tok(i + 1).kind == "name":
                    self.namespace = self.tok(i + 1).text.lstrip("\\")
                elif low == "use" and not after_arrow and not self.is_op(i - 1, ")") \
                        and not any(c.body[0] < i < c.body[1] for c in self.classes):
                    self._parse_use(i)
                elif low in ("class", "interface", "trait", "enum") and not after_arrow:
                    self._parse_class(i)
                elif low == "function" and not after_arrow:
                    self._parse_function(i)
                elif low == "fn" and not after_arrow and (self.is_op(i + 1, "(") or
                                                          (self.is_op(i + 1, "&") and self.is_op(i + 2, "("))):
                    self._parse_arrow(i)
            i += 1
        for f in self.funcs:
            f.cls = self.class_at(f.start)
            if f.cls is not None and f.kind == "method" and f.name:
                inner = [c for c in self.classes if c.body[0] < f.start < c.body[1]]
                if inner and max(inner, key=lambda c: c.body[0]) is f.cls:
                    f.cls.methods.setdefault(f.name.lower(), f)

    def _parse_use(self, u: int) -> None:
        code = self.code
        j = u + 1
        if self.is_name(j, "function", "const"):
            return
        end = j
        while end < len(code) and not self.is_op(end, ";"):
            end += 1
        if self.tok(j).kind == "name" and self.is_op(j + 1, "{"):
            prefix = self.tok(j).text.strip("\\")
            for a, b in self.args(j + 1):
                self._add_import(prefix + "\\" + self.tok(a).text.strip("\\"), a, b)
            return
        for a, b in self._split(j, end):
            if self.tok(a).kind == "name":
                self._add_import(self.tok(a).text.strip("\\"), a, b)

    def _split(self, a: int, b: int) -> list[tuple[int, int]]:
        out, s = [], a
        for k in range(a, b):
            if self.is_op(k, ","):
                out.append((s, k))
                s = k + 1
        out.append((s, b))
        return out

    def _add_import(self, full: str, a: int, b: int) -> None:
        alias = full.split("\\")[-1]
        for k in range(a, b):
            if self.is_name(k, "as") and self.tok(k + 1).kind == "name":
                alias = self.tok(k + 1).text
        self.imports[alias.lower()] = full.lower()

    def _attrs_before(self, i: int) -> list[str]:
        out = []
        j = i - 1
        while j >= 0:
            t = self.code[j]
            if t.kind == "name" and t.low in MODIFIERS:
                j -= 1
                continue
            if t.kind == "op" and t.text == "]" and self.is_op(self.close(j), "#["):
                o = self.close(j)
                for a, _b in self.args(o):
                    if self.tok(a).kind == "name":
                        out.append(self.resolve(self.tok(a).text))
                j = o - 1
                continue
            break
        return out

    def _modifiers_before(self, i: int) -> set[str]:
        mods = set()
        j = i - 1
        while j >= 0:
            t = self.code[j]
            if t.kind == "name" and t.low in MODIFIERS:
                mods.add(t.low)
                j -= 1
            elif t.kind == "op" and t.text == "]" and self.is_op(self.close(j), "#["):
                j = self.close(j) - 1
            else:
                break
        return mods

    def _parse_class(self, i: int) -> None:
        code = self.code
        anonymous = self.is_name(i - 1, "new")
        if not anonymous and self.tok(i + 1).kind != "name":
            return
        short = "" if anonymous else self.tok(i + 1).text
        j = i + 1
        extends, implements = None, []
        while j < len(code) and not self.is_op(j, "{"):
            if self.is_op(j, ";"):
                return
            if self.is_op(j, "("):
                j = self.close(j)
            elif self.is_name(j, "extends") and self.tok(j + 1).kind == "name":
                extends = self.resolve(self.tok(j + 1).text)
            elif self.is_name(j, "implements"):
                k = j + 1
                while k < len(code) and not self.is_op(k, "{"):
                    if self.tok(k).kind == "name":
                        implements.append(self.resolve(self.tok(k).text))
                    k += 1
            j += 1
        if j >= len(code):
            return
        fqn = ((self.namespace + "\\" + short) if self.namespace else short).lower() if short else \
            f"{self.rel}@anonymous{code[i].line}"
        self.classes.append(Cls(fqn, short, code[i].low, self, i, (j, self.close(j)),
                                self._attrs_before(i), extends, implements))

    def _parse_function(self, i: int) -> None:
        j = i + 1
        if self.is_op(j, "&"):
            j += 1
        name = None
        if self.tok(j).kind == "name":
            name = self.tok(j).text
            j += 1
        if not self.is_op(j, "("):
            return
        params = (j, self.close(j))
        k = params[1] + 1
        if self.is_name(k, "use") and self.is_op(k + 1, "("):
            k = self.close(k + 1) + 1
        while k < len(self.code) and not self.is_op(k, "{", ";", "=>") and not self.is_op(k, ",", ")"):
            k += 1
        body = (k, self.close(k)) if self.is_op(k, "{") else None
        mods = self._modifiers_before(i)
        kind = "closure" if name is None else ("method" if self.class_at(i) and self._in_class_body(i) else "function")
        self.funcs.append(Func(name, kind, i, params, body, "static" in mods))

    def _in_class_body(self, i: int) -> bool:
        cls = self.class_at(i)
        if cls is None:
            return False
        return not any(f.body and f.body[0] < i < f.body[1] and cls.body[0] < f.start
                       for f in self.funcs)

    def _parse_arrow(self, i: int) -> None:
        j = i + 1 + (1 if self.is_op(i + 1, "&") else 0)
        params = (j, self.close(j))
        k = params[1] + 1
        while k < len(self.code) and not self.is_op(k, "=>"):
            if self.is_op(k, ";", "{"):
                return
            k += 1
        end = self.expr_end(k + 1, len(self.code))
        self.funcs.append(Func(None, "arrow", i, params, (k + 1, end), self.is_name(i - 1, "static")))

    # lookups
    def class_at(self, i: int) -> Cls | None:
        inner = [c for c in self.classes if c.body[0] < i < c.body[1]]
        return max(inner, key=lambda c: c.body[0]) if inner else None

    def func_at(self, i: int) -> Func | None:
        inner = [f for f in self.funcs if f.body and f.body[0] <= i <= f.body[1] and f.start < i]
        return max(inner, key=lambda f: f.body[0]) if inner else None

    def nested_ranges(self, a: int, b: int) -> list[tuple[int, int]]:
        """Closures and arrow functions that start inside [a, b): their code runs later, not now."""
        return [(f.start, f.body[1]) for f in self.funcs
                if f.kind in ("closure", "arrow") and f.body and a <= f.start < b]

    def in_ranges(self, i: int, ranges: list[tuple[int, int]]) -> bool:
        return any(a <= i <= b for a, b in ranges)


# --- taint --------------------------------------------------------------------------------------------


def words(identifier: str) -> list[str]:
    s = identifier.lstrip("$\\").split("\\")[-1]
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    return [w for w in re.split(r"[_\W]+", s.lower()) if w]


def tenant_like(identifier: str) -> bool:
    ws = words(identifier)
    if any(w in TENANT_WORDS for w in ws):
        return True
    return any(a == "current" and b in CURRENT_WORDS for a, b in zip(ws, ws[1:]))


def tenant_type(short: str) -> bool:
    """A class name that reads like the holder of the current tenant: TenantContext, CurrentWorkspace, Tenant."""
    ws = words(short)
    if not ws:
        return False
    if any(a == "current" and b in CURRENT_WORDS | TENANT_WORDS for a, b in zip(ws, ws[1:])):
        return True
    if any(w in TENANT_WORDS for w in ws) and ws[-1] in ("context", "state", "holder"):
        return True
    return len(ws) == 1 and ws[0] in ("tenant", "tenancy")


def taint(m: Model, a: int, b: int, *, nested: bool = False) -> list[str]:
    """Evidence that tokens [a, b) read the request, auth, session, the current user or a tenant."""
    out: list[str] = []
    for _i, ev in taint_hits(m, a, b, nested=nested):
        if ev not in out:
            out.append(ev)
    return out


def taint_hits(m: Model, a: int, b: int, *, nested: bool = False) -> list[tuple[int, str]]:
    """(token index, evidence) for every read of per-request state in [a, b). Nested closures run later
    and are skipped unless nested=True."""
    skip = [] if nested else m.nested_ranges(a, b)
    found: list[tuple[int, str]] = []
    i = 0

    def add(s: str) -> None:
        found.append((i, s))

    for i in range(a, min(b, len(m.code))):
        if skip and m.in_ranges(i, skip):
            continue
        t = m.code[i]
        prev, nxt = m.tok(i - 1), m.tok(i + 1)
        if t.kind == "name":
            low = t.low.lstrip("\\")
            if low in TAINT_HELPERS and m.is_call(i):
                add(f"{low}()")
                continue
            if nxt.kind == "op" and nxt.text == "::" and not m.is_name(i + 2, "class"):
                fq = m.resolve(t.text)
                short = low.split("\\")[-1]
                if short in FACADES and (fq == FACADES[short] or fq == short or "\\" not in fq
                                         or fq.endswith("\\" + short) and fq.split("\\")[0] != "illuminate"):
                    if not (fq == "illuminate\\http\\request" or m.is_name(i + 2, "create", "capture", "macro")):
                        add(f"{t.text}::")
                        continue
                if tenant_like(t.text):
                    add(f"{t.text}::")
                    continue
            if prev.kind == "op" and prev.text in ("->", "?->") and low == "user" and nxt.text == "(":
                add("->user()")
                continue
            if tenant_like(t.text) and not m.is_op(i + 1, "::") and not (prev.kind == "name" and prev.low in ("new", "instanceof")):
                if prev.kind == "op" and prev.text in ("->", "?->"):
                    add(f"->{t.text}")
                elif m.is_call(i):
                    add(f"{t.text}()")
        elif t.kind == "var":
            low = t.low
            if low in SUPERGLOBALS:
                add(t.text)
            elif low == "$request":
                add("$request")
            elif low == "$this" and m.is_op(i + 1, "->", "?->") and m.tok(i + 2).kind == "name":
                prop = m.tok(i + 2).text
                if prop.lower() == "request":
                    add("$this->request")
            elif tenant_like(t.text):
                add(t.text)
        elif t.kind == "istr" and not t.text.startswith("<<<'"):
            for mm in ISTR_VAR_RE.finditer(t.text):
                v, prop = "$" + mm.group(1), mm.group(2) or ""
                if v.lower() in SUPERGLOBALS or v.lower() == "$request" or tenant_like(v) or (prop and tenant_like(prop)):
                    add(f'"{mm.group(0)}"')
        elif t.kind == "str" and t.value is not None:
            if prev.kind == "op" and prev.text in ("(", "["):
                head = m.tok(i - 2)
                if head.kind in ("name", "var") or (head.kind == "op" and head.text == ")"):
                    v = t.value.lower()
                    if v in TAINT_KEYS or tenant_like(t.value):
                        add(f"'{t.value}'")
    return found


def local_taint(m: Model, f: Func, a: int, b: int) -> list[str]:
    """Taint of local variables used in [a, b), through their assignments earlier in function f."""
    found: list[str] = []
    names = {m.code[k].low for k in range(a, b) if m.code[k].kind == "var" and m.code[k].low != "$this"}
    if not names or not f.body:
        return found
    for k in range(f.body[0], a):
        t = m.code[k]
        if t.kind == "var" and t.low in names and m.is_op(k + 1, "=", "??=", ".="):
            found += taint(m, k + 2, m.expr_end(k + 2, f.body[1]))
    for k in range(f.params[0], f.params[1]):
        t = m.code[k]
        if t.kind == "var" and t.low in names and tenant_like(t.text):
            found.append(t.text)
    return found


def db_hints(m: Model, a: int, b: int) -> list[str]:
    found = []
    for i in range(a, min(b, len(m.code))):
        t = m.code[i]
        if t.kind != "name":
            continue
        prev = m.tok(i - 1)
        if m.is_op(i + 1, "(") and prev.kind == "op":
            if prev.text == "::" and (t.low in DB_HINTS_STATIC or m.is_name(i - 2, "db", "cache")):
                found.append(f"{m.tok(i - 2).text}::{t.text}()")
            elif prev.text in ("->", "?->") and t.low in DB_HINTS_METHOD:
                found.append(f"->{t.text}()")
        elif t.low in ("cache", "db") and m.is_call(i):
            found.append(f"{t.text}()")
    return found


def is_literal(m: Model, a: int, b: int) -> bool:
    """True for a constant right-hand side: scalars, null, booleans, [] and arrays of those."""
    for i in range(a, b):
        t = m.code[i]
        if t.kind in ("str", "num"):
            continue
        if t.kind == "name" and t.low in ("null", "true", "false"):
            continue
        if t.kind == "name" and m.is_op(i + 1, "::") and m.is_name(i + 2, "class"):
            continue
        if t.kind == "name" and t.low == "class" and m.is_op(i - 1, "::"):
            continue
        if t.kind == "op" and t.text in ("[", "]", ",", "=>", "-", "::"):
            continue
        return False
    return True


# --- context ------------------------------------------------------------------------------------------


def is_provider(cls: Cls | None) -> bool:
    if cls is None:
        return False
    return cls.short.lower().endswith("serviceprovider") or (cls.extends or "").endswith("serviceprovider")


def is_console(m: Model, cls: Cls | None) -> bool:
    if "/console/" in ("/" + m.rel.lower()):
        return True
    return cls is not None and (cls.extends or "").endswith("\\command") and "/jobs/" not in m.rel.lower()


def boot_context(m: Model, i: int) -> bool:
    """Code that runs once per worker: providers, boot hooks, routes and bootstrap files, top-level code."""
    rel = m.rel.lower()
    if rel.startswith(("routes/", "bootstrap/", "config/")):
        return True
    f = m.func_at(i)
    while f is not None and f.kind in ("closure", "arrow"):
        f = m.func_at(f.start - 1) if f.start > 0 else None
    if f is None:
        return True
    cls = f.cls
    name = (f.name or "").lower()
    if is_provider(cls):
        return True
    if f.is_static and name.startswith("boot"):
        return True
    if name in BOOT_METHODS and is_provider(cls):
        return True
    return is_console(m, cls)


def reset_context(m: Model, i: int) -> bool:
    f = m.func_at(i)
    while f is not None and f.kind in ("closure", "arrow"):
        f = m.func_at(f.start - 1) if f.start > 0 else None
    return f is not None and bool(RESET_METHOD_RE.match(f.name or ""))


def container_receiver(m: Model, k: int) -> bool:
    """Is the method at index k (after -> or ::) called on the service container?"""
    op = m.tok(k - 1)
    r = k - 2
    if op.text == "::":
        return m.is_name(r, "app", "illuminate\\support\\facades\\app")
    if op.text not in ("->", "?->"):
        return False
    t = m.tok(r)
    if t.kind == "var" and t.low in ("$app", "$container", "$laravel"):
        return True
    if t.kind == "name" and t.low in ("app", "container", "laravel") and m.is_op(r - 1, "->") and m.tok(r - 2).low == "$this":
        return True
    if t.kind == "op" and t.text == ")":
        o = m.close(r)
        if m.is_name(o - 1, "app", "resolve") and m.is_call(o - 1) and o + 1 == r:
            return True
        if m.is_name(o - 1, "getinstance") and m.is_op(o - 2, "::"):
            return True
    return False


def key_of(m: Model, a: int, b: int) -> str | None:
    t = m.tok(a)
    if t.kind == "str" and b == a + 1:
        return t.value
    fq = m.resolve_class_const(a)
    if fq and b == a + 3:
        return fq
    return None


# --- scanner ------------------------------------------------------------------------------------------


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    severity: str
    message: str
    evidence: str
    fix: str
    allowed: str | None = None
    note: str | None = None

    def as_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if v is not None}
        return d


class Scanner:
    def __init__(self, root: Path, includes: list[str], tokenizer: str = "auto"):
        self.root = root
        self.includes = includes
        self.tokenizer = tokenizer
        self.mode = ""
        self.models: list[Model] = []
        self.index: dict[str, Cls] = {}
        self.findings: list[Finding] = []
        self.notes: list[str] = []
        self._ctor_memo: dict[str, list[str]] = {}
        self._memo_memo: dict[str, tuple[list[str], list[str]]] = {}

    # files
    def files(self) -> list[Path]:
        out: list[Path] = []
        dirs = ["app", "routes"] + self.includes
        for d in dirs:
            base = self.root / d
            if base.is_file() and base.suffix == ".php":
                out.append(base)
                continue
            if not base.is_dir():
                if d in self.includes:
                    self.notes.append(f"--include {d}: not found under the root, skipped")
                continue
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = sorted(x for x in dirnames if x not in ("vendor", "node_modules", "tests", ".git"))
                out += [Path(dirpath) / f for f in sorted(filenames) if f.endswith(".php")]
        for f in ("bootstrap/app.php", "config/octane.php"):
            if (self.root / f).is_file():
                out.append(self.root / f)
        seen, uniq = set(), []
        for p in out:
            if p.resolve() not in seen:
                seen.add(p.resolve())
                uniq.append(p)
        return uniq

    def load(self) -> None:
        paths = self.files()
        tokens: dict[Path, list[Tok]] = {}
        php = php_binary() if self.tokenizer in ("auto", "php") else None
        if self.tokenizer == "php" and php is None:
            raise UsageError("--tokenizer php: no PHP 8 binary with token_get_all() on PATH")
        if php is not None:
            try:
                tokens = php_tokenize_files(php[0], paths)
                self.mode = f"php token_get_all (PHP {php[1]})"
            except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as e:
                if self.tokenizer == "php":
                    raise UsageError(str(e))
                tokens = {}
                self.notes.append(f"php tokenizer failed, fell back to the built-in tokenizer: {e}")
        if not self.mode:
            self.mode = "built-in python tokenizer" + ("" if self.tokenizer == "python" else " (no usable php on PATH)")
        for p in paths:
            try:
                src = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                self.notes.append(f"unreadable: {p}")
                continue
            toks = tokens.get(p)
            if toks is None:
                toks = py_tokenize(src)
            rel = p.relative_to(self.root).as_posix()
            m = Model(rel, toks, src.splitlines())
            self.models.append(m)
            for c in m.classes:
                self.index.setdefault(c.fqn, c)

    # reporting
    def add(self, m: Model, line: int, rule: str, severity: str, message: str, evidence: str = "") -> None:
        allowed, note = self._allow(m, line, rule)
        ev = evidence or m.snippet(line)
        f = Finding(m.rel, line, rule, severity, message, ev, FIX[rule], allowed, note)
        if not any(x.file == f.file and x.line == f.line and x.rule == f.rule for x in self.findings):
            self.findings.append(f)

    def _allow(self, m: Model, line: int, rule: str) -> tuple[str | None, str | None]:
        note = None
        for c in m.comments:
            for mm in ALLOW_RE.finditer(c.text):
                at = c.line + c.text[:mm.start()].count("\n")
                if at not in (line, line - 1) or mm.group(1) != rule:
                    continue
                reason = mm.group(2).strip()
                if len(reason) >= MIN_REASON and re.search(r"[A-Za-z]{3,}", reason):
                    return reason, None
                note = "allow comment ignored: it needs a reason"
        return None, note

    # class helpers
    def cls(self, fqn: str | None) -> Cls | None:
        return self.index.get(fqn) if fqn else None

    def ancestors(self, c: Cls) -> list[Cls]:
        out, seen = [], set()
        cur = c
        while cur is not None and cur.fqn not in seen:
            seen.add(cur.fqn)
            out.append(cur)
            cur = self.cls(cur.extends)
        return out

    def is_request_type(self, fqn: str) -> bool:
        if fqn in REQUEST_TYPES:
            return True
        c = self.cls(fqn)
        if c is None:
            return tenant_type(fqn.split("\\")[-1])
        for a in self.ancestors(c):
            if (a.extends or "") in REQUEST_TYPES or any(i in REQUEST_TYPES for i in a.implements):
                return True
        return tenant_type(c.short) and not self._is_model(c)

    def _is_model(self, c: Cls) -> bool:
        return any((a.extends or "").endswith(("\\model", "eloquent\\model")) for a in self.ancestors(c))

    def ctor(self, c: Cls) -> Func | None:
        for a in self.ancestors(c):
            f = a.methods.get("__construct")
            if f is not None:
                return f
        return None

    def params(self, f: Func) -> list[dict]:
        m = f.cls.model if f.cls else None
        if m is None:
            return []
        out = []
        for a, b in m.args(f.params[0]):
            attrs, types, raw, var = [], [], [], None
            j = a
            while j < b:
                t = m.code[j]
                if t.kind == "op" and t.text == "#[":
                    for x, _y in m.args(j):
                        if m.tok(x).kind == "name":
                            attrs.append(m.resolve(m.tok(x).text))
                    j = m.close(j) + 1
                    continue
                if t.kind == "var":
                    var = t.text
                    break
                if t.kind == "name" and t.low not in MODIFIERS:
                    types.append(m.resolve(t.text))
                    raw.append(t.text.lstrip("\\").split("\\")[-1])
                j += 1
            out.append({"attrs": attrs, "types": types, "raw": raw, "var": var, "line": m.tok(a).line})
        return out

    def ctor_reasons(self, c: Cls, depth: int = 0, stack: frozenset = frozenset()) -> list[str]:
        """Why constructing c captures per-request state. Empty list: it does not, as far as we can see."""
        if c.fqn in self._ctor_memo:
            return self._ctor_memo[c.fqn]
        if c.fqn in stack or depth > 3:
            return []
        f = self.ctor(c)
        reasons: list[str] = []
        if f is not None and f.cls is not None:
            m = f.cls.model
            for p in self.params(f):
                attr = next((x for x in p["attrs"] if x.split("\\")[-1] in REQUEST_ATTRS
                             and (x.startswith(ATTR_NS) or "\\" not in x)), None)
                if attr:
                    reasons.append(f"#[{attr.split(chr(92))[-1].title()}] {p['var']} ({m.rel}:{p['line']})")
                    continue
                for ty, rawty in zip(p["types"], p["raw"]):
                    if self.is_request_type(ty):
                        reasons.append(f"{rawty} {p['var']} injected ({m.rel}:{p['line']})")
                        break
                    dep = self.cls(ty)
                    if dep is not None and dep.kind == "class":
                        sub = self.ctor_reasons(dep, depth + 1, stack | {c.fqn})
                        if sub:
                            reasons.append(f"injects {dep.short}, which captures {sub[0]}")
                            break
            if f.body:
                for ev in taint(m, f.body[0], f.body[1]):
                    reasons.append(f"constructor reads {ev} ({m.rel}:{m.code[f.body[0]].line})")
        self._ctor_memo[c.fqn] = reasons
        return reasons

    def container_params(self, c: Cls) -> list[str]:
        f = self.ctor(c)
        if f is None:
            return []
        return [f"{rawty} {p['var']}" for p in self.params(f) for ty, rawty in zip(p["types"], p["raw"])
                if ty in CONTAINER_TYPES]

    def memo_reasons(self, c: Cls) -> tuple[list[str], list[str]]:
        """Instance-property writes outside the constructor, split by risk.

        First list: a value derived from the request, user or tenant, stored without that identity in the
        key, so a reused instance serves it to someone else. Second list: memos that can only go stale
        (keyed by the tenant or user, or not derived from the request)."""
        if c.fqn in self._memo_memo:
            return self._memo_memo[c.fqn]
        cross, stale = [], []
        for a in self.ancestors(c):
            m = a.model
            for name, f in a.methods.items():
                if name == "__construct" or not f.body or f.is_static or REGISTRY_METHOD_RE.match(name):
                    continue
                params_ev = taint(m, f.params[0], f.params[1] + 1)
                for i in range(f.body[0], f.body[1]):
                    if not (m.tok(i).low == "$this" and m.is_op(i + 1, "->") and m.tok(i + 2).kind == "name"):
                        continue
                    j = i + 3
                    while m.is_op(j, "["):
                        j = m.close(j) + 1
                    if not m.is_op(j, *ASSIGN_OPS):
                        continue
                    keyed = j > i + 3
                    memo = keyed or m.tok(j).text == "??="
                    end = m.expr_end(j + 1, f.body[1])
                    key_ev = (taint(m, i + 3, j) or local_taint(m, f, i + 3, j)) if keyed else []
                    val_ev = taint(m, j + 1, end) or (params_ev if memo else [])
                    where = f"$this->{m.tok(i + 2).text} in {a.short}::{f.name}() ({m.rel}:{m.tok(i).line})"
                    if val_ev and not key_ev:
                        cross.append(f"{where} from {val_ev[0]}")
                    elif memo:
                        stale.append(where + (f", keyed by {key_ev[0]}" if key_ev else ""))
        self._memo_memo[c.fqn] = (cross, stale)
        return cross, stale

    # run
    def run(self) -> list[Finding]:
        self.load()
        flush_model = next((m for m in self.models if m.rel == "config/octane.php"), None)
        bindings: list[tuple[Model, int, str, bool]] = []
        for m in self.models:
            if m.rel.startswith("config/"):
                continue
            self.rule_static_props(m)
            self.rule_static_vars(m)
            self.rule_object_ids(m)
            self.rule_globals(m)
            bindings += self.collect_instances(m)
            self.rule_singletons(m)
        for c in list(self.index.values()):
            m = c.model
            if m.rel.startswith("config/"):
                continue
            self.rule_singleton_attr(c)
            self.rule_controller(c)
            self.rule_middleware(c)
            self.rule_job(c)
        self.rule_flush(flush_model, bindings)
        order = {s: k for k, s in enumerate(SEVERITIES)}
        self.findings.sort(key=lambda f: (order[f.severity], f.file, f.line, f.rule))
        return self.findings

    # OS01
    def rule_static_props(self, m: Model) -> None:
        code = m.code
        for i in range(len(code) - 2):
            if not (code[i].kind == "name" and m.is_op(i + 1, "::") and code[i + 2].kind == "var"):
                continue
            if m.is_op(i - 1, "->", "?->", "::"):
                continue
            j = i + 3
            sub_a = j
            while m.is_op(j, "["):
                j = m.close(j) + 1
            while m.is_op(j, "->", "?->") and m.tok(j + 1).kind == "name":
                j += 2
                while m.is_op(j, "["):
                    j = m.close(j) + 1
            op = m.tok(j)
            pre = m.tok(i - 1)
            pushed = m.is_name(i - 2, "array_push", "array_unshift", "array_splice") and m.is_op(i - 1, "(")
            if op.kind == "op" and op.text in ASSIGN_OPS:
                if op.text == "=" and m.is_op(j + 1, "&"):
                    pass
                rhs = (j + 1, m.expr_end(j + 1, len(code)))
            elif (op.kind == "op" and op.text in ("++", "--")) or (pre.kind == "op" and pre.text in ("++", "--")):
                rhs = (j, j)
            elif pushed:
                rhs = (i + 3, m.expr_end(i + 3, m.close(i - 1)))
                rhs = (rhs[0], m.close(i - 1))
            else:
                continue
            target = f"{code[i].text}::{code[i + 2].text}"
            ev = taint(m, sub_a, j) + taint(m, *rhs)
            fn = m.func_at(i)
            if not ev and fn is not None:
                ev = local_taint(m, fn, sub_a, j) + local_taint(m, fn, *rhs)
            boot = boot_context(m, i)
            ev = list(dict.fromkeys(ev))
            if ev:
                self.add(m, code[i].line, "OS01", "blocker",
                         f"static property {target} written with request, user or tenant data ({', '.join(ev[:3])})")
                continue
            if boot or reset_context(m, i):
                continue
            if self._weakmap(m, i, code[i + 2].low):
                continue
            keyed = j > sub_a
            literal = rhs[0] < rhs[1] and is_literal(m, *rhs) and not keyed
            if literal and op.text == "=":
                if m.tok(rhs[0]).low in ("null",) or (m.is_op(rhs[0], "[") and m.close(rhs[0]) == rhs[0] + 1):
                    continue
                self.add(m, code[i].line, "OS01", "low", f"static property {target} set to a constant at runtime (flag)")
                continue
            db = db_hints(m, *rhs)
            if db:
                self.add(m, code[i].line, "OS01", "high",
                         f"static property {target} caches query or cache results for the life of the worker ({db[0]})")
            elif keyed or pushed:
                self.add(m, code[i].line, "OS01", "medium",
                         f"static property {target} grows at runtime; entries survive into later requests and jobs")
            else:
                self.add(m, code[i].line, "OS01", "low",
                         f"static property {target} initialized lazily; fine only if the value is the same for every "
                         "request")

    def _weakmap(self, m: Model, i: int, var: str) -> bool:
        """The static holds a WeakMap: entries die with their key object, so they cannot outlive it."""
        cls = m.class_at(i)
        a, b = (cls.body if cls else (0, len(m.code)))
        for k in range(a, b):
            if m.code[k].kind == "var" and m.code[k].low == var:
                j = k + 1
                if m.is_op(j, "=", "??=") and m.is_name(j + 1, "new") and m.is_name(j + 2, "weakmap"):
                    return True
        return False

    # OS02
    def rule_static_vars(self, m: Model) -> None:
        code = m.code
        for i, t in enumerate(code):
            if not (t.kind == "name" and t.low == "static" and m.tok(i + 1).kind == "var"):
                continue
            f = m.func_at(i)
            if f is None or not f.body or not (f.body[0] < i < f.body[1]):
                continue
            if m.class_at(i) is not None and m.class_at(i).body[0] > f.body[0]:
                continue
            end = i
            while end < len(code) and not m.is_op(end, ";"):
                end += 1
            names = {code[k].low for k in range(i + 1, end) if code[k].kind == "var"
                     and (m.is_op(k - 1, ",") or k == i + 1)}
            init_ev = taint(m, i + 1, end)
            writes: list[tuple[int, int]] = []
            for k in range(end, f.body[1]):
                if code[k].kind == "var" and code[k].low in names:
                    j = k + 1
                    while m.is_op(j, "["):
                        j = m.close(j) + 1
                    if m.is_op(j, *ASSIGN_OPS):
                        writes.append((k, m.expr_end(j + 1, f.body[1])))
            ev = init_ev[:]
            db: list[str] = []
            for a, b in writes:
                ev += taint(m, a, b) or local_taint(m, f, a, b)
                db += db_hints(m, a, b)
            label = ", ".join(sorted(names))
            if ev:
                self.add(m, t.line, "OS02", "blocker",
                         f"static {label} keeps request, user or tenant data across calls ({ev[0]})")
            elif boot_context(m, i) and f.kind != "method":
                continue
            elif db:
                self.add(m, t.line, "OS02", "high", f"static {label} caches query or cache results per worker ({db[0]})")
            elif writes:
                self.add(m, t.line, "OS02", "medium", f"static {label} memoizes per-call data for the life of the worker")

    # OS03
    def _concrete_reasons(self, m: Model, a: int, b: int) -> tuple[list[str], str]:
        """Reasons for a binding's concrete argument tokens [a, b), and a label."""
        fq = m.resolve_class_const(a)
        if fq is not None:
            c = self.cls(fq)
            return (self.ctor_reasons(c) if c else []), (c.short if c else m.tok(a).text)
        t = m.tok(a)
        if t.kind == "str" and b == a + 1:
            c = self.cls((t.value or "").lower().lstrip("\\"))
            return (self.ctor_reasons(c) if c else []), (t.value or "")
        closure = next((f for f in m.funcs if f.start == a or (f.start == a + 1 and m.is_name(a, "static"))), None)
        start, end = (closure.body if closure and closure.body else (a, b))
        if closure and closure.kind == "closure":
            end += 1
        reasons = [f"binding reads {e}" for e in taint(m, start, end)]
        skip = m.nested_ranges(start, end)
        for k in range(start, end):
            if m.in_ranges(k, skip) and not (closure and k == closure.start):
                continue
            target = None
            if m.is_name(k, "new") and m.tok(k + 1).kind == "name":
                target = m.resolve(m.tok(k + 1).text)
            elif m.is_op(k, "(", "[") and m.resolve_class_const(k + 1):
                head = m.tok(k - 1)
                if head.kind in ("name", "var"):
                    target = m.resolve_class_const(k + 1)
            c = self.cls(target)
            if c is not None and c.kind == "class":
                sub = self.ctor_reasons(c)
                if sub:
                    reasons.append(f"builds {c.short}, which captures {sub[0]}")
        return reasons, "closure"

    def _report_singleton(self, m: Model, line: int, how: str, reasons: list[str], label: str, c: Cls | None) -> None:
        if reasons:
            self.add(m, line, "OS03", "blocker", f"{how} {label} captures per-request state: {'; '.join(reasons[:2])}")
        elif c is not None:
            cp = self.container_params(c)
            if cp:
                self.add(m, line, "OS03", "medium",
                         f"{how} {label} keeps the boot-time {', '.join(cp)}; later bindings and config changes are not seen")

    def rule_singletons(self, m: Model) -> None:
        code = m.code
        for k, t in enumerate(code):
            if t.kind != "name":
                continue
            low = t.low
            if low in ("singleton", "singletonif") and m.is_op(k + 1, "(") and container_receiver(m, k):
                args = m.args(k + 1)
                if not args:
                    continue
                if len(args) == 1:
                    fq = m.resolve_class_const(args[0][0])
                    c = self.cls(fq)
                    reasons = self.ctor_reasons(c) if c else []
                    label = c.short if c else m.tok(args[0][0]).text
                    self._report_singleton(m, t.line, "singleton", reasons, label, c)
                else:
                    reasons, label = self._concrete_reasons(m, *args[1])
                    fq = m.resolve_class_const(args[1][0])
                    self._report_singleton(m, t.line, "singleton", reasons, label, self.cls(fq))
            elif low == "withsingletons" and m.is_op(k + 1, "(") and m.is_op(k + 2, "["):
                self._singleton_array(m, k + 2, "withSingletons()")
            elif low == "instance" and m.is_op(k + 1, "(") and container_receiver(m, k) and boot_context(m, k):
                args = m.args(k + 1)
                if len(args) == 2 and m.is_name(args[1][0], "new"):
                    reasons, label = self._concrete_reasons(m, *args[1])
                    tname = m.resolve(m.tok(args[1][0] + 1).text)
                    self._report_singleton(m, t.line, "boot-time instance", reasons, m.tok(args[1][0] + 1).text,
                                           self.cls(tname))
        for i, t in enumerate(code):
            if t.kind == "var" and t.low == "$singletons" and m.is_op(i + 1, "=") and m.is_op(i + 2, "["):
                cls = m.class_at(i)
                if cls is not None and m.func_at(i) is None:
                    self._singleton_array(m, i + 2, "$singletons")

    def _singleton_array(self, m: Model, open_idx: int, how: str) -> None:
        for a, b in m.args(open_idx):
            k = a
            for j in range(a, b):
                if m.is_op(j, "=>"):
                    k = j + 1
            fq = m.resolve_class_const(k)
            c = self.cls(fq)
            if c is not None:
                self._report_singleton(m, m.tok(a).line, f"{how} entry", self.ctor_reasons(c), c.short, c)

    def rule_singleton_attr(self, c: Cls) -> None:
        if any(a == ATTR_NS + "singleton" or a == "singleton" for a in c.attrs):
            self._report_singleton(c.model, c.line, "#[Singleton] class", self.ctor_reasons(c), c.short, c)

    # OS04
    def rule_controller(self, c: Cls) -> None:
        if c.kind != "class" or not (c.short.lower().endswith("controller") or "\\controllers\\" in c.fqn):
            return
        f = c.methods.get("__construct")
        if f is None or not f.body:
            return
        m = c.model
        stored: set[int] = set()
        skip = m.nested_ranges(f.body[0], f.body[1])
        for i in range(f.body[0], f.body[1]):
            if m.in_ranges(i, skip):
                continue
            if m.tok(i).low == "$this" and m.is_op(i + 1, "->") and m.tok(i + 2).kind == "name":
                j = i + 3
                while m.is_op(j, "["):
                    j = m.close(j) + 1
                if m.is_op(j, *ASSIGN_OPS):
                    hits = taint_hits(m, j + 1, m.expr_end(j + 1, f.body[1]))
                    stored |= {k for k, _ in hits}
                    if hits:
                        self.add(m, m.tok(i).line, "OS04", "blocker",
                                 f"{c.short} constructor stores {hits[0][1]} in $this->{m.tok(i + 2).text}; "
                                 "the instance can outlive the request")
        for k, ev in taint_hits(m, f.body[0], f.body[1]):
            if k not in stored:
                self.add(m, m.code[k].line, "OS04", "high", f"{c.short} constructor reads {ev}; it runs once per "
                         "controller instance, which the test client and an escaping exception under Octane reuse")
        for p in self.params(f):
            for ty, rawty in zip(p["types"], p["raw"]):
                dep = self.cls(ty)
                if self.is_request_type(ty) or any(a.split("\\")[-1] in REQUEST_ATTRS for a in p["attrs"]):
                    self.add(m, p["line"], "OS04", "high",
                             f"{c.short} constructor injects {rawty} {p['var']}; inject it into the action")
                    break
                if dep is None or dep.kind != "class":
                    continue
                reasons = self.ctor_reasons(dep)
                tainted, plain = self.memo_reasons(dep)
                if reasons:
                    self.add(m, p["line"], "OS04", "high",
                             f"{c.short} constructor injects {dep.short}, which captures {reasons[0]}")
                elif tainted:
                    self.add(m, p["line"], "OS04", "high",
                             f"{c.short} constructor injects {dep.short}, which memoizes request data without the "
                             f"user or tenant in the key: {tainted[0]}")
                elif plain:
                    self.add(m, p["line"], "OS04", "medium",
                             f"{c.short} constructor injects stateful {dep.short} ({plain[0]}); a reused controller "
                             "serves stale values, so resolve it per call")
                break

    # OS05
    def collect_instances(self, m: Model) -> list[tuple[Model, int, str, bool]]:
        out = []
        for k, t in enumerate(m.code):
            if t.kind == "name" and t.low == "instance" and m.is_op(k + 1, "(") and container_receiver(m, k):
                args = m.args(k + 1)
                if len(args) != 2:
                    continue
                key = key_of(m, *args[0])
                if key is None or boot_context(m, k):
                    continue
                out.append((m, k, key, m.tok(args[0][0]).kind == "str"))
        return out

    def rule_flush(self, fm: Model | None, bindings: list[tuple[Model, int, str, bool]]) -> None:
        if fm is None:
            if bindings:
                self.notes.append("config/octane.php not found: flush comparison skipped")
            return
        entries: list[tuple[str, int]] = []
        for i, t in enumerate(fm.code):
            if t.kind == "str" and t.value == "flush" and fm.is_op(i + 1, "=>") and fm.is_op(i + 2, "["):
                for a, b in fm.args(i + 2):
                    key = key_of(fm, a, b)
                    if key is None:
                        self.notes.append(f"config/octane.php:{fm.tok(a).line}: flush entry not a literal, not compared")
                    else:
                        entries.append((key, fm.tok(a).line))
        flushed = {k.lower() for k, _ in entries}
        bound = {}
        for m, k, key, _is_str in bindings:
            bound.setdefault(key.lower(), (m, k))
            if key.lower() not in flushed:
                self.add(m, m.tok(k).line, "OS05", "high",
                         f"->instance('{key}') is not in config/octane.php flush; it survives when the binding "
                         "reaches the base container")
        for key, line in entries:
            if key.lower() not in bound:
                why = ("a framework or package manager; forgetting it drops drivers registered at boot"
                       if key.lower() in MANAGER_KEYS else "no ->instance() call in the scanned code binds it")
                self.add(fm, line, "OS05", "high", f"flush entry '{key}' is {why}")

    # OS06
    def rule_object_ids(self, m: Model) -> None:
        for k, t in enumerate(m.code):
            if not (t.kind == "name" and t.low.lstrip("\\") in ("spl_object_id", "spl_object_hash") and m.is_call(k)):
                continue
            ev = taint(m, k + 1, m.close(k + 1))
            if ev:
                self.add(m, t.line, "OS06", "blocker", f"{t.text}() of {ev[0]} used as identity; freed handles are reused")
                continue
            a = k - 1
            stored = m.is_op(a, *ASSIGN_OPS, "===", "!==", "==", "!=") and (
                m.tok(a - 2).kind == "name" or m.tok(a - 1).kind == "var" and m.tok(a - 1).low != "$this")
            stamp = any(m.tok(x).low in ("$this", "static", "self") for x in range(max(0, k - 5), k))
            after = m.close(k + 1) + 1
            cmp_after = m.is_op(after, "===", "!==", "==", "!=") and m.tok(after + 1).low in ("$this", "static", "self")
            if stamp or cmp_after or stored and stamp:
                self.add(m, t.line, "OS06", "high", f"{t.text}() stored or compared as a stamp; a new object can reuse the handle")
            else:
                self.add(m, t.line, "OS06", "medium", f"{t.text}() used; never treat it as identity across requests or jobs")

    # OS07
    def rule_globals(self, m: Model) -> None:
        code = m.code
        for k, t in enumerate(code):
            if t.kind == "var" and t.text == "$GLOBALS" and m.is_op(k + 1, "["):
                j = k + 1
                while m.is_op(j, "["):
                    j = m.close(j) + 1
                if m.is_op(j, *ASSIGN_OPS):
                    ev = taint(m, k, m.expr_end(j + 1, len(code)))
                    if ev:
                        self.add(m, t.line, "OS07", "blocker", f"$GLOBALS written with {ev[0]}")
                    elif not boot_context(m, k):
                        self.add(m, t.line, "OS07", "high", "$GLOBALS written at runtime; it survives into later requests and jobs")
            elif t.kind == "name" and m.is_call(k):
                low = t.low.lstrip("\\")
                if low not in GLOBAL_WRITERS and low != "define":
                    continue
                ev = taint(m, k + 1, m.close(k + 1))
                if ev:
                    self.add(m, t.line, "OS07", "blocker", f"{low}() with {ev[0]} changes the whole worker process")
                elif boot_context(m, k):
                    continue
                elif low == "define":
                    self.add(m, t.line, "OS07", "high", "define() at runtime: the first request's value stays for the worker")
                else:
                    self.add(m, t.line, "OS07", "high", f"{low}() in request or job code changes every later request on the worker")

    # OS08
    def rule_middleware(self, c: Cls) -> None:
        h = c.methods.get("handle")
        if h is None or not h.body:
            return
        m = c.model
        is_mw = "\\middleware\\" in c.fqn or any(p["var"] == "$next" for p in self.params(h))
        if not is_mw:
            return
        skip = m.nested_ranges(h.body[0], h.body[1])
        returns = [k for k in range(h.body[0], h.body[1]) if m.is_name(k, "return") and not m.in_ranges(k, skip)]
        forgets: dict[str, int] = {}
        for k in range(h.body[0], h.body[1]):
            if m.is_name(k, "forgetinstance") and m.is_op(k + 1, "("):
                args = m.args(k + 1)
                key = key_of(m, *args[0]) if args else None
                forgets.setdefault((key or "*").lower(), k)
        for k in range(h.body[0], h.body[1]):
            if not (m.is_name(k, "instance") and m.is_op(k + 1, "(") and container_receiver(m, k)):
                continue
            args = m.args(k + 1)
            key = key_of(m, *args[0]) if args else None
            if key is None:
                continue
            f = forgets.get(key.lower(), forgets.get("*"))
            early = [r for r in returns if r < k]
            if f is None or (early and f > early[0]):
                sev = "high" if early else "medium"
                self.add(m, m.tok(k).line, "OS08", sev,
                         f"{c.short}::handle() binds '{key}' without forgetInstance() first"
                         + ("; an earlier return leaves the previous request's value bound" if early else ""))

    # OS09
    def _is_job(self, c: Cls) -> bool:
        if any(i.endswith("shouldqueue") for a in self.ancestors(c) for i in a.implements):
            return True
        return "\\jobs\\" in c.fqn

    def rule_job(self, c: Cls) -> None:
        if c.kind != "class" or not self._is_job(c):
            return
        m = c.model
        for name, f in c.methods.items():
            if not f.body or name == "__construct":
                continue
            tries = self._try_blocks(m, f.body[0], f.body[1])
            for k in range(f.body[0], f.body[1]):
                t = m.code[k]
                kind = None
                if t.kind == "name" and t.low == "instance" and m.is_op(k + 1, "(") and container_receiver(m, k):
                    args = m.args(k + 1)
                    key = key_of(m, *args[0]) if args else None
                    kind = ("bind", key or "?")
                elif t.kind == "name" and t.low in ("login", "setuser", "loginusingid", "onceusingid") and \
                        m.is_op(k - 1, "->", "::") and m.is_op(k + 1, "(") and (
                        m.is_name(k - 2, "auth") or m.is_op(k - 2, ")")):
                    kind = ("auth", t.text)
                elif t.kind == "name" and t.low == "config" and m.is_call(k) and m.is_op(k + 2, "["):
                    kind = ("config", "config([...])")
                elif t.kind == "name" and t.low == "set" and m.is_op(k - 1, "::") and m.is_name(k - 2, "config"):
                    kind = ("config", "Config::set()")
                if kind is None:
                    continue
                if any(t0 < k < t1 and self._finally_resets(m, f0, f1, kind) for t0, t1, f0, f1 in tries):
                    continue
                sev = "blocker" if kind[0] == "bind" and tenant_like(kind[1]) else "high"
                what = {"bind": f"binds '{kind[1]}'", "auth": f"logs a user in with {kind[1]}()",
                        "config": f"writes {kind[1]}"}[kind[0]]
                self.add(m, t.line, "OS09", sev, f"{c.short}::{f.name}() {what} without a reset in finally; "
                         "queue workers keep it for the next job")

    def _try_blocks(self, m: Model, a: int, b: int) -> list[tuple[int, int, int, int]]:
        out = []
        for k in range(a, b):
            if m.is_name(k, "try") and m.is_op(k + 1, "{"):
                t1 = m.close(k + 1)
                j = t1 + 1
                while m.is_name(j, "catch") and m.is_op(j + 1, "("):
                    j = m.close(m.close(j + 1) + 1) + 1
                if m.is_name(j, "finally") and m.is_op(j + 1, "{"):
                    out.append((k + 1, t1, j + 1, m.close(j + 1)))
        return out

    def _finally_resets(self, m: Model, a: int, b: int, kind: tuple[str, str]) -> bool:
        for k in range(a, b):
            t = m.code[k]
            if kind[0] == "bind" and t.kind == "name" and t.low == "forgetinstance":
                args = m.args(k + 1) if m.is_op(k + 1, "(") else []
                key = key_of(m, *args[0]) if args else None
                if key is None or key.lower() == kind[1].lower():
                    return True
            if kind[0] == "auth" and t.kind == "name" and t.low in ("logout", "forgetuser", "forgetguards", "logoutcurrentdevice"):
                return True
            if kind[0] == "config" and t.kind == "name" and (t.low == "config" and m.is_op(k + 2, "[") or t.low == "set"):
                return True
        return False


class UsageError(Exception):
    pass


# --- output -------------------------------------------------------------------------------------------


def summarize(sc: Scanner, findings: list[Finding]) -> dict:
    active = [f for f in findings if not f.allowed]
    counts = {s: sum(1 for f in active if f.severity == s) for s in SEVERITIES}
    per_rule: dict[str, int] = {}
    for f in active:
        per_rule[f.rule] = per_rule.get(f.rule, 0) + 1
    return {"tool": TOOL, "tokenizer": sc.mode, "files": len(sc.models), "counts": counts, "per_rule": per_rule,
            "allowed": sum(1 for f in findings if f.allowed), "notes": sc.notes}


def scan(root: Path, includes: list[str], tokenizer: str) -> tuple[Scanner, list[Finding]]:
    if not root.is_dir():
        raise UsageError(f"not a directory: {root}")
    if not (root / "app").is_dir():
        raise UsageError(f"no app/ directory under {root}; pass the Laravel app root")
    sc = Scanner(root, includes, tokenizer)
    return sc, sc.run()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="octane_scan.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--include", action="append", default=[], help="extra directory to scan, e.g. packages")
    ap.add_argument("--tokenizer", choices=["auto", "php", "python"], default="auto")
    ap.add_argument("--json", action="store_true", help="print findings and summary as JSON")
    ap.add_argument("--min-severity", choices=SEVERITIES, default="low")
    ap.add_argument("--self-test", action="store_true", help="run offline checks against fixtures and exit")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 2
    if args.self_test:
        return self_test()
    try:
        sc, findings = scan(Path(args.root), args.include, args.tokenizer)
    except UsageError as e:
        print(f"octane_scan: {e}", file=sys.stderr)
        return 2
    limit = SEVERITIES.index(args.min_severity)
    shown = [f for f in findings if SEVERITIES.index(f.severity) <= limit]
    summary = summarize(sc, findings)
    if args.json:
        print(json.dumps({"summary": summary, "findings": [f.as_dict() for f in shown]}, indent=2))
    else:
        for f in shown:
            tag = " (allowed: " + f.allowed + ")" if f.allowed else ""
            print(f"{f.file}:{f.line}: {f.severity} {f.rule} {f.message}{tag}")
            print(f"    evidence: {f.evidence}")
            if f.note:
                print(f"    note: {f.note}")
            if not f.allowed:
                print(f"    fix: {f.fix}")
        c = summary["counts"]
        print(f"octane_scan: tokenizer={summary['tokenizer']} files={summary['files']} "
              f"blocker={c['blocker']} high={c['high']} medium={c['medium']} low={c['low']} "
              f"allowed={summary['allowed']}")
        for n in sc.notes:
            print(f"octane_scan: note: {n}")
    return 1 if any(f.severity in FAILING and not f.allowed for f in findings) else 0


# --- self-test ----------------------------------------------------------------------------------------

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "octane-scan"

# (file, line, rule, severity) that each fixture app must produce, and nothing else.
EXPECTED = {
    "leaky-app": {
        ("app/Support/PlanCache.php", 15, "OS01", "blocker"),
        ("app/Support/PlanCache.php", 22, "OS01", "high"),
        ("app/Support/PlanCache.php", 29, "OS02", "blocker"),
        ("app/Support/PlanCache.php", 37, "OS01", "medium"),
        ("app/Providers/AppServiceProvider.php", 17, "OS03", "blocker"),
        ("app/Providers/AppServiceProvider.php", 19, "OS03", "blocker"),
        ("app/Providers/AppServiceProvider.php", 21, "OS03", "medium"),
        ("app/Services/RequestLocale.php", 9, "OS03", "blocker"),
        ("app/Http/Controllers/InvoiceController.php", 15, "OS04", "high"),
        ("app/Http/Controllers/InvoiceController.php", 18, "OS04", "blocker"),
        ("app/Http/Controllers/ReportController.php", 10, "OS04", "high"),
        ("app/Http/Controllers/ReportController.php", 11, "OS04", "high"),
        ("app/Http/Middleware/BindWorkspace.php", 18, "OS05", "high"),
        ("app/Http/Middleware/BindWorkspace.php", 18, "OS08", "high"),
        ("config/octane.php", 7, "OS05", "high"),
        ("config/octane.php", 8, "OS05", "high"),
        ("app/Support/RequestStamp.php", 11, "OS06", "blocker"),
        ("app/Support/RequestStamp.php", 18, "OS06", "high"),
        ("app/Support/Runtime.php", 9, "OS07", "high"),
        ("app/Support/Runtime.php", 10, "OS07", "blocker"),
        ("app/Support/Runtime.php", 11, "OS07", "high"),
        ("app/Jobs/SyncWorkspace.php", 19, "OS09", "blocker"),
        ("app/Jobs/SyncWorkspace.php", 19, "OS05", "high"),
        ("app/Support/Allowed.php", 13, "OS01", "medium"),
        ("app/Support/Runtime.php", 12, "OS07", "high"),
        ("app/Support/Runtime.php", 13, "OS07", "high"),
        ("app/Support/Catalog.php", 11, "OS01", "low"),
        ("app/Http/Controllers/QuotaController.php", 9, "OS04", "medium"),
        ("app/Jobs/SendDigest.php", 18, "OS09", "high"),
        ("app/Jobs/SendDigest.php", 19, "OS09", "high"),
        ("app/Jobs/SendDigest.php", 22, "OS09", "blocker"),
        ("app/Providers/AppServiceProvider.php", 24, "OS03", "blocker"),
    },
    "clean-app": set(),
}
# Findings that an allow comment with a reason must suppress.
EXPECTED_ALLOWED = {("app/Support/Allowed.php", 10, "OS01")}


def _check_fixture(name: str, tokenizer: str, fails: list[str]) -> None:
    root = FIXTURES / name
    try:
        sc, findings = scan(root, [], tokenizer)
    except UsageError as e:
        fails.append(f"{name}/{tokenizer}: {e}")
        return
    got = {(f.file, f.line, f.rule, f.severity) for f in findings if not f.allowed}
    want = EXPECTED[name]
    for x in sorted(want - got):
        fails.append(f"{name}/{tokenizer}: missing {x}")
    for x in sorted(got - want):
        msg = next(f.message for f in findings if (f.file, f.line, f.rule, f.severity) == x)
        fails.append(f"{name}/{tokenizer}: unexpected {x}: {msg}")
    if name == "leaky-app":
        allowed = {(f.file, f.line, f.rule) for f in findings if f.allowed}
        if allowed != EXPECTED_ALLOWED:
            fails.append(f"{name}/{tokenizer}: allowed findings {sorted(allowed)}")
        noted = [f for f in findings if f.note and "reason" in f.note]
        if len(noted) != 1 or noted[0].line != 13:
            fails.append(f"{name}/{tokenizer}: an allow comment without a reason must be ignored and noted")


def self_test() -> int:
    fails: list[str] = []
    try:
        modes = ["python"] + (["php"] if php_binary() else [])
        for mode in modes:
            for name in EXPECTED:
                _check_fixture(name, mode, fails)

        # tokenizer: comments, strings and heredocs never produce code tokens
        src = ("<?php\n// static::$a = request();\n/* self::$b[] = 1; */\n$s = 'static::$c = 1';\n"
               "$h = <<<EOT\nstatic::$d = auth();\nEOT;\n$n = <<<'N'\nself::$e = 1;\nN;\n$q = \"x {$y} static::\\$f\";\n"
               "# Name::$g = 1;\n$ok = 1;\n")
        toks = [t for t in py_tokenize(src) if t.kind != "comment"]
        check_names = [t.text for t in toks if t.kind in ("var", "name")]
        if check_names != ["$s", "$h", "$n", "$q", "$ok"]:
            fails.append(f"tokenizer: code tokens leaked from comments or strings: {check_names}")
        last = [t for t in toks if t.text == "$ok"]
        if not last or last[0].line != 13:
            fails.append(f"tokenizer: line tracking off: {last and last[0].line}")
        php = php_binary()
        if php:
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "t.php"
                p.write_text(src, encoding="utf-8")
                ptoks = [t for t in php_tokenize_files(php[0], [p])[p] if t.kind != "comment"]
                a = [(t.kind, t.text, t.line) for t in toks]
                b = [(t.kind, t.text, t.line) for t in ptoks]
                if a != b:
                    fails.append(f"tokenizer: python and php token streams differ: {a} vs {b}")
            # both tokenizers agree on every fixture file
            for name in EXPECTED:
                files = sorted((FIXTURES / name).rglob("*.php"))
                ptok = php_tokenize_files(php[0], files)
                for f in files:
                    x = [(t.kind, t.text, t.line) for t in py_tokenize(f.read_text(encoding="utf-8"))]
                    y = [(t.kind, t.text, t.line) for t in ptok[f]]
                    if x != y:
                        diff = next((i for i, (u, v) in enumerate(zip(x, y)) if u != v), min(len(x), len(y)))
                        fails.append(f"tokenizer: {f.relative_to(FIXTURES)} differs at token {diff}: "
                                     f"{x[diff:diff + 1]} vs {y[diff:diff + 1]}")

        # exit codes
        devnull = open(os.devnull, "w")
        saved, saved_err = sys.stdout, sys.stderr
        try:
            sys.stdout = sys.stderr = devnull
            codes = (main([str(FIXTURES / "leaky-app"), "--tokenizer", "python"]),
                     main([str(FIXTURES / "clean-app"), "--tokenizer", "python"]),
                     main([str(FIXTURES / "no-such-app")]),
                     main([str(FIXTURES / "clean-app"), "--min-severity", "nope"]))
        finally:
            sys.stdout, sys.stderr = saved, saved_err
            devnull.close()
        if codes != (1, 0, 2, 2):
            fails.append(f"exit codes: leaky, clean, missing root, bad flag gave {codes}, want (1, 0, 2, 2)")
    except Exception as e:  # a crash is a failure, reported like one
        fails.append(f"unexpected {e.__class__.__name__}: {e}")

    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print(f"octane_scan.py self-test: ok (tokenizers: {', '.join(modes)}; fixtures: leaky-app, clean-app; "
          "rules OS01-OS09, allow comments, tokenizer agreement, exit codes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
