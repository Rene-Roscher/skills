#!/usr/bin/env python3
"""Install this repository's skills for agents that read SKILL.md folders (opencode and others).

Claude Code users install plugins with /plugin install instead. Other agents find skills in a
skills directory; this script links (or copies) each skill folder of the chosen plugins there.

Usage:
  install_skills.py --plugins core,saas [--target opencode|agents] [--project DIR | --dest DIR]
                    [--copy] [--dry-run] [--uninstall]
  install_skills.py --list
  install_skills.py --self-test

Targets (skills directories, per the agent's docs):
  opencode  global ~/.config/opencode/skills, with --project DIR: DIR/.opencode/skills
  agents    global ~/.agents/skills,          with --project DIR: DIR/.agents/skills
            (read by opencode and other agents that follow the .agents convention)
--dest DIR installs into DIR directly.

Links are absolute symlinks into this checkout, so a git pull updates the skills; --copy makes a
snapshot instead. An existing folder or file with the same name that this script did not create is
never replaced. --uninstall removes only links into this checkout (and copies marked by this script).

What does not carry over: plugin hooks (guardrails), plugin dependencies (docs-tools, laravel) and
the paths field (ignored, so those skills load by their description). Exit 0 on success, 1 when a
skill was skipped because of a conflict, 2 on a usage error.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARK = ".installed-from-rene-roscher-skills"
NOT_CARRIED = {
    "guardrails": "hooks only work in Claude Code; nothing to install",
    "docs-tools": "installs an MCP server through a Claude Code plugin dependency; configure Context7 in your agent",
}


def available(repo: Path = REPO) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for pdir in sorted((repo / "plugins").iterdir()):
        sd = pdir / "skills"
        skills = sorted(p for p in sd.iterdir() if (p / "SKILL.md").is_file()) if sd.is_dir() else []
        out[pdir.name] = skills
    return out


def target_dir(target: str, project: str | None, dest: str | None) -> Path:
    if dest:
        return Path(dest).expanduser().resolve()
    home = Path.home()
    if target == "opencode":
        return (Path(project).resolve() / ".opencode" / "skills") if project else home / ".config" / "opencode" / "skills"
    return (Path(project).resolve() / ".agents" / "skills") if project else home / ".agents" / "skills"


def ours(entry: Path, repo: Path) -> bool:
    if entry.is_symlink():
        try:
            return Path(os.readlink(entry)).resolve().is_relative_to(repo / "plugins")
        except (OSError, ValueError, AttributeError):
            t = str(Path(os.readlink(entry)).resolve())
            return t.startswith(str(repo / "plugins") + os.sep)
    return entry.is_dir() and (entry / MARK).is_file()


def install(skills: list[Path], dest: Path, repo: Path, copy: bool, dry: bool, log) -> int:
    conflicts = 0
    if not dry:
        dest.mkdir(parents=True, exist_ok=True)
    for src in skills:
        entry = dest / src.name
        if entry.exists() or entry.is_symlink():
            if not ours(entry, repo):
                log(f"skip {src.name}: {entry} exists and was not installed by this script")
                conflicts += 1
                continue
            if not dry:
                if entry.is_symlink() or entry.is_file():
                    entry.unlink()
                else:
                    shutil.rmtree(entry)
        log(f"{'copy' if copy else 'link'} {src.name} -> {entry}")
        if dry:
            continue
        if copy:
            shutil.copytree(src, entry, ignore=shutil.ignore_patterns("__pycache__"))
            (entry / MARK).write_text(str(src) + "\n", encoding="utf-8")
        else:
            entry.symlink_to(src, target_is_directory=True)
    return conflicts


def uninstall(dest: Path, repo: Path, dry: bool, log) -> int:
    if not dest.is_dir():
        log(f"nothing to remove: {dest} does not exist")
        return 0
    for entry in sorted(dest.iterdir()):
        if ours(entry, repo):
            log(f"remove {entry}")
            if not dry:
                if entry.is_symlink():
                    entry.unlink()
                else:
                    shutil.rmtree(entry)
    return 0


def main(argv: list[str], repo: Path = REPO, log=print) -> int:
    if "--self-test" in argv:
        return self_test()
    args = list(argv)

    def opt(name: str) -> str | None:
        if name in args:
            i = args.index(name)
            if i + 1 >= len(args) or args[i + 1].startswith("--"):
                raise SystemExit(f"{name} needs a value")
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return None

    def flag(name: str) -> bool:
        if name in args:
            args.remove(name)
            return True
        return False

    try:
        plugins_arg, target = opt("--plugins"), opt("--target") or "opencode"
        project, dest_arg = opt("--project"), opt("--dest")
    except SystemExit as e:
        print(e, file=sys.stderr)
        return 2
    copy, dry, remove, list_only = flag("--copy"), flag("--dry-run"), flag("--uninstall"), flag("--list")
    if args or target not in {"opencode", "agents"} or (project and dest_arg):
        print(__doc__.split("Targets")[0].strip(), file=sys.stderr)
        return 2

    avail = available(repo)
    if list_only:
        for name, skills in avail.items():
            note = NOT_CARRIED.get(name, ", ".join(s.name for s in skills))
            log(f"{name}: {note}")
        return 0

    dest = target_dir(target, project, dest_arg)
    if remove:
        return uninstall(dest, repo, dry, log)
    if not plugins_arg:
        print("--plugins is required, for example --plugins core,saas (see --list)", file=sys.stderr)
        return 2
    chosen = [p.strip() for p in plugins_arg.split(",") if p.strip()]
    unknown = [p for p in chosen if p not in avail]
    if unknown:
        print(f"unknown plugin(s): {', '.join(unknown)}; see --list", file=sys.stderr)
        return 2
    skills: list[Path] = []
    for p in chosen:
        if p in NOT_CARRIED:
            log(f"note {p}: {NOT_CARRIED[p]}")
        skills += avail[p]
    conflicts = install(skills, dest, repo, copy, dry, log)
    log(f"{len(skills) - conflicts} skill(s) {'would be ' if dry else ''}installed into {dest}, {conflicts} skipped")
    return 1 if conflicts else 0


def self_test() -> int:
    fails: list[str] = []

    def check(label, got, want):
        if got != want:
            fails.append(f"{label}: got {got!r}, want {want!r}")

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        repo = tmp / "repo"
        for plugin, names in {"core": ["alpha", "beta"], "saas": ["gamma"], "guardrails": []}.items():
            (repo / "plugins" / plugin).mkdir(parents=True)
            for n in names:
                d = repo / "plugins" / plugin / "skills" / n
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(f"---\nname: {n}\ndescription: x\n---\n", encoding="utf-8")
        dest = tmp / "dest"
        quiet = lambda *_: None  # noqa: E731

        check("usage without plugins", main(["--dest", str(dest)], repo, quiet), 2)
        check("unknown plugin", main(["--plugins", "nope", "--dest", str(dest)], repo, quiet), 2)
        check("dry run writes nothing", (main(["--plugins", "core", "--dest", str(dest), "--dry-run"], repo, quiet),
                                         dest.exists()), (0, False))
        check("install links", main(["--plugins", "core,saas", "--dest", str(dest)], repo, quiet), 0)
        check("links point into repo", sorted(p.name for p in dest.iterdir() if p.is_symlink()), ["alpha", "beta", "gamma"])
        check("skill readable through link", (dest / "alpha" / "SKILL.md").is_file(), True)
        check("reinstall is idempotent", main(["--plugins", "core,saas", "--dest", str(dest)], repo, quiet), 0)
        foreign = dest / "beta"
        foreign.unlink()
        foreign.mkdir()
        (foreign / "SKILL.md").write_text("mine", encoding="utf-8")
        check("foreign folder is a conflict", main(["--plugins", "core", "--dest", str(dest)], repo, quiet), 1)
        check("foreign folder untouched", (foreign / "SKILL.md").read_text(encoding="utf-8"), "mine")
        check("guardrails note, no skills", main(["--plugins", "guardrails", "--dest", str(dest)], repo, quiet), 0)
        check("uninstall", main(["--uninstall", "--dest", str(dest)], repo, quiet), 0)
        check("uninstall keeps foreign", sorted(p.name for p in dest.iterdir()), ["beta"])
        cdest = tmp / "copies"
        check("copy install", main(["--plugins", "saas", "--dest", str(cdest), "--copy"], repo, quiet), 0)
        check("copy is a real folder", (cdest / "gamma").is_dir() and not (cdest / "gamma").is_symlink(), True)
        check("copy uninstall", (main(["--uninstall", "--dest", str(cdest)], repo, quiet), (cdest / "gamma").exists()),
              (0, False))
        check("project target opencode", target_dir("opencode", str(tmp), None), tmp.resolve() / ".opencode" / "skills")
        check("project target agents", target_dir("agents", str(tmp), None), tmp.resolve() / ".agents" / "skills")

    if fails:
        for f in fails:
            print("FAIL", f)
        print(f"self-test: {len(fails)} failure(s)")
        return 1
    print("self-test: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
