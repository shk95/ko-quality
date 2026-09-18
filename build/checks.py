#!/usr/bin/env python3
"""09 §13 build checks over built dists. Run from the repository root:  python3 -m build.checks

  check 1  provenance: python3 -m upstream.extractors check (re-extraction), plus every sidecar recomputes (tests/check_provenance.py)
  check 2  policy identical: for each profile, the Claude Code output-style body equals the Codex AGENTS.md section body
           (frontmatter, markers and blank lines at the ends removed)
  check 3  agents identical: for each agent, the system prompt is the same string in every dist (the Claude Code plugin and
           every Codex profile dist), and it starts with the agent-reply policy body (S1-A)
  check 4  skills identical: skills/ trees are byte-identical across all dists
  check 5  agent names: no .claude/agents/*.md in this repository has a name that is in assemble/agents/ (E7-c)
  check 6  dependency boundary: no Python file under logger/, build/, upstream/, dist/ or hostguard/ imports outside the
           standard library; third-party imports are allowed only under measure/ (S3; hostguard/ added by era 98)
  check 7  host state: no file in the tip tree and no commit reachable from HEAD carries host state (era 98 spec §2.5)
"""
import ast
import filecmp
import importlib.util
import subprocess
import sys
import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build.mini_yaml import load as load_yaml  # noqa: E402

BOUNDARY = ("logger", "build", "upstream", "dist", "hostguard")


def body(path):
    text = path.read_text(encoding="utf-8")
    return text.split("---\n", 2)[2] if text.startswith("---\n") else text


def dists():
    """(label, plugin dir) for every dist that carries skills: the Claude Code plugin(s) and each Codex profile."""
    out = []
    for harness in ("claude-code", "agent-plugin"):
        base = ROOT / "dist" / harness
        if base.is_dir():
            out += [(f"{harness}/{p.name}", p) for p in sorted(base.iterdir()) if p.is_dir() and (p / "skills").is_dir()]
    return out


def cc_policy(pdir, profile):
    return body(pdir / "output-styles" / f"{profile}.md").strip("\n")


def codex_policy(pdir):
    section = (pdir / "install" / "AGENTS.section.md").read_text(encoding="utf-8")
    return "\n".join(l for l in section.split("\n") if not l.startswith("<!-- ko-quality")).strip("\n")


def agent_prompts(label, pdir):
    if label.startswith("claude-code/"):
        return {p.stem: body(p).strip("\n") for p in sorted((pdir / "agents").glob("*.md"))}
    from build.mini_toml import loads
    out = {}
    for p in sorted((pdir / "install" / ".codex" / "agents").glob("*.toml")):
        data = loads(p.read_text(encoding="utf-8"))
        out[data["name"]] = data["developer_instructions"].strip("\n")
    return out


def trees_equal(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False, cmp.left_only + cmp.right_only + cmp.diff_files
    shallow = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if shallow[1] or shallow[2]:
        return False, shallow[1] + shallow[2]
    for sub in cmp.common_dirs:
        ok, what = trees_equal(a / sub, b / sub)
        if not ok:
            return False, [f"{sub}/{w}" for w in what]
    return True, []


def frontmatter_name(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    for line in text.split("---\n", 2)[1].split("\n"):
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"\'')
    return None


def is_stdlib(name):
    if name in sys.builtin_module_names:
        return True
    names = getattr(sys, "stdlib_module_names", None)  # Python 3.10+
    if names is not None:
        return name in names
    spec = importlib.util.find_spec(name)
    if spec is None or spec.origin in (None, "built-in", "frozen"):
        return spec is not None
    stdlib = Path(sysconfig.get_paths()["stdlib"]).resolve()
    origin = Path(spec.origin).resolve()
    return stdlib in origin.parents and "site-packages" not in origin.parts


def local_modules(py):
    """Names importable from the file's own directory or the repository root (our code, not a dependency)."""
    names = set()
    for d in (py.parent, ROOT):
        names |= {p.stem for p in d.glob("*.py")} | {p.name for p in d.iterdir() if p.is_dir() and (p / "__init__.py").exists()}
    return names


def third_party_imports(py):
    tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods = [node.module]
        else:
            continue
        for m in mods:
            top = m.split(".")[0]
            if top not in local_modules(py) and not is_stdlib(top):
                found.append(f"{py.relative_to(ROOT)}:{node.lineno} {m}")
    return found


def main():
    all_dists = dists()
    failures = []
    # check 1
    r = subprocess.run([sys.executable, "-m", "upstream.extractors", "check"], cwd=ROOT, capture_output=True, text=True)
    print("check 1 re-extraction:", r.stdout.strip().splitlines()[-1])
    if r.returncode:
        failures.append("check 1: re-extraction")
    for label, pdir in all_dists:
        targets = [str(s.relative_to(ROOT)) for s in sorted((pdir / "skills").glob("*/"))]
        targets += [str(p.relative_to(ROOT)) for p in (pdir / "provenance").glob("*.yaml")]
        for t in targets:
            r = subprocess.run([sys.executable, "tests/check_provenance.py", t], cwd=ROOT, capture_output=True, text=True)
            if r.returncode:
                failures.append(f"check 1: sidecar {t}"); print(r.stdout)
    print(f"check 1 sidecars: {'ok' if not any('sidecar' in f for f in failures) else 'FAILED'}")
    # check 2
    cfg = load_yaml(ROOT / "assemble/build.yaml")
    cc = [(l, p) for l, p in all_dists if l.startswith("claude-code/")]
    codex = {l.split("/", 1)[1]: p for l, p in all_dists if l.startswith("agent-plugin/")}
    profiles = sorted(p.stem for p in (ROOT / "assemble/profiles").glob("*.yaml"))
    bodies = {}
    for prof in profiles:
        seen = {l: cc_policy(p, prof) for l, p in cc if (p / "output-styles" / f"{prof}.md").exists()}
        if prof in codex:
            seen[f"agent-plugin/{prof}"] = codex_policy(codex[prof])
        if not seen or len(set(seen.values())) > 1:
            failures.append(f"check 2: policy body for {prof} differs or is missing: {sorted(seen)}")
        bodies[prof] = next(iter(seen.values()), "")
        print(f"check 2 {prof}: compared {', '.join(sorted(seen))}")
    # check 3
    prompts = {l: agent_prompts(l, p) for l, p in all_dists}
    names = set().union(*[set(v) for v in prompts.values()])
    for name in sorted(names):
        vals = {l: v.get(name) for l, v in prompts.items()}
        if None in vals.values() or len(set(vals.values())) > 1:
            failures.append(f"check 3: agent {name} differs or is missing across {sorted(vals)}")
        elif not next(iter(vals.values())).startswith(bodies[cfg["agent_profile"]]):
            failures.append(f"check 3: agent {name} does not start with the {cfg['agent_profile']} policy body")
    print(f"check 3 agents: {len(names)} agents across {len(prompts)} dists")
    # check 4
    ref = all_dists[0]
    for label, d in all_dists[1:]:
        ok, what = trees_equal(ref[1] / "skills", d / "skills")
        if not ok:
            failures.append(f"check 4: skills differ between {ref[0]} and {label}: {what[:5]}")
    print(f"check 4 skills: compared {len(all_dists)} dists")
    # check 5
    shipped = {load_yaml(p)["name"] for p in (ROOT / "assemble/agents").glob("*.yaml")}
    dev_agents = sorted((ROOT / ".claude/agents").glob("*.md")) if (ROOT / ".claude/agents").is_dir() else []
    for p in dev_agents:
        if frontmatter_name(p) in shipped:
            failures.append(f"check 5: {p.relative_to(ROOT)} uses the shipped agent name {frontmatter_name(p)}")
    print(f"check 5 agent names: {len(dev_agents)} repository agents against {len(shipped)} shipped names")
    # check 6
    pys = [f for top in BOUNDARY if (ROOT / top).is_dir() for f in sorted((ROOT / top).rglob("*.py"))
           if ".cache" not in f.parts and "__pycache__" not in f.parts]
    bad = [hit for f in pys for hit in third_party_imports(f)]
    failures += [f"check 6: third-party import {b}" for b in bad]
    print(f"check 6 dependency boundary: {len(pys)} files under {', '.join(BOUNDARY)}, {len(bad)} third-party imports")
    # check 7
    from hostguard import scan  # noqa: E402
    hits = list(dict.fromkeys(scan.Scanner(ROOT).history("HEAD")))
    for path, n, rule, excerpt in hits:
        failures.append(f"check 7: {path}:{n}: {rule}: {excerpt}")
    print(f"check 7 host state: tip and history of HEAD, {len(hits)} hits")
    for f in failures:
        print("FAIL", f)
    print(f"checks: {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
