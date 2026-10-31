#!/usr/bin/env python3
"""Check an MCP `tools/list` dump against the tool-design rules that a machine can decide.

Usage:
  check_tool_manifest.py TOOLS.json [--max-name 40] [--max-lead 300] [--tenant-params a,b,c]
  check_tool_manifest.py --self-test

TOOLS.json is the JSON-RPC result of `tools/list`, either {"tools": [...]} or the bare list.

Findings (exit 1):
  M01  name is not snake_case or is longer than the limit
  M02  no title
  M03  no description, or its first paragraph is longer than the limit
  M04  neither readOnlyHint nor destructiveHint is set explicitly
  M05  a schema has a tenant parameter (the connection binds the tenant)
  M06  catch-all tool: an `action` or `operation` enum parameter
  M07  a tool named like a write has readOnlyHint true, or one named like a read does not
  M08  a tool without inputSchema, or with additionalProperties not false
  M09  duplicate tool name
Warnings (printed, exit unaffected):
  W01  more than 6 top-level parameters; small models break on wide schemas
  W02  description does not say what the tool does not do or name a sibling (no "not" or "never")
  W03  a create_ tool without a matching update_ tool

Exit 0 when no finding, 1 with findings, 2 on a usage error. Python 3.8 or later, standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
READ_PREFIXES = ("find_", "list_", "get_", "whoami", "search_", "read_")
WRITE_PREFIXES = ("create_", "update_", "edit_", "post_", "publish_", "send_", "delete_", "cancel_",
                  "resolve_", "page_", "schedule_", "change_", "restore_", "confirm_")
DEFAULT_TENANT_PARAMS = ("organization_id", "tenant_id", "workspace_id", "account_id", "org_id", "team_id")
CATCH_ALL = ("action", "operation", "op", "mode")


def tools_of(data):
    if isinstance(data, dict):
        data = data.get("tools", data.get("result", {}).get("tools") if isinstance(data.get("result"), dict) else None)
    if not isinstance(data, list):
        raise ValueError("expected a list of tools or an object with a 'tools' list")
    return data


def check(tools, max_name=40, max_lead=300, tenant_params=DEFAULT_TENANT_PARAMS):
    findings, warnings, seen = [], [], set()
    names = [t.get("name", "") for t in tools if isinstance(t, dict)]
    for t in tools:
        name = t.get("name", "")
        where = name or "(unnamed)"
        if name in seen:
            findings.append(f"M09 {where}: duplicate tool name")
        seen.add(name)
        if not NAME_RE.match(name) or len(name) > max_name:
            findings.append(f"M01 {where}: name must be snake_case and at most {max_name} characters")
        if not str(t.get("title") or (t.get("annotations") or {}).get("title") or "").strip():
            findings.append(f"M02 {where}: no title")
        desc = str(t.get("description") or "").strip()
        if not desc:
            findings.append(f"M03 {where}: no description")
        else:
            lead = desc.split("\n\n", 1)[0]
            if len(lead) > max_lead:
                findings.append(f"M03 {where}: first paragraph has {len(lead)} characters (limit {max_lead})")
            if not re.search(r"\b(not|never|no)\b", desc, re.I):
                warnings.append(f"W02 {where}: description says nothing about what the tool does not do")
        ann = t.get("annotations") or {}
        if "readOnlyHint" not in ann and "destructiveHint" not in ann:
            findings.append(f"M04 {where}: set readOnlyHint or destructiveHint explicitly (the defaults are not safe)")
        read_like = name.startswith(READ_PREFIXES)
        write_like = name.startswith(WRITE_PREFIXES)
        if write_like and ann.get("readOnlyHint") is True and name != "confirm_action":
            findings.append(f"M07 {where}: named like a write but readOnlyHint is true")
        if read_like and "readOnlyHint" in ann and ann.get("readOnlyHint") is not True:
            findings.append(f"M07 {where}: named like a read but readOnlyHint is not true")
        schema = t.get("inputSchema")
        if not isinstance(schema, dict):
            findings.append(f"M08 {where}: no inputSchema")
            continue
        if schema.get("additionalProperties") is not False:
            findings.append(f"M08 {where}: inputSchema must set additionalProperties to false")
        props = schema.get("properties") or {}
        for p in props:
            if p in tenant_params:
                findings.append(f"M05 {where}.{p}: tenant parameter; the connection binds the tenant")
            spec = props[p] if isinstance(props[p], dict) else {}
            if p in CATCH_ALL and isinstance(spec.get("enum"), list):
                findings.append(f"M06 {where}.{p}: catch-all action parameter; split the tool by effect")
        if len(props) > 6:
            warnings.append(f"W01 {where}: {len(props)} parameters; keep schemas flat and narrow")
    for n in names:
        if n.startswith("create_"):
            obj = n[len("create_"):].split("_draft")[0]
            if not any(m.startswith(("update_" + obj, "edit_" + obj)) for m in names):
                warnings.append(f"W03 {n}: no update_ or edit_ tool for the same object")
    return findings, warnings


def self_test():
    ok = True
    good = [
        {"name": "find_bookings", "title": "Find bookings",
         "description": "Search bookings by customer or date. Never creates anything; use create_booking for that.",
         "annotations": {"readOnlyHint": True},
         "inputSchema": {"type": "object", "properties": {"customer": {"type": "string"}}, "additionalProperties": False}},
        {"name": "create_booking", "title": "Create booking",
         "description": "Create a NEW booking as a draft. Does not notify anyone.",
         "annotations": {"readOnlyHint": False, "destructiveHint": False},
         "inputSchema": {"type": "object", "properties": {"customer": {"type": "string"}}, "additionalProperties": False}},
        {"name": "update_booking", "title": "Update booking",
         "description": "Change fields of an existing booking. Does not notify anyone.",
         "annotations": {"readOnlyHint": False, "destructiveHint": False},
         "inputSchema": {"type": "object", "properties": {"version": {"type": "string"}}, "additionalProperties": False}},
    ]
    f, w = check(good)
    if f:
        print("self-test: clean manifest produced findings: " + "; ".join(f))
        ok = False
    cases = {
        "M01": {"name": "CreateBooking"},
        "M02": {"name": "find_x", "title": ""},
        "M03": {"name": "find_y", "title": "Y", "description": "x" * 400},
        "M04": {"name": "find_z", "title": "Z", "description": "No side effects.", "annotations": {}},
        "M05": {"name": "find_a", "title": "A", "description": "Never writes.", "annotations": {"readOnlyHint": True},
                "inputSchema": {"type": "object", "properties": {"organization_id": {"type": "string"}}, "additionalProperties": False}},
        "M06": {"name": "manage_b", "title": "B", "description": "Not for reads.", "annotations": {"destructiveHint": True},
                "inputSchema": {"type": "object", "properties": {"action": {"enum": ["a", "b"]}}, "additionalProperties": False}},
        "M07": {"name": "delete_c", "title": "C", "description": "Never undoes.", "annotations": {"readOnlyHint": True},
                "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
        "M08": {"name": "find_d", "title": "D", "description": "Never writes.", "annotations": {"readOnlyHint": True},
                "inputSchema": {"type": "object", "properties": {}}},
    }
    for code, tool in cases.items():
        f, _ = check([tool])
        if not any(x.startswith(code) for x in f):
            print(f"self-test: {code} not detected")
            ok = False
    f, _ = check([good[0], dict(good[0])])
    if not any(x.startswith("M09") for x in f):
        print("self-test: M09 not detected")
        ok = False
    _, w = check([good[1]])
    if not any(x.startswith("W03") for x in w):
        print("self-test: W03 not detected")
        ok = False
    print("self-test: " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest", nargs="?")
    ap.add_argument("--max-name", type=int, default=40)
    ap.add_argument("--max-lead", type=int, default=300)
    ap.add_argument("--tenant-params", default=",".join(DEFAULT_TENANT_PARAMS))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.manifest:
        ap.print_usage(sys.stderr)
        return 2
    try:
        with open(args.manifest, encoding="utf-8") as fh:
            tools = tools_of(json.load(fh))
    except (OSError, ValueError) as exc:
        print(f"cannot read manifest: {exc}", file=sys.stderr)
        return 2
    findings, warnings = check(tools, args.max_name, args.max_lead, tuple(x for x in args.tenant_params.split(",") if x))
    for line in warnings + findings:
        print(line)
    print(f"{len(tools)} tool(s), {len(findings)} finding(s), {len(warnings)} warning(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
