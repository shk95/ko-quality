#!/usr/bin/env python3
"""Build dist/agent-plugin/<profile>/ for Codex (Agent Plugins) from upstream/normalized/ and assemble/ (09 §13).

Run from the repository root:  python3 -m build.agent_plugin

Per profile:
  plugin.json                          Agent Plugins manifest (skills; hooks under extensions.com.openai)
  hooks/, logger/, ko-quality.stamp.json  minimal logger and its build stamp (P7), shared with Claude Code
  skills/                              rendered from the same templates as Claude Code (06 §12 check 4: byte-identical)
  install/AGENTS.section.md            the profile's policy body between ko-quality markers, for AGENTS.md
  install/.codex/agents/<name>.toml    agents with developer_instructions = agent-reply policy + append, in every profile (S1-A, check 3)
  install/ko_quality_codex.py          idempotent install/uninstall of the section and agent files
  provenance/policy.yaml               provenance for AGENTS.section.md and the agent prompts
dist/agent-plugin/.agents/plugins/marketplace.json lists every profile plugin; README.md is the install doc.
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build.claude_code import Out, config, render_policy, render_skills, ship_logger, sidecar, stamp  # noqa: E402
from build.mini_toml import dumps as toml_dumps  # noqa: E402
from build.mini_yaml import load as load_yaml  # noqa: E402

ASM, DIST = ROOT / "assemble", ROOT / "dist/agent-plugin"
BEGIN = "<!-- ko-quality:begin profile={profile} -->"
END = "<!-- ko-quality:end -->"


def policy_out(profile):
    out = Out()
    render_policy(out, profile, f"assemble/profiles/{profile['id']}.yaml")
    # drop the leading blank lines the output-style layout starts with; AGENTS.md sections start at their first line
    while out.lines and out.lines[0] == "":
        out.lines.pop(0)
        for s in out.spans:
            s["lines"] = [s["lines"][0] - 1, s["lines"][1] - 1]
    return out


def agents_section(profile):
    body = policy_out(profile)
    out = Out()
    out.literal(BEGIN.format(profile=profile["id"]), "build/agent_plugin.py (marker)")
    offset = len(out.lines)
    out.lines.extend(body.lines)
    for s in body.spans:
        s = dict(s); s["lines"] = [s["lines"][0] + offset, s["lines"][1] + offset]; out.spans.append(s)
    out.literal(END, "build/agent_plugin.py (marker)")
    return out


def agent_prompt(defn, profile, name):
    out = policy_out(profile)
    if defn["prompt"].get("append"):
        out.blank(); out.literal(defn["prompt"]["append"], f"assemble/agents/{name}.yaml")
    return out


def build():
    cfg = config()
    presets = load_yaml(ASM / "presets.yaml")
    profiles = [load_yaml(p) for p in sorted((ASM / "profiles").glob("*.yaml"))]
    agent_profile = next(p for p in profiles if p["id"] == cfg["agent_profile"])
    agents = {p.stem: load_yaml(p) for p in sorted((ASM / "agents").glob("*.yaml"))}
    ctx = dict(presets=presets, profiles=profiles)
    if DIST.exists():
        shutil.rmtree(DIST)
    market = {"name": "ko-quality", "interface": {"displayName": "ko-quality"}, "plugins": []}
    for profile in profiles:
        plugin = cfg["agent_plugin"][profile["id"]]
        pdir = DIST / profile["id"]
        pdir.mkdir(parents=True)
        manifest = {"name": plugin["name"], "version": cfg["version"], "description": plugin["description"],
                    "author": {"name": "ko-quality"}, "license": "MIT", "skills": "./skills/",
                    "extensions": {"com.openai": {"hooks": "./hooks/hooks.json"}}}
        (pdir / "plugin.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        market["plugins"].append({"name": plugin["name"], "source": {"source": "local", "path": f"./{profile['id']}"},
                                  "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"})
        render_skills(pdir, ctx)
        inst = pdir / "install"
        (inst / ".codex" / "agents").mkdir(parents=True)
        pol = []
        sec = agents_section(profile)
        (inst / "AGENTS.section.md").write_text(sec.text(), encoding="utf-8"); pol.append(("install/AGENTS.section.md", sec))
        for name, defn in agents.items():
            o = agent_prompt(defn, agent_profile, name)
            rel = f"install/.codex/agents/{defn['name']}.toml"
            (pdir / rel).write_text(toml_dumps({"name": defn["name"], "description": defn["description"],
                                                "developer_instructions": o.text()}), encoding="utf-8")
            pol.append((rel + "#developer_instructions", o))
        shutil.copyfile(ROOT / "build/ko_quality_codex.py", inst / "ko_quality_codex.py")
        (pdir / "provenance").mkdir()
        (pdir / "provenance/policy.yaml").write_text(sidecar(
            "# Provenance for AGENTS.section.md and agent developer_instructions (flow.md D3). Built by build/agent_plugin.py; do not edit.\n"
            "# A path ending in #developer_instructions counts lines inside that TOML string.",
            pol, base=f"dist/agent-plugin/{profile['id']}"), encoding="utf-8")
        # Codex keeps profile in the stamp: one dist per profile, so it is a property of the installation there (09 §13 drops it for Claude Code only)
        ship_logger(pdir, stamp(plugin["name"], "codex", {"profile": profile["id"]}))
        print(f"built dist/agent-plugin/{profile['id']} ({plugin['name']})")
    (DIST / ".agents" / "plugins").mkdir(parents=True)
    (DIST / ".agents/plugins/marketplace.json").write_text(json.dumps(market, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if (ASM / "install/agent-plugin.md").exists():
        shutil.copyfile(ASM / "install/agent-plugin.md", DIST / "README.md")
    print("built dist/agent-plugin/.agents/plugins/marketplace.json")


if __name__ == "__main__":
    build()
