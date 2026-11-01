#!/usr/bin/env python3
"""Compute unit economics per plan from a model file whose every input carries a source.

Usage:
  unit_economics.py MODEL.json
  unit_economics.py --self-test

Every input is an object {"value": number or null, "source": "...", "assumption": true|false}.
"source" names the measurement query, invoice or vendor page with its date. "assumption": true marks a
number that is not measured yet; results that depend on it are marked with "*".
The file layout is described in references/model-structure.md.

Findings (code, what fails; exit 1):
  E01  an input has no source
  E02  a cost driver of a plan has no ceiling (the plan limit, or a measured high percentile)
  E03  a plan loses money for a tenant at every ceiling (max-out margin below zero)
  E04  a required field is missing or not a number
Warnings (printed, exit unaffected):
  W01  typical gross margin below the target
  W02  lifetime not measurable: no churned customers in the period

All amounts are net, in one currency, per month. Exit 0 when no finding, 1 with findings, 2 on a usage
error. Python 3.8 or later, standard library only, no network.
"""

from __future__ import annotations

import argparse
import json
import sys


class Model:
    def __init__(self, data):
        self.data = data
        self.findings = []
        self.warnings = []
        self.assumed = False

    def num(self, obj, where, required=True):
        """Read a sourced input. Returns (value or None, is_assumption)."""
        if not isinstance(obj, dict) or "value" not in obj:
            if required:
                self.findings.append(f"E04 {where}: missing input object with 'value'")
            return None, False
        if not str(obj.get("source", "")).strip():
            self.findings.append(f"E01 {where}: input has no source")
        v = obj["value"]
        if v is not None and not isinstance(v, (int, float)):
            self.findings.append(f"E04 {where}: value is not a number")
            return None, False
        return v, bool(obj.get("assumption"))


def mark(value, assumed, pct=False):
    if value is None:
        return "n/a"
    text = f"{value * 100:.1f} %" if pct else f"{value:,.2f}"
    return text + ("*" if assumed else "")


def run(data):
    m = Model(data)
    target, t_a = m.num(data.get("target_gross_margin"), "target_gross_margin")
    unit = {}
    for name, obj in (data.get("unit_costs") or {}).items():
        unit[name] = m.num(obj, f"unit_costs.{name}")
    fee = data.get("payment_fee") or {}
    fee_pct, fp_a = m.num(fee.get("percent"), "payment_fee.percent")
    fee_fix, ff_a = m.num(fee.get("fixed"), "payment_fee.fixed")
    vat, v_a = m.num(fee.get("vat_rate_on_charge"), "payment_fee.vat_rate_on_charge")
    fixed_total, fixed_a = 0.0, False
    for i, obj in enumerate(data.get("fixed_costs") or []):
        v, a = m.num(obj, f"fixed_costs[{i}] {obj.get('name', '') if isinstance(obj, dict) else ''}")
        fixed_total += v or 0.0
        fixed_a |= a

    rows, contrib_sum, paying, any_a = [], 0.0, 0.0, fixed_a
    free_cost = None
    for plan in data.get("plans") or []:
        name = plan.get("name", "?")
        price, p_a = m.num(plan.get("price_monthly_net"), f"{name}.price_monthly_net")
        base, b_a = m.num(plan.get("base_cost"), f"{name}.base_cost")
        customers, c_a = m.num(plan.get("customers"), f"{name}.customers")
        assumed = p_a or b_a
        typical = base or 0.0
        maxout = base or 0.0
        unbounded = False
        for driver, use in (plan.get("usage") or {}).items():
            cost, u_a = unit.get(driver, (None, False))
            if driver not in unit:
                m.findings.append(f"E04 {name}.usage.{driver}: no unit cost for this driver")
                continue
            typ, ty_a = m.num(use.get("typical"), f"{name}.usage.{driver}.typical")
            ceil, ce_a = m.num(use.get("ceiling"), f"{name}.usage.{driver}.ceiling")
            if ceil is None:
                unbounded = True
                m.findings.append(f"E02 {name}.usage.{driver}: no ceiling; set a plan limit or a measured high percentile")
            typical += (typ or 0.0) * (cost or 0.0)
            maxout += (ceil or 0.0) * (cost or 0.0)
            assumed |= u_a or ty_a or ce_a
        fee_m = 0.0
        if price:
            fee_m = (fee_pct or 0.0) * price * (1 + (vat or 0.0)) + (fee_fix or 0.0)
            assumed |= fp_a or ff_a or v_a
        annual, an_a = m.num(plan.get("price_annual_net"), f"{name}.price_annual_net", required=False)
        fee_annual_m = None
        if annual:
            fee_annual_m = ((fee_pct or 0.0) * annual * (1 + (vat or 0.0)) + (fee_fix or 0.0)) / 12
        if not price:
            free_cost = (customers or 0.0) * typical
            any_a |= assumed or c_a
            rows.append((name, price, typical, None, maxout, None, fee_m, fee_annual_m, assumed))
            continue
        gm = (price - typical - fee_m) / price
        mo = None if unbounded else (price - maxout - fee_m) / price
        if unbounded:
            maxout = None
        elif mo < 0:
            m.findings.append(f"E03 {name}: a tenant at every ceiling costs {maxout + fee_m:,.2f} against a price of {price:,.2f}")
        if target is not None and gm < target:
            m.warnings.append(f"W01 {name}: typical gross margin {gm * 100:.1f} % is below the target {target * 100:.1f} %")
        contrib_sum += (price - typical - fee_m) * (customers or 0.0)
        paying += customers or 0.0
        any_a |= assumed or c_a
        rows.append((name, price, typical, gm, maxout, mo, fee_m, fee_annual_m, assumed))

    print("plan | price | typical cost | typical margin | max-out cost | max-out margin | fee/month (monthly) | fee/month (annual)")
    for name, price, typ, gm, mx, mo, fm, fa, a in rows:
        print(" | ".join([name, mark(price, a), mark(typ, a), mark(gm, a, True), mark(mx, a), mark(mo, a, True),
                          mark(fm, a), mark(fa, a)]))
    avg = contrib_sum / paying if paying else None
    print(f"fixed costs per month: {mark(fixed_total, fixed_a)}")
    print(f"contribution per paying customer: {mark(avg, any_a)}")
    if avg and avg > 0:
        print(f"break-even paying customers (fixed costs only): {mark(fixed_total / avg, any_a)}")
        if free_cost is not None:
            print(f"break-even paying customers (fixed costs plus free tier): {mark((fixed_total + free_cost) / avg, any_a)}")
    free = data.get("free") or {}
    if free_cost is not None and free:
        conv, cv_a = m.num(free.get("conversions_per_month"), "free.conversions_per_month")
        print(f"free tier cost per month: {mark(free_cost, any_a)}")
        if conv:
            print(f"free tier cost per conversion: {mark(free_cost / conv, any_a or cv_a)}")
    churn = data.get("churn")
    if churn:
        lost, l_a = m.num(churn.get("churned_customers"), "churn.churned_customers")
        start, s_a = m.num(churn.get("customers_at_start"), "churn.customers_at_start")
        if not lost:
            m.warnings.append("W02 lifetime not measurable: no churned customers in the period")
        elif start and avg:
            rate = lost / start
            print(f"monthly churn: {mark(rate, l_a or s_a, True)} from {int(lost)} churned customers")
            print(f"lifetime contribution per customer (undiscounted): {mark(avg / rate, any_a or l_a or s_a)}")
    for w in m.warnings:
        print(w)
    for f in m.findings:
        print(f)
    if any_a:
        print("* depends on an input marked as assumption")
    return m


def src(v, assumption=False):
    return {"value": v, "source": "self-test fixture", "assumption": assumption}


FIXTURE = {
    "target_gross_margin": src(0.75),
    "unit_costs": {"sms_segment": src(0.10), "storage_gb": src(0.02), "support_hour": src(40)},
    "payment_fee": {"percent": src(0.02), "fixed": src(0.25), "vat_rate_on_charge": src(0.0)},
    "fixed_costs": [{"name": "base infrastructure", **src(500)}],
    "plans": [
        {"name": "free", "price_monthly_net": src(0), "base_cost": src(0.5), "customers": src(200),
         "usage": {"storage_gb": {"typical": src(1), "ceiling": src(5)}}},
        {"name": "team", "price_monthly_net": src(50), "price_annual_net": src(500), "base_cost": src(2),
         "customers": src(20),
         "usage": {"sms_segment": {"typical": src(50), "ceiling": src(200)},
                   "support_hour": {"typical": src(0.1), "ceiling": src(0.5)}}},
    ],
    "free": {"conversions_per_month": src(2)},
    "churn": {"churned_customers": src(0), "customers_at_start": src(20)},
}


def self_test():
    import contextlib
    import copy
    import io
    ok = True

    def quiet(data):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            res = run(data)
        return res, out.getvalue()

    res, out = quiet(copy.deepcopy(FIXTURE))
    # team: typical = 2 + 50*0.10 + 0.1*40 = 11; fee = 0.02*50 + 0.25 = 1.25; margin = (50-11-1.25)/50 = 75.5 %
    # max-out = 2 + 200*0.10 + 0.5*40 = 42; margin = (50-42-1.25)/50 = 13.5 %
    # contribution = 37.75; break-even = 500/37.75 = 13.25; free cost = 200*(0.5+0.02) = 104
    expect = ["75.5 %", "13.5 %", "42.00", "13.25", "104.00", "52.00", "W02"]
    for e in expect:
        if e not in out:
            print(f"self-test: expected '{e}' in output")
            ok = False
    if res.findings:
        print("self-test: clean fixture produced findings: " + "; ".join(res.findings))
        ok = False
    bad = copy.deepcopy(FIXTURE)
    bad["plans"][1]["usage"]["sms_segment"]["ceiling"] = src(None)
    bad["unit_costs"]["storage_gb"] = {"value": 0.02}
    bad["plans"][1]["usage"]["support_hour"]["ceiling"] = src(5)
    res, out = quiet(bad)
    codes = {f.split(" ", 1)[0] for f in res.findings}
    for code in ("E01", "E02"):
        if code not in codes:
            print(f"self-test: bad fixture did not trigger {code}")
            ok = False
    if "n/a | n/a" not in out:
        print("self-test: unbounded plan still printed a max-out margin")
        ok = False
    loss = copy.deepcopy(FIXTURE)
    loss["plans"][1]["usage"]["sms_segment"]["ceiling"] = src(1000)
    res, out = quiet(loss)
    if not any(f.startswith("E03") for f in res.findings):
        print("self-test: max-out loss did not trigger E03")
        ok = False
    assumed = copy.deepcopy(FIXTURE)
    assumed["unit_costs"]["sms_segment"] = src(0.10, assumption=True)
    res, out = quiet(assumed)
    if "75.5 %*" not in out:
        print("self-test: assumption was not marked")
        ok = False
    print("self-test: " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model", nargs="?")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.model:
        ap.print_usage(sys.stderr)
        return 2
    try:
        with open(args.model, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        print(f"cannot read model: {exc}", file=sys.stderr)
        return 2
    return 1 if run(data).findings else 0


if __name__ == "__main__":
    sys.exit(main())
