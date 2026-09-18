"""Measurement registry (09 §15.4). Every measurement declares its layer and tier.

Tier 0 runs on the standard library. Tier 1 runs when the analyser is installed (measure/analyser.py); otherwise it is not
computed and the report says why. Tier 2 (`ko.preserve`) runs on paste-in pairs only.
"""
from measure import analyser, exclusion
from measure.measurements import tier0, tier1, tier2

MEASUREMENTS = [dict(name=n, fn=f, layers=l, tier=t) for n, f, l, t in tier0.MEASUREMENTS + tier1.MEASUREMENTS]
PRESERVE = "ko.preserve"
PRESERVE_DECL = {"layers": ["skill"], "tier": 2, "kinds": list(tier2.KINDS)}
DELEGATION_PREFIX = "delegation_prompt_"


def available_tiers():
    return (0, 1, 2) if analyser.available() else (0, 2)


def _features(res, tiers, layer=None):
    return {m["name"]: m["fn"](res) for m in MEASUREMENTS
            if m["tier"] in tiers and (m["tier"] == 0 or res.analysis is not None) and (layer is None or layer in m["layers"])}


def compute_text(text, tiers=None):
    tiers = available_tiers() if tiers is None else tiers
    return _features(exclusion.run(text or "", analyse=None if 1 in tiers else False), tiers)


def compute_pair(original, rewrite, tiers=None):
    """A paste-in pair: every measurement on the rewrite, and ko.preserve on the two."""
    tiers = available_tiers() if tiers is None else tiers
    out = compute_text(rewrite, tiers)
    if 2 in tiers:
        out[PRESERVE] = tier2.preserve(original, rewrite)
    return out


def is_paste_in(annotation):
    return stratum_of(annotation).startswith(tier2.PASTE_IN_STRATUM)


def stratum_of(annotation):
    ann = annotation or {}
    return ann.get("stratum") or (ann.get("corpus_prompt_id") or "unannotated").split("/")[0]


def compute(record, annotation, tiers=None):
    """Features of one log record: every measurement on the output; on a sub record, the policy-layer ones on the
    delegation prompt as well (09 §15.4 capture-dependent); on a paste-in record, ko.preserve against the pasted text."""
    tiers = available_tiers() if tiers is None else tiers
    if is_paste_in(annotation) and record.get("harness_position") != "sub-to-orchestrator":
        out = compute_pair(tier2.pasted_original(record.get("task")), record.get("output"), tiers)
    else:
        out = compute_text(record.get("output"), tiers)
    if record.get("harness_position") == "sub-to-orchestrator" and record.get("task"):
        res = exclusion.run(record["task"], analyse=None if 1 in tiers else False)
        for name, value in _features(res, tiers, layer="policy").items():
            out[DELEGATION_PREFIX + name] = value
    return out


def declarations():
    out = {m["name"]: {"layers": list(m["layers"]), "tier": m["tier"]} for m in MEASUREMENTS}
    out[PRESERVE] = dict(PRESERVE_DECL)
    return out


def analyser_status():
    return {"version": analyser.version()} if analyser.available() else {"version": None, "unavailable": analyser.unavailable_reason()}


def report(logs, index):
    """09 §15.6: arm and stratum counts; floor exclusions (none); measurement declarations; the analyser version."""
    by_session, by_turn = index
    arms, strata, profiles = {}, {}, {}
    for _, rec in logs:
        ann = by_turn.get((rec.get("session_id"), rec.get("turn_key"))) or by_session.get(rec.get("session_id"))
        arm = (ann or {}).get("arm", "unannotated")
        stratum = stratum_of(ann)
        arms[arm] = arms.get(arm, 0) + 1
        strata[stratum] = strata.get(stratum, 0) + 1
        prof = (ann or {}).get("profile_selected") or "none"
        profiles[prof] = profiles.get(prof, 0) + 1
    return {"arm_counts": arms, "stratum_counts": strata, "profile_counts": profiles,
            "floor_exclusions": {"count": 0, "reason": "no Tier 0 or Tier 1 measurement applies a length floor"},
            "tiers_computed": list(available_tiers()), "analyser": analyser_status(),
            "measurements": declarations()}
