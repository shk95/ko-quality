"""Separation of correct from telegraphic Korean on the committed F7 set (10_plan.md P6.1), beside E2's recorded values.

  python3 -m measure separation [--cases tests/measure-cases] [--report <path>]

For `noun_ending_ratio` and `particle_absence_ratio`: per set, the pooled ratio (sum of numerators over sum of
denominators), the mean, min and max of the case ratios, and the gaps. The direction E2 measured is telegraphic higher.
E2's values are read from tests/runs/02-E2/kiwipiepy-recipes.json, not restated. E2's sentences were never committed, so
the two sets are different texts: the comparison is of direction and size, not of values.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build.mini_yaml import load as load_yaml  # noqa: E402

from measure import exclusion  # noqa: E402
from measure import measurements as registry  # noqa: E402

CORRECT = ["t1-correct-01-prose", "t1-correct-02-irregular", "t1-correct-03-haeyo", "t1-correct-04-honorific", "t1-correct-05-technical"]
TELEGRAPHIC = ["t1-defect-01-telegraphic-nouns", "t1-defect-02-telegraphic-ham", "t1-defect-03-telegraphic-bare", "t1-defect-04-telegraphic-marks"]
BESIDE = ["t1-defect-05-memo-eum"]   # F15: 문서체 -음, counted as a noun ending, reported apart from the two sets
MEASURES = {"noun_ending_ratio": ("noun_endings", "sentences"), "particle_absence_ratio": ("absent", "nouns")}
E2_RECORD = ROOT / "tests/runs/02-E2/kiwipiepy-recipes.json"


def _set_stats(rows, num, den):
    ratios = [r["ratio"] for r in rows if r["ratio"] is not None]
    n, d = sum(r[num] for r in rows), sum(r[den] for r in rows)
    return {"cases": len(rows), num: n, den: d, "pooled": round(n / d, 4) if d else None,
            "mean": round(sum(ratios) / len(ratios), 4) if ratios else None, "min": min(ratios, default=None), "max": max(ratios, default=None),
            "per_case": [r["ratio"] for r in rows]}


def e2_values():
    rec = json.loads(E2_RECORD.read_text(encoding="utf-8"))["recipes"]
    ne = rec["noun_ending_ratio"]["measured"]["fixed_strip_trailing_punctuation"]
    pa = rec["particle_absence_ratio"]["measured"]["exclude_verbalised_nouns_from_denominator"]
    return {"noun_ending_ratio": {"recipe": "fixed_strip_trailing_punctuation", "correct": ne["correct_prose"], "telegraphic": ne["telegraphic"],
                                  "gap": ne["separation"]},
            "particle_absence_ratio": {"recipe": "exclude_verbalised_nouns_from_denominator", "correct_mean": pa["correct_mean"],
                                       "defective_mean": pa["defective_mean"], "gap": pa["gap"], "fully_separable": pa["fully_separable"],
                                       "correct": pa["correct"], "defective": pa["defective"]}}


def run(cases_dir):
    cases = {c["id"]: c for c in (load_yaml(f) for f in sorted(Path(cases_dir).glob("t1-*.yaml")))}
    missing = [i for i in CORRECT + TELEGRAPHIC + BESIDE if i not in cases]
    if missing or 1 not in registry.available_tiers():
        return {"failures": [f"missing cases: {missing}" if missing else f"analyser unavailable: {registry.analyser_status()}"]}
    feats = {i: registry.compute_text(cases[i]["input"]) for i in CORRECT + TELEGRAPHIC + BESIDE}
    out = {"exclusion_version": exclusion.version(), "analyser": registry.analyser_status(),
           "sets": {"correct": CORRECT, "telegraphic": TELEGRAPHIC, "beside": BESIDE}, "measurements": {}, "e2": e2_values(), "failures": []}
    for m, (num, den) in MEASURES.items():
        cor = _set_stats([feats[i][m] for i in CORRECT], num, den)
        tel = _set_stats([feats[i][m] for i in TELEGRAPHIC], num, den)
        row = {"correct": cor, "telegraphic": tel,
               "gap_mean": round(tel["mean"] - cor["mean"], 4), "gap_pooled": round(tel["pooled"] - cor["pooled"], 4),
               "gap_min_telegraphic_minus_max_correct": round(tel["min"] - cor["max"], 4),
               "direction": "telegraphic higher" if tel["mean"] > cor["mean"] else "not telegraphic higher",
               "fully_separable": tel["min"] > cor["max"],
               "beside": {i: feats[i][m] for i in BESIDE}}
        out["measurements"][m] = row
        if row["direction"] != "telegraphic higher":
            out["failures"].append(f"{m}: telegraphic is not higher (E2's direction)")
    out["sentences"] = {"correct": out["measurements"]["noun_ending_ratio"]["correct"]["sentences"],
                        "telegraphic": out["measurements"]["noun_ending_ratio"]["telegraphic"]["sentences"]}
    return out
