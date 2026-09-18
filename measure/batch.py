"""Sized-batch analysis (10_plan.md P9.1–P9.2; 09 §15.7, §18.1). Reads a corpus home for one batch, after
`python3 -m measure run`.

  python3 -m measure batch --home <corpus home> --batch <id> [--resamples 10000] [--seed 20260917] [--report <path>]

Per measurement, within stratum and within the layer the measurement declares:
  B − C   the policy's own effect (09 §18.1), per profile: arm B against arm C turns under that profile. Policy layer
  A − B   the skills' and agents' effect. Skill layer on main records; the agent layer compares sub records of A with B/C
Each difference is of session means (the unit is a session: 09 §18.2 alternates profiles inside a session, so turns are
not independent), with a **session-level percentile bootstrap** interval (flow.md F11: 10,000 resamples, fixed seed).
False-positive rates on the correct stratum carry a **Wilson** interval (09 §16.1). The method and resample count are
written beside every interval.

A `watch:` candidate is written only where 09 §15.7's two conditions hold: (1) a false-positive rate was observed on correct
Korean (the measurement has a zero line and correct-stratum records), and (2) the B − C difference is non-zero: its
bootstrap interval excludes zero, in at least one (stratum, profile). The candidate value is the measurement's
95th percentile over arm C sessions of that profile in the correct stratum when the defect side is high (`max`); it is a
candidate, read by nothing in era 02.
"""
import json
import math
import random
import statistics
from pathlib import Path

from measure import exclusion
from measure import measurements as registry
from measure.pilot import PRIMARY, fires, load, value_of, wilson

RESAMPLES, SEED = 10000, 20260917
LEVEL = 0.95


def percentile(sorted_vals, q):
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * q
    lo, hi = math.floor(k), math.ceil(k)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def bootstrap_diff(xs, ys, rng, resamples=RESAMPLES):
    """Percentile interval for mean(xs) − mean(ys), resampling sessions within each arm."""
    if len(xs) < 2 or len(ys) < 2:
        return None
    diffs = []
    for _ in range(resamples):
        a = rng.choices(xs, k=len(xs))
        b = rng.choices(ys, k=len(ys))
        diffs.append(statistics.fmean(a) - statistics.fmean(b))
    diffs.sort()
    lo, hi = percentile(diffs, (1 - LEVEL) / 2), percentile(diffs, 1 - (1 - LEVEL) / 2)
    return [round(lo, 6), round(hi, 6)]


def session_means(pairs, derived, name, position="main-to-user"):
    """session_id -> mean primary value over the session's records in `pairs`."""
    per = {}
    for r, a in pairs:
        if r["harness_position"] != position or r["id"] not in derived:
            continue
        v = value_of(derived[r["id"]]["features"], name)
        if v is not None:
            per.setdefault(r["session_id"], []).append(v)
    return {s: statistics.fmean(v) for s, v in per.items()}


def cell(pairs, **want):
    return [(r, a) for r, a in pairs if all((a.get(k) or "none") == v for k, v in want.items())]


def compare(xs, ys, rng):
    x, y = list(xs.values()), list(ys.values())
    row = {"n_sessions": [len(x), len(y)], "means": [round(statistics.fmean(x), 6) if x else None, round(statistics.fmean(y), 6) if y else None]}
    if x and y:
        row["difference"] = round(statistics.fmean(x) - statistics.fmean(y), 6)
        ci = bootstrap_diff(x, y, rng)
        row["interval"] = ci
        row["interval_method"] = f"session-level percentile bootstrap, {RESAMPLES} resamples, {int(LEVEL * 100)}%" if ci else "not computed: fewer than 2 sessions in an arm"
        row["nonzero"] = bool(ci and (ci[0] > 0 or ci[1] < 0))
    return row


def run(home, batch, resamples=RESAMPLES, seed=SEED):
    global RESAMPLES
    RESAMPLES = resamples
    rng = random.Random(seed)
    anns, logs, by_turn, derived = load(home, batch)
    # a session whose turns did not line up with its records is left out whole (arm check, task match, turn count, errors)
    failed = {a["session_id"] for a in anns if not (a.get("arm_check") and a.get("task_matches_prompt") and a.get("log_record_found")
                                                     and a.get("turns_complete", True) and not a.get("is_error"))}
    excluded = {"sessions": len(failed), "annotations": sum(1 for a in anns if a["session_id"] in failed),
                "log_records": sum(1 for r in logs if r["session_id"] in failed),
                "rule": "any annotation of the session fails arm_check, task_matches_prompt, log_record_found or turns_complete, or is_error"}
    anns = [a for a in anns if a["session_id"] not in failed]
    logs = [r for r in logs if r["session_id"] not in failed]
    by_turn = {k: v for k, v in by_turn.items() if k[0] not in failed}
    pairs = [(r, by_turn[(r["session_id"], r.get("turn_key"))]) for r in logs if (r["session_id"], r.get("turn_key")) in by_turn]
    decl = registry.declarations()
    strata = sorted({a["stratum"] for a in anns})
    out = {"batch": batch, "exclusion_version": exclusion.version(), "analyser": registry.analyser_status(),
           "bootstrap": {"method": "session-level percentile bootstrap", "resamples": resamples, "seed": seed, "level": LEVEL},
           "false_positive_method": "Wilson score interval, 95%", "excluded": excluded, "sessions_by_arm": {}, "measurements": {}, "candidates": {}}
    for arm in ("A", "B", "C"):
        out["sessions_by_arm"][arm] = len({a["session_id"] for a in anns if a["arm"] == arm})
    for name, (path, rule) in PRIMARY.items():
        layers = decl[name]["layers"]
        m = {"primary": path, "layers": layers, "tier": decl[name]["tier"], "by_stratum": {}}
        correct = cell(pairs, stratum="correct-korean")
        fp = {}
        for arm_profile in sorted({f"{a['arm']}/{a.get('profile_selected') or 'none'}" for _, a in correct}):
            arm, prof = arm_profile.split("/")
            fl = [fires(derived[r["id"]]["features"], name) for r, a in cell(correct, arm=arm, profile_selected=prof)
                  if r["harness_position"] == "main-to-user" and r["id"] in derived]
            fl = [f for f in fl if f is not None]
            if fl:
                fp[arm_profile] = {"fires": sum(fl), "n": len(fl), "rate": round(sum(fl) / len(fl), 4), "wilson_95": wilson(sum(fl), len(fl))}
        m["false_positive_rate_correct_stratum"] = fp if rule else {"not_observable": "no zero line: the clean value is not zero"}
        for stratum in strata:
            s = cell(pairs, stratum=stratum)
            row = {}
            if "policy" in layers:
                for prof in ("agent-reply", "formal-report"):
                    row[f"B_minus_C/{prof}"] = compare(session_means(cell(s, arm="B"), derived, name),
                                                       session_means(cell(s, arm="C", profile_selected=prof), derived, name), rng)
            if "skill" in layers:
                row["A_minus_B"] = compare(session_means(cell(s, arm="A"), derived, name), session_means(cell(s, arm="B"), derived, name), rng)
            if stratum == "delegation":
                row["agent_layer_A_minus_BC"] = compare(session_means(cell(s, arm="A"), derived, name, "sub-to-orchestrator"),
                                                        {**session_means(cell(s, arm="B"), derived, name, "sub-to-orchestrator"),
                                                         **session_means(cell(s, arm="C"), derived, name, "sub-to-orchestrator")}, rng)
            m["by_stratum"][stratum] = row
        # 09 §15.7
        observed_fp = bool(rule) and any(v["n"] for v in fp.values())
        nonzero = [(st, k) for st, row in m["by_stratum"].items() for k, v in row.items() if k.startswith("B_minus_C") and v.get("nonzero")]
        m["candidate"] = {"fp_observed": observed_fp, "nonzero_B_minus_C": [f"{st}:{k}" for st, k in nonzero],
                          "qualifies": observed_fp and bool(nonzero)}
        if not observed_fp:
            m["candidate"]["reason"] = "no false-positive rate observed on correct Korean" + ("" if rule else " (no zero line)")
        elif not nonzero:
            m["candidate"]["reason"] = "no B − C interval excludes zero" + ("" if "policy" in layers else " (skill layer: B − C is not this layer's comparison)")
        else:
            m["candidate"]["reason"] = "both 09 §15.7 conditions hold"
            for prof in sorted({k.split("/")[1] for _, k in nonzero}):
                vals = sorted(session_means(cell(pairs, stratum="correct-korean", arm="C", profile_selected=prof), derived, name).values())
                if vals:
                    if rule == "false":   # the defect side is low (quote_balance: 1 = balanced)
                        cand = {"min": round(percentile(vals, 0.05), 6), "basis": f"5th percentile of arm C session means, correct-korean stratum, n={len(vals)}"}
                    else:
                        cand = {"max": round(percentile(vals, 0.95), 6), "basis": f"95th percentile of arm C session means, correct-korean stratum, n={len(vals)}"}
                    out["candidates"].setdefault(prof, {})[name] = cand
        out["measurements"][name] = m
    for prof, cands in out["candidates"].items():
        cands["_meta"] = {"source": f"corpus {batch}", "arm": "C", "exclusion_version": exclusion.version(), "status": "candidate"}
    return out
