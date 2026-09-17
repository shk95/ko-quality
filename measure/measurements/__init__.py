"""Measurement registry (09 §15.4). Every measurement declares its layer and tier. Tier 1 and Tier 2 join in P6."""
from measure import exclusion
from measure.measurements import tier0

MEASUREMENTS = [dict(name=n, fn=f, layers=l, tier=t) for n, f, l, t in tier0.MEASUREMENTS]
DELEGATION_PREFIX = "delegation_prompt_"


def compute_text(text, tiers=(0,)):
    res = exclusion.run(text or "")
    return {m["name"]: m["fn"](res) for m in MEASUREMENTS if m["tier"] in tiers}


def compute(record, annotation, tiers=(0,)):
    """Features of one log record: every measurement on the output; on a sub record, the policy-layer ones on the
    delegation prompt as well (09 §15.4 capture-dependent)."""
    out = compute_text(record.get("output"), tiers)
    if record.get("harness_position") == "sub-to-orchestrator" and record.get("task"):
        res = exclusion.run(record["task"])
        for m in MEASUREMENTS:
            if m["tier"] in tiers and "policy" in m["layers"]:
                out[DELEGATION_PREFIX + m["name"]] = m["fn"](res)
    return out


def declarations():
    return {m["name"]: {"layers": list(m["layers"]), "tier": m["tier"]} for m in MEASUREMENTS}


def report(logs, index):
    """09 §15.6: arm and stratum counts; floor exclusions (none in Tier 0); measurement declarations."""
    by_session, by_turn = index
    arms, strata, profiles = {}, {}, {}
    for _, rec in logs:
        ann = by_turn.get((rec.get("session_id"), rec.get("turn_key"))) or by_session.get(rec.get("session_id"))
        arm = (ann or {}).get("arm", "unannotated")
        stratum = (ann or {}).get("stratum") or ((ann or {}).get("corpus_prompt_id") or "unannotated").split("/")[0]
        arms[arm] = arms.get(arm, 0) + 1
        strata[stratum] = strata.get(stratum, 0) + 1
        prof = (ann or {}).get("profile_selected") or "none"
        profiles[prof] = profiles.get(prof, 0) + 1
    return {"arm_counts": arms, "stratum_counts": strata, "profile_counts": profiles,
            "floor_exclusions": {"count": 0, "reason": "no Tier 0 measurement applies a length floor"},
            "measurements": declarations()}
