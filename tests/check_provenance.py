#!/usr/bin/env python3
"""Recompute provenance for a hand-built skill (P1-P3, flow.md D3). Temporary until P4's extractors.

For every upstream span in SKILL.provenance.yaml:
  1. the fragment in upstream/normalized/<role>/<slot>.yaml hashes to its content_hash;
  2. the rendered span (minus prefix) equals the fragment text (quick-line spans: re-rendered from the fragment);
  3. the fragment text is present in the upstream file at the lock commit
     (selected fragments: each line is a substring of the file).
Exit 1 on any mismatch. Usage: tests/check_provenance.py dist/claude-code/skills/<skill> | dist/claude-code/provenance/<name>.yaml
"""
import glob, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def sha(s): return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_fragments(ref):
    # ref is the path under upstream/normalized without .yaml: procedure/rewrite, reference/diagnose/lread-rubric
    text = (ROOT / "upstream/normalized" / f"{ref}.yaml").read_text(encoding="utf-8")
    frags = {}
    for block in text.split("\n  - id: ")[1:]:
        fid = block.split("\n")[0].strip()
        get = lambda k: re.search(rf"^\s+{k}: (.*)$", block, re.M).group(1)
        frags[fid] = dict(text=json.loads(get("text")), path=get("path"), commit=get("commit"),
                          hash=get("content_hash"), transform=get("transform"))
    return frags

def parse_sidecar(path):
    files, cur, span = {}, None, None
    for line in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r"^  (\S.*):$", line)
        if m: cur = files.setdefault(m.group(1), []); continue
        m = re.match(r"^    - lines: \[(\d+), (\d+)\]$", line)
        if m: span = dict(lines=(int(m.group(1)), int(m.group(2)))); cur.append(span); continue
        m = re.match(r"^      (\w+): (.*)$", line)
        if m and span is not None: span[m.group(1)] = json.loads(m.group(2))
    return files

PAT = re.compile(r"^#+ ([A-J]-\d+)\.\s+(.+?)\s*(?:\[([^\]]+)\])?\s*$")
QM = re.compile(r"_quick:\s*(true|false)(?:\s*·\s*quick_pattern:\s*(.*?))?(?:\s*·\s*quick_fix:\s*(.*?))?_\s*$")

def main(target):
    # target: a skill directory (reads SKILL.provenance.yaml) or a sidecar .yaml with a `base:` line
    target = ROOT / target
    if target.suffix == ".yaml":
        sidecar = target
        base = ROOT / re.search(r"^base: (.*)$", target.read_text(encoding="utf-8"), re.M).group(1)
    else:
        sidecar, base = target / "SKILL.provenance.yaml", target
    errors, checked = [], 0
    cache = {}
    for rel, spans in parse_sidecar(sidecar).items():
        rendered = (base / rel).read_text(encoding="utf-8").split("\n")
        for s in spans:
            if s["owner"] != "upstream": continue
            checked += 1
            ref, fid = s["fragment"].split("#")
            f = cache.setdefault(ref, load_fragments(ref))[fid]
            where = f"{rel}:{s['lines'][0]} {s['fragment']}"
            if sha(f["text"]) != f["hash"] or f["hash"] != s["content_hash"]:
                errors.append(f"hash differs: {where}")
            got = "\n".join(rendered[s["lines"][0] - 1:s["lines"][1]])
            if "render" in s:
                h, m = f["text"].split("\n"); pm, mm = PAT.match(h), QM.search(m)
                sev = f" [{pm.group(3).strip()}]" if pm.group(3) else ""
                want = f"- **{pm.group(1)}**{sev} {mm.group(2).strip()} → {mm.group(3).strip()}"
            else:
                want = s.get("prefix", "") + f["text"]
            if got != want:
                errors.append(f"render differs: {where}")
            up = glob.glob(str(ROOT / f"upstream/.cache/*@{f['commit']}"))[0]
            src = (Path(up) / f["path"]).read_text(encoding="utf-8")
            if not all(line in src for line in f["text"].split("\n")):
                errors.append(f"anchor text not found upstream: {where}")
    for e in errors: print(e)
    print(f"{checked} upstream spans checked, {len(errors)} errors")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
