"""Case runner for tests/measure-cases/ (09 §17.3).

A case is YAML in the subset build/mini_yaml.py reads: `id`, `profile`, `arm`, `layer`, `input` (a JSON-quoted string:
the reply text the measurements read), and `expect`, whose keys are dotted paths into a measurement's value
(`em_dash_count.count`, `phrase_battery.entries.rewrite.A-1.count`) with `max`, `min` or `equals`. A key nothing reads is
an error, not a silent pass (09 §17.3: a field nothing reads is not kept).

A paste-in case (Tier 2) carries the original in `input`, as 09 §17.3 says, and the rewrite in `output`: the measurements
then read `output`, and `ko.preserve` reads both. `expect.preserve: [kinds]` passes when each kind has zero violations; a
case that must fail a kind says so with a dotted path (`ko.preserve.quote.pass: {equals: false}`).

A check on a measurement whose tier did not run (Tier 1 without the analyser) is reported as skipped, never as a pass.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build.mini_yaml import load as load_yaml  # noqa: E402

from measure import exclusion  # noqa: E402
from measure import measurements as registry  # noqa: E402

DECLARED = registry.declarations()


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


def measurement_of(path):
    """The measurement a dotted path names: the longest declared name it starts with (`ko.preserve` contains a dot)."""
    for name in sorted(DECLARED, key=len, reverse=True):
        if path == name or path.startswith(name + "."):
            return name
    return path.split(".")[0]


def lookup(features, path):
    name = measurement_of(path)
    rest = path[len(name) + 1:]
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


def run(cases_dir, tiers=None):
    tiers = registry.available_tiers() if tiers is None else tiers
    results, failures, skipped = [], [], []
    covered = {}
    for f in sorted(Path(cases_dir).glob("*.yaml")):
        case = load_yaml(f)
        if case.get("output") is not None:
            feats = registry.compute_pair(case["input"], case["output"], tiers)
        else:
            feats = registry.compute_text(case["input"], tiers)
        expect = dict(case.get("expect") or {})
        for kind in expect.pop("preserve", None) or []:
            expect[f"{registry.PRESERVE}.{kind}.pass"] = {"equals": True}
        for path, cond in expect.items():
            name = measurement_of(path)
            tier = DECLARED.get(name, {}).get("tier")
            kind_tier1 = name == registry.PRESERVE and any(path.startswith(f"{name}.{k}") for k in ("proper_noun", "register"))
            if tier not in tiers or ((tier == 1 or kind_tier1) and 1 not in tiers):
                skipped.append({"case": case["id"], "expect": path, "reason": f"tier {1 if kind_tier1 else tier} not computed"})
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
                covered.setdefault(name, {"correct": set(), "defective": set()})[kind].add(case["id"])
                if not ok:
                    failures.append(row)
    coverage = {m: {k: len(v) for k, v in c.items()} for m, c in sorted(covered.items())}
    return {"exclusion_version": exclusion.version(None if 1 in tiers else False), "analyser": registry.analyser_status(),
            "tiers": list(tiers), "checks": len(results), "failures": failures, "skipped": len(skipped),
            "skipped_checks": skipped, "coverage_cases_per_measurement": coverage, "results": results}


if __name__ == "__main__":
    out = run(sys.argv[1] if len(sys.argv) > 1 else ROOT / "tests/measure-cases")
    print(json.dumps({k: v for k, v in out.items() if k != "results"}, ensure_ascii=False, indent=1))
