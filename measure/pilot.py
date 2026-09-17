"""Pilot report (10_plan.md P8.3–P8.4; 09 §18.4 item 1). Reads logs/, annotations/ and derived/ of a corpus home, for one
batch. Run `python3 -m measure run --home <home>` first, so derived records exist.

  python3 -m measure pilot --home <corpus home> --batch <id> [--prompts corpus/prompts/set-1.json] [--report <path>]

What it reports:
  join          every log record of the batch's sessions joins an annotation and a derived record (P8.2)
  exclusion     false negatives of the pass on generated replies: echo prompts carry labelled zone spans, and each span
                the reply reproduces must lie inside its zone's spans; a span the reply does not reproduce is counted apart
  false_pos     per measurement, on the deliberately correct stratum: the share of main records whose primary value is on
                the defect side of zero, with a Wilson 95% interval, overall and per arm and profile (09 §16.1: per arm)
  hand_back     sub records whose output is Claude Code's hand-back stub (09 §14.2)
  truncation    records with a truncated tool-output scan (L2)
  variance      per measurement, the session-level SD within (stratum, arm, profile) cells, pooled
  power         sessions per arm by a normal-approximation power calculation (flow.md F9)

A primary value is one number per measurement, named in PRIMARY. Nothing here is a threshold: `fires` is only the zero
line that makes a false-positive rate countable, and a measurement whose clean value is not zero has no zero line.
"""
import json
import math
import statistics
from pathlib import Path

from measure import exclusion
from measure import measurements as registry
from measure.runner import read_jsonl

ALPHA, POWER, EFFECT_SD = 0.05, 0.8, 0.5          # flow.md F9 (user, 2026-09-17, U1)
HANDBACK_STUB = "I sent my report to the agent that started me."
ROOT = Path(__file__).resolve().parents[1]

# measurement -> (dotted path to the primary value, fires rule). Rules: "gt0" value > 0; "false" value is False;
# "gt1" value > 1; None: no zero line (the clean value is not zero), so no false-positive rate
PRIMARY = {
    "em_dash_count": ("per_100_eojeol", "gt0"),
    "emoji_count": ("per_100_eojeol", "gt0"),
    "bold_density": ("per_100_eojeol", "gt0"),
    "bullet_density": ("ratio", "gt0"),
    "header_formula": ("ratio", "gt0"),
    "quote_emphasis_count": ("count", "gt0"),
    "phrase_battery": ("total", "gt0"),
    "english_ratio": ("ratio", None),
    "english_gloss_repeat": ("count", "gt0"),
    "sentence_len_var": ("cv", None),
    "paragraph_initial_repeat": ("ratio", "gt0"),
    "comma_rate": ("after_connective", "gt0"),
    "spelling_denylist": ("count", "gt0"),
    "quote_balance": ("balanced", "false"),
    "allomorph_errors": ("count", "gt0"),
    "honorific_address": ("present", None),
    "noun_ending_ratio": ("ratio", "gt0"),
    "particle_absence_ratio": ("ratio", "gt0"),
    "speech_level": ("levels_present", "gt1"),
    "noun_run_length": ("max", None),
    "genitive_ui_ratio": ("ratio", "gt0"),
    "ending_monotony": ("ratio", None),
    "pos_ngram_diversity": ("ratio", None),
    "adnominal_chain_depth": ("count", "gt0"),
    "suffix_jeok_density": ("per_100_eojeol", "gt0"),
    "spacing_errors": ("per_100_eojeol", "gt0"),
}


def value_of(features, name):
    path, _ = PRIMARY[name]
    v = features.get(name)
    for k in path.split("."):
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    if isinstance(v, bool):
        return float(v)
    return float(v) if isinstance(v, (int, float)) else None


def fires(features, name):
    path, rule = PRIMARY[name]
    raw = features.get(name, {})
    for k in path.split("."):
        raw = raw.get(k) if isinstance(raw, dict) else None
    if rule is None or raw is None:
        return None
    return {"gt0": lambda v: v > 0, "gt1": lambda v: v > 1, "false": lambda v: v is False}[rule](raw)


def wilson(k, n, z=1.959964):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 4), round(min(1.0, c + h), 4)]


def load(home, batch):
    home = Path(home).expanduser()
    anns = [a for _, a in read_jsonl(home / "annotations") if a.get("batch_id") == batch]
    sessions = {a["session_id"] for a in anns}
    by_turn = {(a["session_id"], a.get("turn_key")): a for a in anns}
    logs = [r for _, r in read_jsonl(home / "logs") if r.get("session_id") in sessions]
    derived = {d["record_id"]: d for _, d in read_jsonl(home / "derived")}
    return anns, logs, by_turn, derived


def join_report(anns, logs, by_turn, derived):
    unjoined_ann = [r["id"] for r in logs if (r["session_id"], r.get("turn_key")) not in by_turn]
    unjoined_derived = [r["id"] for r in logs if r["id"] not in derived]
    return {"log_records": len(logs), "main": sum(r["harness_position"] == "main-to-user" for r in logs),
            "sub": sum(r["harness_position"] == "sub-to-orchestrator" for r in logs), "annotations": len(anns),
            "annotations_without_log_record": sum(1 for a in anns if not a.get("log_record_found")),
            "records_without_annotation": len(unjoined_ann), "records_without_derived": len(unjoined_derived),
            "all_joined": not unjoined_ann and not unjoined_derived}


def exclusion_on_replies(mains, prompts):
    zones = {}
    reproduced = {"echo_records": 0, "text_reproduced_verbatim": 0}
    for r, a in mains:
        p = prompts.get(a["corpus_prompt_id"])
        if not p or "zones" not in p:
            continue
        reproduced["echo_records"] += 1
        source = p["text"].split("\n\n", 1)[1]
        reproduced["text_reproduced_verbatim"] += source in r["output"]
        res = exclusion.run(r["output"])
        for z in p["zones"]:
            row = zones.setdefault(z["zone"], {"positives": 0, "not_reproduced": 0, "false_negatives": 0, "missed": []})
            i = r["output"].find(z["text"])
            if i < 0:
                row["not_reproduced"] += 1
                continue
            row["positives"] += 1
            inside = all(any(s <= k < e for s, e in res.spans[z["zone"]]) for k in range(i, i + len(z["text"])) if not r["output"][k].isspace())
            if not inside:
                row["false_negatives"] += 1
                row["missed"].append(f"{a['corpus_prompt_id']} arm {a['arm']}: {z['text']}")
    return {"exclusion_version": exclusion.version(), **reproduced, "zones": zones}


def false_positive_rates(mains, derived):
    out = {}
    correct = [(r, a) for r, a in mains if a["stratum"] == "correct-korean"]
    for name, (path, rule) in PRIMARY.items():
        if rule is None:
            vals = [value_of(derived[r["id"]]["features"], name) for r, _ in correct if r["id"] in derived]
            vals = [v for v in vals if v is not None]
            out[name] = {"primary": path, "rule": None, "fp_rate": None, "reason": "no zero line: the clean value is not zero",
                         "n": len(vals), "mean": round(statistics.mean(vals), 4) if vals else None,
                         "min": min(vals, default=None), "max": max(vals, default=None)}
            continue
        cells = {}
        for r, a in correct:
            f = fires(derived.get(r["id"], {}).get("features", {}), name)
            if f is None:
                continue
            for key in ("all", f"{a['arm']}/{a.get('profile_selected') or 'none'}"):
                c = cells.setdefault(key, [0, 0])
                c[0] += bool(f)
                c[1] += 1
        out[name] = {"primary": path, "rule": rule, **({} if cells else {"all": {"fires": 0, "n": 0, "fp_rate": None, "reason": "no record had a value"}}),
                     **{k: {"fires": v[0], "n": v[1], "fp_rate": round(v[0] / v[1], 4), "wilson_95": wilson(*v)} for k, v in sorted(cells.items())}}
    return out


def session_values(mains, derived):
    """(stratum, arm, profile) -> measurement -> [session mean]."""
    per = {}
    for r, a in mains:
        if r["id"] not in derived:
            continue
        cell = (a["stratum"], a["arm"], a.get("profile_selected") or "none")
        feats = derived[r["id"]]["features"]
        for name in PRIMARY:
            v = value_of(feats, name)
            if v is not None:
                per.setdefault(cell, {}).setdefault(name, {}).setdefault(r["session_id"], []).append(v)
    return {cell: {n: [statistics.mean(v) for v in s.values()] for n, s in ms.items()} for cell, ms in per.items()}


def variance_and_power(mains, derived):
    cells = session_values(mains, derived)
    z = statistics.NormalDist().inv_cdf(1 - ALPHA / 2) + statistics.NormalDist().inv_cdf(POWER)
    out = {}
    for name in PRIMARY:
        ss, df, n_sessions, used = 0.0, 0, 0, 0
        for cell, ms in cells.items():
            vals = ms.get(name, [])
            n_sessions += len(vals)
            if len(vals) > 1:
                ss += statistics.variance(vals) * (len(vals) - 1)
                df += len(vals) - 1
                used += 1
        sd = math.sqrt(ss / df) if df else None
        row = {"sessions": n_sessions, "cells_with_2_or_more": used, "df": df, "pooled_sd": round(sd, 6) if sd is not None else None}
        if sd:
            delta = EFFECT_SD * sd
            n = 2 * (z * sd / delta) ** 2
            row.update(min_effect=round(delta, 6), sessions_per_arm_exact=round(n, 3), sessions_per_arm=math.ceil(n))
        else:
            row.update(min_effect=None, sessions_per_arm=None, reason="no session-level variance observed" if df else "fewer than two sessions in every cell")
        out[name] = row
    return {"method": "normal approximation, two-sided two-sample: n per arm = 2 (z_(1-α/2) + z_(1-β))² σ² / δ²",
            "alpha": ALPHA, "power": POWER, "effect": f"δ = {EFFECT_SD} × pooled session-level SD (flow.md F9)",
            "z_sum": round(z, 6), "unit": "session; a session's value is the mean over its main records in one (stratum, arm, profile) cell",
            "note": "With δ set as a multiple of σ, σ cancels: n = 2 (z/0.5)² for every measurement with observed variance. σ is reported so δ is known in each measurement's own units",
            "measurements": out}


def run(home, batch, prompts_path=ROOT / "corpus/prompts/set-1.json"):
    anns, logs, by_turn, derived = load(home, batch)
    prompts = {p["id"]: p for p in json.loads(Path(prompts_path).read_text(encoding="utf-8"))["prompts"]}
    mains = [(r, by_turn[(r["session_id"], r.get("turn_key"))]) for r in logs
             if r["harness_position"] == "main-to-user" and (r["session_id"], r.get("turn_key")) in by_turn]
    subs = [r for r in logs if r["harness_position"] == "sub-to-orchestrator"]
    stub = sum(1 for r in subs if r["output"].strip() == HANDBACK_STUB)
    trunc = sum(1 for r in logs if (r.get("tool_output_chars") or {}).get("truncated_calls"))
    arms = {}
    for a in anns:
        k = f"{a['arm']}/{a.get('profile_selected') or 'none'}"
        arms[k] = arms.get(k, 0) + 1
    return {
        "batch": batch, "exclusion_version": exclusion.version(), "analyser": registry.analyser_status(),
        "annotations_by_arm_profile": dict(sorted(arms.items())),
        "arm_check_failures": [f"{a['corpus_prompt_id']} arm {a['arm']}: init {a.get('init_output_style')}" for a in anns if not a.get("arm_check")],
        "cost_usd": round(sum(a.get("cost_usd") or 0 for a in anns), 4),
        "join": join_report(anns, logs, by_turn, derived),
        "exclusion_on_generated_replies": exclusion_on_replies(mains, prompts),
        "false_positive_rate_correct_stratum": false_positive_rates(mains, derived),
        "hand_back": {"sub_records": len(subs), "stub_outputs": stub, "rate": round(stub / len(subs), 4) if subs else None,
                      "stub": HANDBACK_STUB, "wilson_95": wilson(stub, len(subs))},
        "truncation": {"records": len(logs), "records_with_truncated_calls": trunc, "rate": round(trunc / len(logs), 4) if logs else None,
                       "calls_truncated": sum((r.get("tool_output_chars") or {}).get("truncated_calls", 0) for r in logs)},
        "variance_and_power": variance_and_power(mains, derived),
        "tool_errors": sum(r.get("tool_errors") or 0 for r in logs),
        "turn_errors": sum(1 for a in anns if a.get("is_error")),
    }
