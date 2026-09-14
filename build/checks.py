#!/usr/bin/env python3
"""06 §12 build checks 2-4 over built dists. Run from the repository root:  python3 -m build.checks

  check 1  provenance: python3 -m upstream.extractors check (re-extraction), plus every sidecar recomputes (tests/check_provenance.py)
  check 2  policy identical: for each profile, the policy body (output style or AGENTS.md section, frontmatter and wrapping
           markers removed) is the same string in every harness dist, and every agent of that profile starts with it
  check 3  agents identical: for each profile and agent, the system prompt is the same string in every harness dist
  check 4  skills identical: skills/ trees are byte-identical across all dists (profiles and harnesses)

Harness dists present are discovered: dist/claude-code/<profile>/ now; dist/agent-plugin/<profile>/ from P6.
With one harness, checks 2 and 3 compare within that harness only and say so.
"""
import filecmp
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def body(path):
    text = path.read_text(encoding="utf-8")
    return text.split("---\n", 2)[2] if text.startswith("---\n") else text


def harness_dists():
    out = {}
    for harness in ("claude-code", "agent-plugin"):
        base = ROOT / "dist" / harness
        if base.is_dir():
            out[harness] = {p.name: p for p in sorted(base.iterdir()) if p.is_dir() and (p / "skills").is_dir()}
    return out


def policy_body(harness, pdir):
    if harness == "claude-code":
        return body(next((pdir / "output-styles").glob("*.md"))).rstrip("\n")
    section = (pdir / "install" / "AGENTS.section.md").read_text(encoding="utf-8")
    lines = [l for l in section.split("\n") if not l.startswith("<!-- ko-quality")]
    return "\n".join(lines).strip("\n")


def agent_prompts(harness, pdir):
    if harness == "claude-code":
        return {p.stem: body(p).rstrip("\n") for p in sorted((pdir / "agents").glob("*.md"))}
    from build.mini_toml import loads
    out = {}
    for p in sorted((pdir / "install" / ".codex" / "agents").glob("*.toml")):
        data = loads(p.read_text(encoding="utf-8"))
        out[data["name"]] = data["developer_instructions"].rstrip("\n")
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


def main():
    dists = harness_dists()
    failures = []
    # check 1
    r = subprocess.run([sys.executable, "-m", "upstream.extractors", "check"], cwd=ROOT, capture_output=True, text=True)
    print("check 1 re-extraction:", r.stdout.strip().splitlines()[-1])
    if r.returncode:
        failures.append("check 1: re-extraction")
    for harness, profiles in dists.items():
        for prof, pdir in profiles.items():
            targets = [str(s.relative_to(ROOT)) for s in sorted((pdir / "skills").glob("*/"))]
            targets += [str(p.relative_to(ROOT)) for p in (pdir / "provenance").glob("*.yaml")]
            for t in targets:
                r = subprocess.run([sys.executable, "tests/check_provenance.py", t], cwd=ROOT, capture_output=True, text=True)
                if r.returncode:
                    failures.append(f"check 1: sidecar {t}"); print(r.stdout)
    print(f"check 1 sidecars: {'ok' if not any('sidecar' in f for f in failures) else 'FAILED'}")
    # check 2 and 3
    profiles = sorted({p for d in dists.values() for p in d})
    harnesses = sorted(dists)
    for prof in profiles:
        bodies = {h: policy_body(h, dists[h][prof]) for h in harnesses if prof in dists[h]}
        if len(set(bodies.values())) > 1:
            failures.append(f"check 2: policy body differs across harnesses for {prof}")
        prompts = {h: agent_prompts(h, dists[h][prof]) for h in bodies}
        for h, ps in prompts.items():
            for name, prompt in ps.items():
                if not prompt.startswith(bodies[h]):
                    failures.append(f"check 2: {h}/{prof} agent {name} does not start with the policy body")
        names = set().union(*[set(p) for p in prompts.values()])
        for name in sorted(names):
            vals = {h: prompts[h].get(name) for h in prompts}
            if None in vals.values() or len(set(vals.values())) > 1:
                failures.append(f"check 3: agent {name} differs or is missing across harnesses for {prof}")
        scope = "across " + ", ".join(bodies) if len(bodies) > 1 else f"within {next(iter(bodies))} only"
        print(f"check 2/3 {prof}: {scope}")
    # check 4
    all_dirs = [(h, p, d) for h, ps in dists.items() for p, d in ps.items()]
    ref = all_dirs[0]
    for h, p, d in all_dirs[1:]:
        ok, what = trees_equal(ref[2] / "skills", d / "skills")
        if not ok:
            failures.append(f"check 4: skills differ between {ref[0]}/{ref[1]} and {h}/{p}: {what[:5]}")
    print(f"check 4 skills: compared {len(all_dirs)} dists")
    for f in failures:
        print("FAIL", f)
    print(f"checks: {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
