"""Summary of batch-01 after the review's top-up (era 02 7-review, section A).

python3 tests/runs/02-review/pooled_summary.py --progress <batch>.progress.jsonl --canary <canary report>
    --report <pooled batch report> --before tests/runs/02-P9/batch-01-report.json
    --streams <stream dir> [--streams <stream dir> ...] --out <path>

Written by committed code so the figures can be regenerated (review B6). Paths are arguments; none is written out.
"""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

ALPHA, EFFECT_SD = 0.05, 0.5  # F9
TOPUP_ROUNDS = (19, 20, 21)


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def power(n):
    z = 1.959964  # two-sided alpha 0.05
    return phi(math.sqrt(n / 2) * EFFECT_SD - z)


def nonzero_pairs(report):
    out = {}
    for m, v in report["measurements"].items():
        for stratum, comparisons in v["by_stratum"].items():
            for c, x in comparisons.items():
                if isinstance(x, dict) and "nonzero" in x:
                    out[f"{m}|{stratum}|{c}"] = x
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--progress", required=True)
    ap.add_argument("--canary", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--before", required=True)
    ap.add_argument("--streams", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    rows = [json.loads(line) for line in Path(a.progress).read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = [r for r in rows if not r.get("skipped")]
    rnd = lambda r: int(re.search(r"-r(\d+)$", r["key"]).group(1))
    topup = [r for r in rows if rnd(r) in TOPUP_ROUNDS]
    first = [r for r in rows if rnd(r) not in TOPUP_ROUNDS]
    cells = Counter(re.sub(r"-\d+-([ABC])-r\d+$", r"-\1", r["key"]) for r in rows)
    canary = json.loads(Path(a.canary).read_text(encoding="utf-8"))
    canary_cost = sum(r.get("cost_usd") or 0 for r in canary["runs"])

    versions = Counter()
    for d in a.streams:
        for f in Path(d).rglob("*"):
            if f.is_file():
                versions.update(re.findall(r'"claude_code_version":"([^"]+)"', f.read_text(encoding="utf-8", errors="replace")))

    before, pooled = json.loads(Path(a.before).read_text(encoding="utf-8")), json.loads(Path(a.report).read_text(encoding="utf-8"))
    b0, b1 = nonzero_pairs(before), nonzero_pairs(pooled)
    changed = lambda f: sorted(k for k in b1 if f(b0.get(k, {}).get("nonzero", False), b1[k]["nonzero"]))
    values = lambda c: {m: (v.get("max"), v.get("min")) for m, v in c.items() if m != "_meta"}

    n = min(cells.values())
    summary = {
        "batch": "batch-01",
        "topup_rounds": list(TOPUP_ROUNDS),
        "sessions": {"first_run": len(first), "topup": len(topup), "total": len(rows)},
        "sessions_per_stratum_arm_cell": sorted(set(cells.values())),
        "cells": len(cells),
        "achieved_power": {"n_per_arm": n, "effect": f"{EFFECT_SD} SD", "alpha": ALPHA, "power": round(power(n), 4),
                           "before_topup": round(power(54), 4),
                           "method": "normal approximation, Φ(sqrt(n/2)·d − z_(1−α/2))"},
        "topup_failed_sessions": sum(1 for r in topup if not (r["rc"] == 0 and r["arm_check"] and r["task_matches"]
                                                              and r["turns_seen"] == r["turns_expected"])),
        "excluded": pooled["excluded"],
        "sessions_by_arm_analysed": pooled["sessions_by_arm"],
        "claude_code_version_in_streams": dict(versions),
        "cost_usd_api_equivalent": {"first_run": round(sum(r.get("cost_usd") or 0 for r in first), 4),
                                    "topup": round(sum(r.get("cost_usd") or 0 for r in topup), 4),
                                    "topup_canaries": round(canary_cost, 4),
                                    "topup_ceiling": 40},
        "canary_verdict": canary["verdict"],
        "nonzero_interval_pairs": {"total_pairs": len(b1),
                                   "B_minus_C": [sum(1 for k, x in d.items() if "|B_minus_C" in k and x["nonzero"]) for d in (b0, b1)],
                                   "A_minus_B": [sum(1 for k, x in d.items() if "|A_minus_B" in k and x["nonzero"]) for d in (b0, b1)],
                                   "became_nonzero": changed(lambda o, p: p and not o),
                                   "became_zero": changed(lambda o, p: o and not p),
                                   "order": "[before top-up, pooled]"},
        "candidate_values_unchanged": all(values(before["candidates"][p]) == values(pooled["candidates"][p])
                                          for p in before["candidates"]),
    }
    Path(a.out).write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
