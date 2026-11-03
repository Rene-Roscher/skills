#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
mkdir -p docs/growth/sets docs/growth/snapshots
python3 - <<'PY'
import datetime as dt, json
today = dt.date.today()
live = today - dt.timedelta(days=5)
b_end = live - dt.timedelta(days=5)
b_start = b_end - dt.timedelta(days=27)
a_start, a_end = live, today - dt.timedelta(days=1)
site = "https://www.example.com/venues/"
treated = [site + s for s in ("halls", "rooftops", "studios")]
control = [site + s for s in ("barns", "galleries", "lofts")]
open("docs/growth/sets/CH-003-treated.txt", "w").write("\n".join(treated) + "\n")
open("docs/growth/sets/CH-003-control.txt", "w").write("\n".join(control) + "\n")
def win(s, e, lag):
    days = (e - s).days + 1
    return {"start": s.isoformat(), "end": e.isoformat(), "days": days, "start_weekday": s.strftime("%a"),
            "whole_weeks": days % 7 == 0, "inside_lag": lag}
def rows(per_day_t, per_day_c, days, pos_t, pos_c):
    out = []
    for p in treated:
        out.append({"page": p, "clicks": per_day_t * days, "impressions": per_day_t * days * 25, "ctr": 0.04,
                    "position": pos_t})
    for p in control:
        out.append({"page": p, "clicks": per_day_c * days, "impressions": per_day_c * days * 25, "ctr": 0.04,
                    "position": pos_c})
    return out
base = {"meta": {"label": "baseline", "created_at": (live - dt.timedelta(days=2)).isoformat() + "T08:00:00+00:00",
                 "window": win(b_start, b_end, False), "data_state": "final", "skipped": {}},
        "sources": {"gsc": {"page": {"rows": rows(10, 10, 28, 8.2, 7.9)}}}}
aft = {"meta": {"label": "ch-003-early", "created_at": today.isoformat() + "T07:00:00+00:00",
                "window": win(a_start, a_end, True), "data_state": "all", "skipped": {}},
       "sources": {"gsc": {"page": {"rows": rows(14, 13, (a_end - a_start).days + 1, 7.1, 7.0)}}}}
json.dump(base, open(f"docs/growth/snapshots/{base['meta']['created_at'][:10]}-baseline.json", "w"), indent=1)
json.dump(aft, open(f"docs/growth/snapshots/{today.isoformat()}-ch-003-early.json", "w"), indent=1)
open("docs/growth/changes.md", "w").write(f"""# Growth change log

## CH-003: Venue page titles name the venue type and the city

- Status: live
- Hypothesis: Titles that name the venue type and city raise clicks on the venue pages by at least 15 % within 28 days.
- Change type: title and description
- Treated set: `docs/growth/sets/CH-003-treated.txt` (3 pages)
- Control set: `docs/growth/sets/CH-003-control.txt` (3 pages)
- Primary metric: clicks, up, at least 15 %
- Baseline snapshot: `docs/growth/snapshots/{base['meta']['created_at'][:10]}-baseline.json`
- Shipped: {live.isoformat()}
- Live HTML confirmed: {live.isoformat()}
- Recrawl confirmed (URL Inspection `lastCrawlTime`): not checked yet
- Re-measure date: not set
- Revert condition: difference in differences on clicks below 5 points, or negative
- Outcome:
- Decision:
""")
PY
git add -A
git -c user.name=Dev -c user.email=dev@example.com commit -q -m 'docs: log CH-003'
