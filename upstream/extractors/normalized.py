"""Write and read the normalized YAML files (temporary format from P1-P3, described by upstream/interface/*.schema.yaml).

Text values are JSON strings (valid YAML, exact bytes). The reader only understands files this module writes."""
import hashlib
import json
import re


def sha(text):
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def q(value):
    return json.dumps(value, ensure_ascii=False)


def fragment_lines(f, upstream, commit):
    out = [f"  - id: {f['id']}", f"    kind: {f['kind']}"]
    if f.get("blanks") is not None:
        out.append(f"    blanks: {f['blanks']}")
    out += [f"    text: {q(f['text'])}",
           "    provenance:", f"      upstream: {upstream}", f"      commit: {commit}", f"      path: {f['path']}",
           f"      anchor: {q(f['anchor'])}", f"      content_hash: {sha(f['text'])}", f"      transform: {f['transform']}"]
    if f.get("original") is not None:
        out.append(f"      original: {q(f['original'])}")
    if f.get("note"):
        out.append(f"      note: {q(f['note'])}")
    return out


def excluded_lines(excluded):
    out = ["excluded:"]
    for path, anchor, reason in excluded:
        out += [f"  - path: {path}", f"    anchor: {q(anchor)}", f"    reason: {q(reason)}"]
    return out


def load(text):
    """Top-level scalar fields and fragments of a normalized file."""
    head = text.split("\nfragments:\n")[0]
    top = dict(re.findall(r"^(\w+): (.*)$", head, re.M))
    body = text.split("\nfragments:\n", 1)[1] if "\nfragments:\n" in text else ""
    body = body.split("\nexcluded:\n")[0]
    frags = []
    for block in ("\n" + body).split("\n  - id: ")[1:]:
        fid = block.split("\n")[0].strip()
        fields = dict(re.findall(r"^\s+(\w+): (.*)$", block, re.M))
        frag = {"id": fid}
        for k, v in fields.items():
            frag[k] = json.loads(v) if k in ("text", "anchor", "original", "note") else v
        frags.append(frag)
    return top, frags
