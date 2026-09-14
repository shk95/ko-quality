"""yoonmoon → procedure/diagnose, taxonomy/diagnose, reference/diagnose/* (flow.md D2, D5). Whole-file block extraction (P2)."""
from .markdown import parse
from .normalized import excluded_lines, fragment_lines
from .source import read

NAME = "yoonmoon"
DETECT = "skills/detect/SKILL.md"
TAX = "skills/humanize/references/ai-tell-taxonomy.md"
REFS = [("lread-rubric", "rubric", "skills/detect/references/lread-rubric.md"),
        ("katfishnet-research", "research", "skills/humanize/references/katfishnet-research.md"),
        ("xdac-research", "research", "skills/detect/references/xdac-research.md")]
HDR = "# Temporary format (P1 shape, used unchanged in P2 — flow.md). Schema is derived in P4. Text values are exact upstream bytes."


def _frags(prefix, path, blocks, include):
    out = []
    for n, b in enumerate(blocks):
        if b["kind"] == "tag" or not include(b):
            continue
        out.append(dict(id=f"{prefix}.{n:03d}", kind=b["kind"], text=b["text"], path=path, anchor=b["anchor"], transform="verbatim"))
    return out


def _doc(role, slot, frags, commit, extra=None, excluded=()):
    out = [HDR, f"role: {role}", f"slot: {slot}"]
    for k, v in (extra or {}).items():
        out.append(f"{k}: {v}")
    out.append("fragments:")
    for f in frags:
        out += fragment_lines(f, NAME, commit)
    if excluded:
        out += excluded_lines(excluded)
    return "\n".join(out) + "\n"


def extract(commit):
    files, failures = {}, []
    det = parse(read(NAME, DETECT, commit))
    title = next(b["text"] for b in det if b["kind"] == "heading")
    files["procedure/diagnose.yaml"] = _doc(
        "procedure", "diagnose", _frags("diagnose", DETECT, det, lambda b: b["kind"] != "heading"), commit,
        excluded=[(DETECT, "frontmatter", "name/description are ours (assemble/skills/ko-diagnose.md)"),
                  (DETECT, title, "title is ours")])
    tax = parse(read(NAME, TAX, commit))
    keep = lambda b: not (b["kind"] == "heading" and b["text"].startswith("# ")) and b["ctx"] != "## 목차" and b["text"] != "## 목차"
    tax_title = next(b["text"] for b in tax if b["kind"] == "heading" and b["text"].startswith("# "))
    files["taxonomy/diagnose.yaml"] = _doc(
        "taxonomy", "diagnose", _frags("diagnose", TAX, tax, keep), commit,
        excluded=[(TAX, tax_title, "title is ours"), (TAX, "## 목차", "navigation links into the upstream file")])
    for name, kind, path in REFS:
        bl = parse(read(NAME, path, commit))
        files[f"reference/diagnose/{name}.yaml"] = _doc(
            "reference", "diagnose", _frags(name, path, bl, lambda b: True), commit, extra={"name": name, "kind": kind})
    return files, failures
