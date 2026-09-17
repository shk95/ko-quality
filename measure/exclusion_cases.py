"""False negatives per zone on the labelled set (09 §15.2 done-condition; 10_plan.md P4.1; flow.md F5).

Case file (tests/exclusion-cases/*.json), written by us, synthetic:
  {"id": str, "kind": "correct" | "defective", "text": str,
   "positives": [{"zone": str, "text": str, "nth": int?}],     spans the pass must exclude (or, for structure, label)
   "negatives": [{"zone": str, "text": str, "nth": int?}]}     near misses: look like the zone and are not
A positive is found when every non-space character of it lies inside a span of its zone. One that is excluded, but under
another zone, is counted apart (`other_zone`) and is not a false negative of the pass. A negative is a false positive
when any character of it lies inside a span of its zone. `nth` picks the nth occurrence (0-based) when the text repeats.
"""
import json
from pathlib import Path

from measure import exclusion

from measure import analyser


def locate(text, needle, nth=0):
    i = -1
    for _ in range(nth + 1):
        i = text.find(needle, i + 1)
        if i < 0:
            return None
    return i, i + len(needle)


def covered(spans, s, e, text, whole=True):
    inside = [any(a <= i < b for a, b in spans) for i in range(s, e)]
    chars = [ok for i, ok in zip(range(s, e), inside) if not text[i].isspace()]
    return all(chars) if whole else any(chars)


def evaluate(cases_dir, run=exclusion.run):
    zones = {z: {"positives": 0, "false_negatives": 0, "other_zone": 0, "other_zone_isolated_misses": 0, "negatives": 0, "false_positives": 0, "missed": [], "wrongly_excluded": []}
             for z in exclusion.ZONES}
    files = sorted(Path(cases_dir).glob("*.json"))
    errors = []
    for f in files:
        case = json.loads(f.read_text(encoding="utf-8"))
        res = run(case["text"])
        for label, key in (("positives", "positives"), ("negatives", "negatives")):
            for item in case.get(label, []):
                z = item["zone"]
                loc = locate(case["text"], item["text"], item.get("nth", 0))
                if loc is None:
                    errors.append(f"{case['id']}: {label} text not found: {item['text']!r}")
                    continue
                spans = res.spans[z]
                row = zones[z]
                row[key] += 1
                if label == "positives" and not covered(spans, *loc, case["text"], whole=True):
                    others = [s for oz in exclusion.REMOVED if oz != z for s in res.spans[oz]]
                    if z in exclusion.REMOVED and covered(spans + others, *loc, case["text"], whole=True):
                        row["other_zone"] += 1
                        # isolation: would the zone find it on its own line, without the span that swallowed it? (P4 V4)
                        window = case["text"][loc[0]:loc[1] + 20].split("\n")[0]   # the item and what follows it (a speech marker follows its quote)
                        alone = run(window).spans[z]
                        found_alone = covered(alone, 0, len(item["text"]), window, whole=True)
                        row["other_zone_isolated_misses"] += 0 if found_alone else 1
                        row["missed"].append(f"{case['id']}: {item['text']} (other zone; alone: {'found' if found_alone else 'missed'})")
                    else:
                        row["false_negatives"] += 1
                        row["missed"].append(f"{case['id']}: {item['text']}")
                if label == "negatives" and covered(spans, *loc, case["text"], whole=False):
                    row["false_positives"] += 1
                    row["wrongly_excluded"].append(f"{case['id']}: {item['text']}")
    if not analyser.available():
        zones["proper_noun"]["status"] = "Tier 1 half not applied: the analyser is unavailable. Only Latin capitalised tokens are found"
    return {"exclusion_version": exclusion.version(), "analyser": analyser.version(), "cases": len(files), "zones": zones, "label_errors": errors}
