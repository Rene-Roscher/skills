#!/usr/bin/env python3
"""Static high-availability checks over a repository directory. A heuristic starting point, not an audit.

Usage:
  ha_check.py DIR [--json]
  ha_check.py --self-test

What it reads: PHP mail config (Laravel config/mail.php pattern), Symfony MAILER_DSN lines in env files,
Kubernetes manifests (*.yaml, *.yml), octoDNS config files, CloudNativePG Cluster and ScheduledBackup objects.
Files with Helm or Go template syntax are skipped and counted; render them first (helm template) and scan the output.

Findings (exit 1):
  HA-M01  failover or roundrobin mailer has a 'log', 'array' or 'null' member (alarm mail counts as sent and is lost)
  HA-M02  Symfony failover/roundrobin DSN has a null:// member
  HA-M03  failover mailer has fewer than two distinct members
  HA-K01  workload with replicas above 1 has no matching PodDisruptionBudget
  HA-K02  workload with replicas above 1 has neither topologySpreadConstraints nor podAntiAffinity
  HA-K03  Deployment or StatefulSet container without readinessProbe
  HA-K04  workload labelled critical runs one replica (replicas unset counts as 1 unless an HPA has minReplicas of 2 or more)
  HA-K05  PodDisruptionBudget allows no voluntary eviction (maxUnavailable 0, minAvailable 100 percent)
  HA-D01  octoDNS zone publishes to fewer than two targets
  HA-C01  CloudNativePG Cluster with one instance (instances unset defaults to 1)
  HA-C02  CloudNativePG Cluster without WAL archiving or backup configuration
  HA-C03  CloudNativePG Cluster without a ScheduledBackup that names it
  HA-C04  CloudNativePG Cluster with enablePDB set to false
Warnings (printed, exit unaffected):
  HA-W01  CloudNativePG Cluster still uses the deprecated in-tree barmanObjectStore

Exit 0 when clean, 1 with findings, 2 on a usage error. Python 3.8 or later, standard library only.
PyYAML is used when installed; otherwise a small built-in parser for block-style YAML is used.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

SKIP_DIRS = {".git", "node_modules", "vendor", "__pycache__", ".terraform", ".venv"}
WORKLOADS = {"Deployment", "StatefulSet"}
BAD_MAIL = {"log", "array", "null"}


# ---------------------------------------------------------------- YAML subset parser

def _strip_comment(line):
    out, quote = [], None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def _scalar(text):
    t = text.strip()
    if t == "" or t in ("~", "null"):
        return None
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":
        return t[1:-1]
    if t in ("true", "True"):
        return True
    if t in ("false", "False"):
        return False
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        return [_scalar(p) for p in inner.split(",")] if inner else []
    if t == "{}":
        return {}
    return t


def _split_key(text):
    m = re.match(r"""^("[^"]*"|'[^']*'|[^\s:'"][^:]*?)\s*:(?:\s+(.*)|$)""", text)
    if not m:
        return None
    key = m.group(1)
    if len(key) >= 2 and key[0] in "'\"" and key[-1] == key[0]:
        key = key[1:-1]
    return key, (m.group(2) or "")


def mini_load_all(text):
    docs, cur = [], []
    for raw in text.splitlines():
        if raw.startswith("---"):
            docs.append(cur)
            cur = []
        elif raw.startswith("..."):
            continue
        else:
            cur.append(raw)
    docs.append(cur)
    result = []
    for lines in docs:
        prepared = []
        for raw in lines:
            s = _strip_comment(raw.replace("\t", "  "))
            if s.strip():
                prepared.append((len(s) - len(s.lstrip(" ")), s.strip()))
        if prepared:
            val, _ = _parse_block(prepared, 0, prepared[0][0])
            result.append(val)
    return result


def _skip_block_scalar(items, i, indent):
    while i < len(items) and items[i][0] > indent:
        i += 1
    return i


def _parse_block(items, i, indent):
    if i >= len(items):
        return None, i
    if items[i][1].startswith("- ") or items[i][1] == "-":
        return _parse_seq(items, i, items[i][0])
    return _parse_map(items, i, items[i][0])


def _parse_value(items, i, indent, rest):
    """Value after 'key:' with remaining text rest; items[i] is the line after the key line."""
    if rest in ("|", ">", "|-", ">-", "|+", ">+"):
        return "", _skip_block_scalar(items, i, indent)
    if rest != "":
        return _scalar(rest), i
    if i < len(items):
        ni, ntext = items[i]
        if ni > indent:
            return _parse_block(items, i, ni)
        if ni == indent and (ntext.startswith("- ") or ntext == "-"):
            return _parse_seq(items, i, ni)
    return None, i


def _parse_map(items, i, indent):
    out = {}
    while i < len(items) and items[i][0] == indent and not (items[i][1].startswith("- ") or items[i][1] == "-"):
        kv = _split_key(items[i][1])
        if kv is None:
            i += 1
            continue
        key, rest = kv
        i += 1
        out[key], i = _parse_value(items, i, indent, rest)
    return out, i


def _parse_seq(items, i, indent):
    out = []
    while i < len(items) and items[i][0] == indent and (items[i][1].startswith("- ") or items[i][1] == "-"):
        body = items[i][1][1:].strip()
        if body == "":
            i += 1
            if i < len(items) and items[i][0] > indent:
                val, i = _parse_block(items, i, items[i][0])
            else:
                val = None
            out.append(val)
            continue
        kv = _split_key(body) if not body.startswith(("[", "{", "'", '"')) else None
        if kv is None:
            out.append(_scalar(body))
            i += 1
            continue
        # inline mapping item: rewrite the dash line as a mapping line at indent + 2
        inner = indent + 2
        items[i] = (inner, body)
        val, i = _parse_map(items, i, inner)
        out.append(val)
    return out, i


def load_all(text, force_mini=False):
    if not force_mini:
        try:
            import yaml  # type: ignore
            return [d for d in yaml.safe_load_all(text)]
        except ImportError:
            pass
        except Exception:
            return []
    try:
        return mini_load_all(text)
    except Exception:
        return []


# ---------------------------------------------------------------- helpers

def g(obj, *path, default=None):
    cur = obj
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur


def walk_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in sorted(filenames):
            yield os.path.join(dirpath, f)


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def is_critical(labels, annotations):
    for src in (labels or {}, annotations or {}):
        for k, v in src.items():
            val = str(v).lower()
            if "critical" in str(k).lower() and val not in ("false", "no", "0", "none"):
                return True
            if val == "critical":
                return True
    return False


# ---------------------------------------------------------------- mail checks

def match_bracket(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def check_php_mail(path, text, findings):
    blocks = []
    for m in re.finditer(r"""['"](\w+)['"]\s*=>\s*\[""", text):
        end = match_bracket(text, m.end() - 1)
        body = text[m.end():end]
        t = re.search(r"""['"]transport['"]\s*=>\s*['"](\w+)['"]""", body)
        if t:
            blocks.append((m.group(1), t.group(1), body, text.count("\n", 0, m.start()) + 1))
    transport_of = {name: tr for name, tr, _, _ in blocks}
    for name, tr, body, line in blocks:
        if tr not in ("failover", "roundrobin"):
            continue
        lm = re.search(r"""['"]mailers['"]\s*=>\s*\[(.*?)\]""", body, re.S)
        members = re.findall(r"""['"](\w+)['"]""", lm.group(1)) if lm else []
        for mem in members:
            if mem in BAD_MAIL or transport_of.get(mem) in BAD_MAIL:
                findings.append(("HA-M01", path, line,
                                 "%s mailer '%s' has member '%s' that discards or logs mail" % (tr, name, mem)))
        if tr == "failover" and len(set(members)) < 2:
            findings.append(("HA-M03", path, line, "failover mailer '%s' has fewer than two distinct members" % name))


def check_dsn(path, text, findings):
    for n, line in enumerate(text.splitlines(), 1):
        m = re.search(r"(?:failover|roundrobin)\(([^)]*)\)", line)
        if m and re.search(r"(^|\s)null://", m.group(1)):
            findings.append(("HA-M02", path, n, "failover or roundrobin DSN contains a null:// member"))


# ---------------------------------------------------------------- object collection

def collect(root, force_mini=False):
    objs, skipped, files = [], 0, []
    for p in walk_files(root):
        low = p.lower()
        if low.endswith((".yaml", ".yml")):
            files.append(p)
        elif low.endswith(".php") and os.sep + "config" + os.sep in p and os.path.basename(p) == "mail.php":
            files.append(p)
        elif os.path.basename(p).startswith(".env"):
            files.append(p)
    return files


def run(root, force_mini=False):
    findings, warnings = [], []
    docs = []  # (path, obj)
    skipped = 0
    for p in collect(root):
        text = read(p)
        base = os.path.basename(p)
        if base == "mail.php":
            check_php_mail(p, text, findings)
            continue
        if base.startswith(".env"):
            check_dsn(p, text, findings)
            continue
        if "{{" in text:
            skipped += 1
            continue
        for obj in load_all(text, force_mini):
            if isinstance(obj, dict):
                docs.append((p, obj))
    check_k8s(docs, findings)
    check_octodns(docs, findings)
    check_cnpg(docs, findings, warnings)
    return findings, warnings, skipped


# ---------------------------------------------------------------- kubernetes

def pod_template(obj):
    return g(obj, "spec", "template", default={}) or {}


def effective_replicas(obj, hpas):
    r = g(obj, "spec", "replicas")
    name = g(obj, "metadata", "name")
    for h in hpas:
        if g(h, "spec", "scaleTargetRef", "name") == name and (g(h, "spec", "minReplicas") or 1) >= 2:
            return max(2, int(g(h, "spec", "minReplicas")))
    return 1 if r is None else r


def check_k8s(docs, findings):
    pdbs = [(p, o) for p, o in docs if o.get("kind") == "PodDisruptionBudget"]
    hpas = [o for _, o in docs if o.get("kind") == "HorizontalPodAutoscaler"]
    for p, o in pdbs:
        if str(g(o, "spec", "maxUnavailable")) in ("0", "0%") or str(g(o, "spec", "minAvailable")) == "100%":
            findings.append(("HA-K05", p, 0, "PodDisruptionBudget '%s' allows no voluntary eviction; node drains will hang"
                             % g(o, "metadata", "name")))
    for p, o in docs:
        if o.get("kind") not in WORKLOADS:
            continue
        name = g(o, "metadata", "name", default="?")
        replicas = effective_replicas(o, hpas)
        tpl = pod_template(o)
        spec = g(tpl, "spec", default={}) or {}
        pod_labels = g(tpl, "metadata", "labels", default={}) or {}
        labels = dict(g(o, "metadata", "labels", default={}) or {})
        labels.update(pod_labels)
        where = "%s/%s" % (o.get("kind"), name)
        if isinstance(replicas, int) and replicas > 1:
            matched = False
            for pp, pdb in pdbs:
                sel = g(pdb, "spec", "selector", "matchLabels", default=None)
                if isinstance(sel, dict) and sel and pod_labels:
                    matched = matched or all(pod_labels.get(k) == v for k, v in sel.items())
                elif os.path.dirname(pp) == os.path.dirname(p):
                    matched = True
            if not matched:
                findings.append(("HA-K01", p, 0, "%s has %s replicas and no matching PodDisruptionBudget" % (where, replicas)))
            if not spec.get("topologySpreadConstraints") and not g(spec, "affinity", "podAntiAffinity"):
                findings.append(("HA-K02", p, 0, "%s has %s replicas and no topologySpreadConstraints or podAntiAffinity"
                                 % (where, replicas)))
        containers = spec.get("containers") or []
        if containers and not any(isinstance(c, dict) and c.get("readinessProbe") for c in containers):
            findings.append(("HA-K03", p, 0, "%s has no readinessProbe" % where))
        if replicas == 1 and is_critical(labels, g(o, "metadata", "annotations")):
            findings.append(("HA-K04", p, 0, "%s is labelled critical and runs one replica" % where))


# ---------------------------------------------------------------- octodns

def check_octodns(docs, findings):
    for p, o in docs:
        if "providers" not in o or "zones" not in o or "kind" in o:
            continue
        zones = o.get("zones")
        if not isinstance(zones, dict):
            continue
        for zname, z in zones.items():
            if not isinstance(z, dict):
                continue
            targets = z.get("targets") or []
            if isinstance(targets, str):
                targets = [targets]
            if len(set(map(str, targets))) < 2:
                findings.append(("HA-D01", p, 0, "octoDNS zone '%s' publishes to %d target(s); use two independent providers"
                                 % (zname, len(set(map(str, targets))))))


# ---------------------------------------------------------------- cloudnativepg

def check_cnpg(docs, findings, warnings):
    sched = {g(o, "spec", "cluster", "name") for _, o in docs if o.get("kind") == "ScheduledBackup"}
    for p, o in docs:
        if o.get("kind") != "Cluster" or not str(o.get("apiVersion", "")).startswith("postgresql.cnpg.io/"):
            continue
        name = g(o, "metadata", "name", default="?")
        spec = o.get("spec") or {}
        inst = spec.get("instances", 1)
        if inst == 1:
            findings.append(("HA-C01", p, 0, "Cluster '%s' runs one instance; a node loss is an outage" % name))
        plugins = spec.get("plugins") or []
        wal_plugin = any(isinstance(x, dict) and x.get("isWALArchiver") for x in plugins)
        backup = spec.get("backup") or {}
        in_tree = bool(backup.get("barmanObjectStore")) if isinstance(backup, dict) else False
        snap = bool(backup.get("volumeSnapshot")) if isinstance(backup, dict) else False
        if not (wal_plugin or in_tree or snap):
            findings.append(("HA-C02", p, 0, "Cluster '%s' has no WAL archiving or backup configuration" % name))
        if name not in sched:
            findings.append(("HA-C03", p, 0, "Cluster '%s' has no ScheduledBackup that names it" % name))
        if spec.get("enablePDB") is False:
            findings.append(("HA-C04", p, 0, "Cluster '%s' sets enablePDB to false" % name))
        if in_tree:
            warnings.append(("HA-W01", p, 0, "Cluster '%s' uses the deprecated in-tree barmanObjectStore; plan the move to the Barman Cloud plugin" % name))


# ---------------------------------------------------------------- self-test

BAD_MAIL_PHP = """<?php
return [
    'default' => env('MAIL_MAILER', 'failover'),
    'mailers' => [
        'smtp' => ['transport' => 'smtp', 'host' => 'smtp.example.com'],
        'backup' => ['transport' => 'smtp', 'host' => 'smtp.example.net'],
        'log' => ['transport' => 'log', 'channel' => env('MAIL_LOG_CHANNEL')],
        'failover' => [
            'transport' => 'failover',
            'mailers' => ['smtp', 'backup', 'log'],
        ],
    ],
];
"""
GOOD_MAIL_PHP = BAD_MAIL_PHP.replace("['smtp', 'backup', 'log']", "['smtp', 'backup']")

BAD_K8S = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: registry.example.com/api:1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: billing
  labels:
    app: billing
    criticality: critical
spec:
  replicas: 1
  selector:
    matchLabels:
      app: billing
  template:
    metadata:
      labels:
        app: billing
    spec:
      containers:
        - name: billing
          image: registry.example.com/billing:1
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web
spec:
  maxUnavailable: 0
  selector:
    matchLabels:
      app: web
"""
GOOD_K8S = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: api
      containers:
        - name: api
          image: registry.example.com/api:1
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: api
"""

BAD_DNS = """providers:
  config:
    class: octodns.provider.yaml.YamlProvider
    directory: ./config
  ns1:
    class: octodns_ns1.Ns1Provider
zones:
  example.com.:
    sources:
      - config
    targets:
      - ns1
"""
GOOD_DNS = BAD_DNS.replace("      - ns1\n", "      - ns1\n      - route53\n")

BAD_PG = """apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: app-db
spec:
  instances: 1
  storage:
    size: 10Gi
"""
GOOD_PG = """apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: app-db
spec:
  instances: 3
  storage:
    size: 10Gi
  plugins:
    - name: barman-cloud.cloudnative-pg.io
      isWALArchiver: true
      parameters:
        barmanObjectName: offsite
---
apiVersion: postgresql.cnpg.io/v1
kind: ScheduledBackup
metadata:
  name: app-db-daily
spec:
  schedule: "0 0 2 * * *"
  method: plugin
  cluster:
    name: app-db
"""


def _write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def self_test():
    failures = []

    def expect(label, root, want_ids, force_mini):
        findings, _, _ = run(root, force_mini)
        got = {f[0] for f in findings}
        if got != want_ids:
            failures.append("%s (mini=%s): expected %s, got %s" % (label, force_mini, sorted(want_ids), sorted(got)))

    modes = [True]
    try:
        import yaml  # noqa: F401
        modes.append(False)
    except ImportError:
        pass
    for mini in modes:
        with tempfile.TemporaryDirectory() as bad, tempfile.TemporaryDirectory() as good:
            _write(bad, "laravel/config/mail.php", BAD_MAIL_PHP)
            _write(bad, "k8s/app.yaml", BAD_K8S)
            _write(bad, "dns/octodns.yaml", BAD_DNS)
            _write(bad, "db/cluster.yaml", BAD_PG)
            _write(bad, "app/.env.example", "MAILER_DSN=failover(smtp://a@default null://null)\n")
            _write(good, "laravel/config/mail.php", GOOD_MAIL_PHP)
            _write(good, "k8s/app.yaml", GOOD_K8S)
            _write(good, "dns/octodns.yaml", GOOD_DNS)
            _write(good, "db/cluster.yaml", GOOD_PG)
            _write(good, "chart/templates/x.yaml", "name: {{ .Values.x }}\n")
            expect("bad", bad, {"HA-M01", "HA-M02", "HA-K01", "HA-K02", "HA-K03", "HA-K04", "HA-K05",
                                "HA-D01", "HA-C01", "HA-C02", "HA-C03"}, mini)
            expect("good", good, set(), mini)
    # individual cases
    with tempfile.TemporaryDirectory() as d:
        _write(d, "c.yaml", BAD_PG.replace("instances: 1", "instances: 3"))
        expect("cnpg three instances still lacks backup", d, {"HA-C02", "HA-C03"}, True)
    with tempfile.TemporaryDirectory() as d:
        _write(d, "w.yaml", GOOD_K8S.replace("replicas: 3", "replicas: 1"))
        findings, _, _ = run(d, True)
        if findings:
            failures.append("single replica unlabelled workload must be clean, got %s" % findings)
    with tempfile.TemporaryDirectory() as d:
        _write(d, "p.yaml", GOOD_PG.replace("isWALArchiver: true", "isWALArchiver: false")
               .replace("plugins:", "plugins:"))
        findings, _, _ = run(d, True)
        if {f[0] for f in findings} != {"HA-C02"}:
            failures.append("cluster with non-archiving plugin must give HA-C02 only, got %s" % findings)
    with tempfile.TemporaryDirectory() as d:
        _write(d, "c.yaml", GOOD_PG.replace("plugins:\n    - name: barman-cloud.cloudnative-pg.io\n      isWALArchiver: true\n"
                                            "      parameters:\n        barmanObjectName: offsite\n",
                                            "backup:\n    barmanObjectStore:\n      destinationPath: s3://b/\n"))
        findings, warnings, _ = run(d, True)
        if findings or [w[0] for w in warnings] != ["HA-W01"]:
            failures.append("in-tree barmanObjectStore must give only HA-W01, got %s / %s" % (findings, warnings))
    with tempfile.TemporaryDirectory() as d:
        _write(d, "config/mail.php", "<?php return ['mailers' => ['a' => ['transport' => 'smtp'], "
                                     "'f' => ['transport' => 'failover', 'mailers' => ['a']]]];")
        findings, _, _ = run(d, True)
        if {f[0] for f in findings} != {"HA-M03"}:
            failures.append("single-member failover must give HA-M03, got %s" % findings)
    if failures:
        for f in failures:
            print("SELF-TEST FAIL: " + f, file=sys.stderr)
        return 1
    print("self-test passed (%d parser mode(s))" % len(modes))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Static high-availability checks (heuristic).")
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if args.self_test:
        return self_test()
    if not args.dir or not os.path.isdir(args.dir):
        print("usage: ha_check.py DIR [--json] | --self-test", file=sys.stderr)
        return 2
    findings, warnings, skipped = run(args.dir)
    if args.json:
        print(json.dumps({"findings": [dict(id=i, path=p, line=l, message=m) for i, p, l, m in findings],
                          "warnings": [dict(id=i, path=p, line=l, message=m) for i, p, l, m in warnings],
                          "skipped_templates": skipped}, indent=2))
    else:
        for i, p, l, m in findings:
            print("%s %s%s: %s" % (i, os.path.relpath(p, args.dir), (":%d" % l) if l else "", m))
        for i, p, l, m in warnings:
            print("warning %s %s: %s" % (i, os.path.relpath(p, args.dir), m))
        if skipped:
            print("note: skipped %d templated file(s); render Helm charts first and scan the output" % skipped)
        if not findings:
            print("no findings (heuristic: absence of findings is not proof of availability)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
