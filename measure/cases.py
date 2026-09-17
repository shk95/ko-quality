"""Case runner for tests/measure-cases/ (09 §17.3).

A case is YAML in the subset build/mini_yaml.py reads: `id`, `profile`, `arm`, `layer`, `input` (a JSON-quoted string:
the reply text the measurements read), and `expect`, whose keys are dotted paths into a measurement's value
(`em_dash_count.count`, `phrase_battery.entries.rewrite.A-1.count`) with `max`, `min` or `equals`. A key nothing reads is
an error, not a silent pass (09 §17.3: a field nothing reads is not kept).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build.mini_yaml import load as load_yaml  # noqa: E402

from measure import exclusion  # noqa: E402
from measure import measurements as registry  # noqa: E402


def number(v):
    if isinstance(v, bool) or v is None:
        return v
    try:
        return int(v)
    except (TypeError, ValueError):
        try:
            return float(v)
        except (TypeError, ValueError):
            return v


def lookup(features, path):
    name, _, rest = path.partition(".")
    if name not in features:
        raise KeyError(f"no measurement {name}")
    value = features[name]
    while rest:
        if isinstance(value, dict):
            for k in sorted(value, key=len, reverse=True):     # keys may contain dots (phrase ids such as rewrite.A-1)
                if rest == k or rest.startswith(k + "."):
                    value, rest = value[k], rest[len(k) + 1:]
                    break
            else:
                raise KeyError(f"{path}: no key at {rest!r}")
        else:
            raise KeyError(f"{path}: {rest!r} under a non-map value")
    return value


def check(value, op, target):
    target = number(target)
    if op == "equals":
        return value == target
    if value is None:
        return False
    return value <= target if op == "max" else value >= target if op == "min" else None


def run(cases_dir, tiers=(0,)):
    results, failures = [], []
    covered = {}
    for f in sorted(Path(cases_dir).glob("*.yaml")):
        case = load_yaml(f)
        feats = registry.compute_text(case["input"], tiers)
        for path, cond in (case.get("expect") or {}).items():
            if path == "preserve":
                continue
            for op, target in cond.items():
                try:
                    value = lookup(feats, path)
                    ok = check(value, op, target)
                except KeyError as exc:
                    value, ok = f"error: {exc}", False
                row = {"case": case["id"], "expect": path, "op": op, "target": number(target), "value": value, "pass": bool(ok)}
                results.append(row)
                kind = "correct" if "-correct-" in case["id"] else "defective"
                covered.setdefault(path.split(".")[0], {"correct": set(), "defective": set()})[kind].add(case["id"])
                if not ok:
                    failures.append(row)
    coverage = {m: {k: len(v) for k, v in c.items()} for m, c in sorted(covered.items())}
    return {"exclusion_version": exclusion.EXCLUSION_VERSION, "checks": len(results), "failures": failures,
            "coverage_cases_per_measurement": coverage, "results": results}


if __name__ == "__main__":
    out = run(sys.argv[1] if len(sys.argv) > 1 else ROOT / "tests/measure-cases")
    print(json.dumps({k: v for k, v in out.items() if k != "results"}, ensure_ascii=False, indent=1))
