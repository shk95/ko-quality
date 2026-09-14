#!/usr/bin/env python3
"""Build dist/claude-code/<profile>/ from upstream/normalized/ and assemble/ (06 §12; decision ②: build-time profile).

Run from the repository root:  python3 -m build.claude_code

Template directives (a line starting with @ in assemble/skills/<skill>/**/*.md; @@ escapes a literal @):
  @frag <ref>#<id> [prefix="…"]                         one fragment
  @blocks <ref> [select=[…]] [ids="glob"] [blanks=single|exact] [headings=anchor]
                                                         fragments of a whole-file extraction in file order;
                                                         select = anchor-context prefixes; blanks from the fragment
  @quick-rules <ref>                                     categories and pattern lines (upstream build_quick_rules format)
  @presets                                               presets and profile defaults from assemble/ (ours)
All other lines are ours. Every file gets provenance: skills in SKILL.provenance.yaml, the rest in provenance/policy.yaml.
"""
import fnmatch
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build.mini_yaml import load as load_yaml  # noqa: E402
from upstream.extractors.normalized import load as load_norm, sha  # noqa: E402

NORM, ASM, DIST = ROOT / "upstream/normalized", ROOT / "assemble", ROOT / "dist/claude-code"
_cache = {}


def norm(ref):
    if ref not in _cache:
        text = (NORM / f"{ref}.yaml").read_text(encoding="utf-8")
        top, frags = load_norm(text)
        _cache[ref] = dict(top=top, frags=frags, by_id={f["id"]: f for f in frags}, text=text)
    return _cache[ref]


def policy_data(ref, variant):
    text = norm(ref)["text"]
    m = re.search(rf"^  {re.escape(variant)}:\n    path: .*\n    frontmatter:\n((?:      .*\n)*)", text, re.M)
    return {k: json.loads(v) for k, v in re.findall(r"^      ([\w-]+): (.*)$", m.group(1), re.M)}


class Out:
    def __init__(self):
        self.lines, self.spans = [], []

    def literal(self, line, source):
        self.lines.append(line)
        if line.strip():
            last = self.spans[-1] if self.spans else None
            if last and last["owner"] == "ours" and last["source"] == source and last["lines"][1] == len(self.lines) - 1:
                last["lines"][1] = len(self.lines)
            else:
                self.spans.append(dict(lines=[len(self.lines), len(self.lines)], owner="ours", source=source))

    def blank(self, n=1):
        self.lines.extend([""] * n)

    def frag(self, ref, f, prefix=""):
        start = len(self.lines) + 1
        t = f["text"].split("\n")
        self.lines.append(prefix + t[0]); self.lines.extend(t[1:])
        span = dict(lines=[start, len(self.lines)], owner="upstream", fragment=f"{ref}#{f['id']}")
        if prefix:
            span["prefix"] = prefix
        span.update(content_hash=f["content_hash"], transform=f["transform"])
        self.spans.append(span)

    def structure(self, line, source):
        self.lines.append(line)
        self.spans.append(dict(lines=[len(self.lines), len(self.lines)], owner="structure", source=source))

    def text(self):
        return "\n".join(self.lines) + "\n"


PAT = re.compile(r"^#+ ([A-J]-\d+)\.\s+(.+?)\s*(?:\[([^\]]+)\])?\s*$")
QM = re.compile(r"_quick:\s*(true|false)(?:\s*·\s*quick_pattern:\s*(.*?))?(?:\s*·\s*quick_fix:\s*(.*?))?_\s*$")


def args_of(rest):
    out, pos = {}, []
    for k, v, p in re.findall(r'(\w+)=(\[[^\]]*\]|"(?:[^"\\]|\\.)*"|\S+)|(\S+)', rest):
        if p:
            pos.append(p)
        else:
            out[k] = json.loads(v) if v[0] in '["' else v
    return pos, out


def directive(out, line, src, ctx):
    name, _, rest = line[1:].partition(" ")
    pos, kw = args_of(rest)
    if name == "frag":
        ref, fid = pos[0].split("#")
        out.frag(ref, norm(ref)["by_id"][fid], kw.get("prefix", ""))
    elif name == "blocks":
        ref = pos[0]
        blanks, first, prev = kw.get("blanks", "single"), True, None
        for f in norm(ref)["frags"]:
            c = f["anchor"].split(" > ")[0]
            if "select" in kw and not any(c == s or c.startswith(s) for s in kw["select"]):
                continue
            if "ids" in kw and not fnmatch.fnmatch(f["id"], kw["ids"]):
                continue
            b = int(f.get("blanks", 0))
            if kw.get("headings") == "anchor" and c != prev and f["kind"] != "heading" and c.startswith("#"):
                if not first:
                    out.blank()
                out.structure(c, f"heading from the anchor context of {ref}")
                out.blank(); first, prev, b = False, c, 0
            if blanks == "exact":
                out.blank(b)
            elif b and not first:
                out.blank()
            out.frag(ref, f)
            first, prev = False, c
    elif name == "quick-rules":
        ref = pos[0]; d = norm(ref); cur = None
        for f in d["frags"]:
            if f["kind"] != "pattern":
                continue
            letter = f["id"].split(".", 1)[1][0]
            if letter != cur:
                if cur:
                    out.blank()
                cur = letter; out.frag(ref, d["by_id"][f"category.{letter}"]); out.blank()
            h, m = f["text"].split("\n"); pm, mm = PAT.match(h), QM.search(m)
            sev = f" [{pm.group(3).strip()}]" if pm.group(3) else ""
            out.lines.append(f"- **{pm.group(1)}**{sev} {mm.group(2).strip()} → {mm.group(3).strip()}")
            out.spans.append(dict(lines=[len(out.lines), len(out.lines)], owner="upstream", fragment=f"{ref}#{f['id']}",
                                  render="quick-line: - **id** [severity] quick_pattern → quick_fix (upstream build_quick_rules.py format)",
                                  content_hash=f["content_hash"], transform=f["transform"]))
    elif name == "presets":
        presets, profiles = ctx["presets"], ctx["profiles"]
        for pname, steps in presets["presets"].items():
            run = [presets["steps"][s] for s in steps if presets["steps"].get(s)]
            note = " (the policy is already active)" if "policy" in steps else ""
            body = ", then ".join(f"`{r}`" for r in run) if run else "nothing to run"
            out.literal(f"- `{pname}`: {body}{note}", "assemble/presets.yaml")
        out.blank()
        for p in profiles:
            out.literal(f"- Plugin `{p['plugin']['name']}` is profile `{p['id']}` ({p['register']}); its default preset is `{p['default_preset']}`.", f"assemble/profiles/{p['id']}.yaml")
    else:
        raise SystemExit(f"{src}: unknown directive @{name}")


def render_template(path, ctx):
    src = str(path.relative_to(ROOT))
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")[:-1] if text.endswith("\n") else text.split("\n")
    out = Out()
    for line in lines:
        if line.startswith("@@"):
            out.literal(line[1:], src)
        elif line.startswith("@"):
            directive(out, line, src, ctx)
        elif line.strip():
            out.literal(line, src)
        else:
            out.blank()
    return out


def render_policy(out, profile, source):
    ref, variant = profile["policy"].split("#")
    for f in norm(ref)["frags"]:
        if f["id"].startswith(variant + "."):
            out.blank(int(f.get("blanks", 0)))
            out.frag(ref, f)
    for bid in profile["blocks"]:
        out.blank(); out.frag(ref, norm(ref)["by_id"][f"block.{bid}"])


def output_style(profile):
    ref, variant = profile["policy"].split("#")
    fm = policy_data(ref, variant)
    src = f"assemble/profiles/{profile['id']}.yaml"
    out = Out()
    head = ["---", f"name: {profile['output_style']['name']}", f"description: {profile['output_style']['description']}"]
    if "keep-coding-instructions" in fm:
        head.append(f"keep-coding-instructions: {fm['keep-coding-instructions']}")
    if profile["output_style"].get("force"):
        head.append("force-for-plugin: true")
    head.append("---")
    for l in head:
        out.literal(l, src + " (frontmatter)")
    render_policy(out, profile, src)
    return out


def agent(defn, profile, name):
    src = f"assemble/agents/{name}.yaml"
    out = Out()
    for l in ["---", f"name: {defn['name']}", f"description: {defn['description']}", f"tools: {', '.join(defn['tools'])}", "---"]:
        out.literal(l, src + " (frontmatter)")
    render_policy(out, profile, f"assemble/profiles/{profile['id']}.yaml")
    if defn["prompt"].get("append"):
        out.blank(); out.literal(defn["prompt"]["append"], src)
    return out


def span_yaml(spans, indent):
    pad, out = " " * indent, []
    for s in spans:
        out.append(f"{pad}- lines: [{s['lines'][0]}, {s['lines'][1]}]")
        for k in ("owner", "source", "fragment", "prefix", "render", "content_hash", "transform"):
            if k in s:
                out.append(f"{pad}  {k}: {json.dumps(s[k], ensure_ascii=False)}")
    return out


def upstreams(files):
    names = set()
    for _, o in files:
        for s in o.spans:
            if s["owner"] == "upstream":
                ref = s["fragment"].split("#")[0]
                f = norm(ref)["by_id"][s["fragment"].split("#")[1]]
                names.add((f["upstream"], f["commit"]))
    return sorted(names)


def sidecar(header, files, base=None):
    lines = [header]
    if base:
        lines.append(f"base: {base}")
    for name, commit in upstreams(files):
        lines.append(f"upstream: {name}"); lines.append(f"commit: {commit}")
    lines.append("files:")
    for rel, o in files:
        lines.append(f"  {rel}:"); lines += span_yaml(o.spans, 4)
    return "\n".join(lines) + "\n"


def build():
    presets = load_yaml(ASM / "presets.yaml")
    profiles = [load_yaml(p) for p in sorted((ASM / "profiles").glob("*.yaml"))]
    agents = {p.stem: load_yaml(p) for p in sorted((ASM / "agents").glob("*.yaml"))}
    ctx = dict(presets=presets, profiles=profiles)
    if DIST.exists():
        shutil.rmtree(DIST)
    market = {"name": "ko-quality", "owner": {"name": "ko-quality"}, "plugins": []}
    for profile in profiles:
        pdir = DIST / profile["id"]
        (pdir / ".claude-plugin").mkdir(parents=True)
        (pdir / ".claude-plugin/plugin.json").write_text(json.dumps({
            "name": profile["plugin"]["name"], "version": "0.1.0", "description": profile["plugin"]["description"],
            "author": {"name": "ko-quality"}, "license": "MIT"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        market["plugins"].append({"name": profile["plugin"]["name"], "source": f"./{profile['id']}",
                                  "description": profile["plugin"]["description"]})
        for sdir in sorted((ASM / "skills").iterdir()):
            if not sdir.is_dir():
                continue
            files = []
            for tpl in sorted(sdir.rglob("*.md")):
                rel = str(tpl.relative_to(sdir))
                o = render_template(tpl, ctx)
                target = pdir / "skills" / sdir.name / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(o.text(), encoding="utf-8")
                files.append((rel, o))
            files.sort(key=lambda x: (x[0] != "SKILL.md", x[0]))
            (pdir / "skills" / sdir.name / "SKILL.provenance.yaml").write_text(sidecar(
                "# Which spans are upstream, structure or ours (flow.md D3). Built by build/claude_code.py; do not edit.",
                files).replace("files:\n", f"skill: {sdir.name}\nfiles:\n", 1), encoding="utf-8")
        pol = []
        o = output_style(profile)
        rel = f"output-styles/{profile['output_style']['name']}.md"
        (pdir / "output-styles").mkdir(); (pdir / rel).write_text(o.text(), encoding="utf-8"); pol.append((rel, o))
        (pdir / "agents").mkdir()
        for name, defn in agents.items():
            o = agent(defn, profile, name)
            rel = f"agents/{defn['name']}.md"
            (pdir / rel).write_text(o.text(), encoding="utf-8"); pol.append((rel, o))
        (pdir / "provenance").mkdir()
        (pdir / "provenance/policy.yaml").write_text(sidecar(
            "# Provenance for plugin files outside skills/ (flow.md D3). Built by build/claude_code.py; do not edit.",
            pol, base=f"dist/claude-code/{profile['id']}"), encoding="utf-8")
        print(f"built dist/claude-code/{profile['id']} ({profile['plugin']['name']})")
    (DIST / ".claude-plugin").mkdir()
    (DIST / ".claude-plugin/marketplace.json").write_text(json.dumps(market, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("built dist/claude-code/.claude-plugin/marketplace.json")


if __name__ == "__main__":
    build()
