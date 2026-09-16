"""Validate normalized files against the rules in upstream/interface/*.schema.yaml (stdlib only; the schema files are the reference)."""
import re

from .normalized import load, sha
from .source import ROOT, lock

ROLES = {
    "procedure": {"required": ["slot"]},
    "taxonomy": {"required": ["slot"]},
    "reference": {"required": ["slot", "name", "kind"], "kind": {"rubric", "research", "recipes", "derived"}},
    "policy": {"required": ["name"], "sections": ["data"]},
}
KINDS = {
    # structural kinds, assigned by the block parser (whole-file extraction)
    "heading", "paragraph", "item", "quote", "row", "table-header", "table-sep", "tag",
    # semantic kinds, assigned by a hand-written selection
    "summary", "invariant", "step", "output", "check", "grade", "input",
    "severity", "exclusion", "category", "pattern", "block",
}
TRANSFORMS = {"verbatim", "selected", "adapted"}


def validate_text(rel, text, locks):
    errors = []
    top, frags = load(text)
    role = top.get("role")
    if role not in ROLES:
        return [f"{rel}: role {role!r} not in {sorted(ROLES)}"]
    for key in ROLES[role]["required"]:
        if key not in top:
            errors.append(f"{rel}: missing top-level {key}")
    if "kind" in ROLES[role] and top.get("kind") not in ROLES[role]["kind"]:
        errors.append(f"{rel}: kind {top.get('kind')!r} not in {sorted(ROLES[role]['kind'])}")
    for section in ROLES[role].get("sections", []):
        if not re.search(rf"^{section}:$", text, re.M):
            errors.append(f"{rel}: missing section {section}:")
    if not frags:
        errors.append(f"{rel}: no fragments")
    ids, anchors = set(), set()
    for f in frags:
        where = f"{rel} {f['id']}"
        if f["id"] in ids:
            errors.append(f"{where}: duplicate id")
        ids.add(f["id"])
        for k in ("kind", "text", "upstream", "commit", "path", "anchor", "content_hash", "transform"):
            if k not in f or f[k] in ("", None):
                errors.append(f"{where}: missing {k}")
        if f.get("kind") not in KINDS:
            errors.append(f"{where}: kind {f.get('kind')!r} not allowed")
        if "blanks" in f and not str(f["blanks"]).isdigit():
            errors.append(f"{where}: blanks must be a non-negative integer")
        if f.get("transform") not in TRANSFORMS:
            errors.append(f"{where}: transform {f.get('transform')!r} not allowed")
        if f.get("transform") == "adapted" and not f.get("original"):
            errors.append(f"{where}: adapted without original (06 §5.4)")
        if f.get("upstream") not in locks:
            errors.append(f"{where}: upstream {f.get('upstream')!r} not in lock.yaml")
        elif f.get("commit") != locks[f["upstream"]]["commit"]:
            errors.append(f"{where}: commit {f.get('commit')} is not the lock commit")
        if "text" in f and sha(f["text"]) != f.get("content_hash"):
            errors.append(f"{where}: content_hash does not match text")
        key = (f.get("path"), f.get("anchor"))
        if key in anchors:
            errors.append(f"{where}: anchor not unique in file (06 §5.5 rule 2): {f.get('anchor')}")
        anchors.add(key)
    return errors


def validate_all():
    locks = lock()
    errors = []
    for p in sorted((ROOT / "upstream/normalized").rglob("*.yaml")):
        errors += validate_text(str(p.relative_to(ROOT / "upstream/normalized")), p.read_text(encoding="utf-8"), locks)
    return errors
