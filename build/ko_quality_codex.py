#!/usr/bin/env python3
"""Install or remove ko-quality's Codex pieces that a plugin cannot carry (06 §12, P6): the policy section in AGENTS.md
and the agent files. Idempotent. Copied into dist/agent-plugin/<profile>/install/ by the build; run it from there.

  python3 ko_quality_codex.py install   [--scope global|project] [--project DIR] [--codex-home DIR]
  python3 ko_quality_codex.py uninstall [--scope global|project] [--project DIR] [--codex-home DIR]
  python3 ko_quality_codex.py status    [--scope global|project] [--project DIR] [--codex-home DIR]

global  : $CODEX_HOME/AGENTS.md and $CODEX_HOME/agents/ (CODEX_HOME defaults to ~/.codex)
project : DIR/AGENTS.md and DIR/.codex/agents/

The section sits between `<!-- ko-quality:begin ... -->` and `<!-- ko-quality:end -->`. Installing replaces an existing
ko-quality section (any profile) in place, or appends one. Agent files are recorded in `.ko-quality-install.json` next to
AGENTS.md so that uninstall removes exactly what install wrote; an existing agent file with the same name that ko-quality
did not write is never overwritten.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTION = re.compile(r"\n*<!-- ko-quality:begin[^\n]*-->\n.*?<!-- ko-quality:end -->\n?", re.S)


def targets(args):
    if args.scope == "global":
        home = Path(args.codex_home or os.environ.get("CODEX_HOME") or Path.home() / ".codex")
        return home / "AGENTS.md", home / "agents", home / ".ko-quality-install.json"
    root = Path(args.project or os.getcwd())
    return root / "AGENTS.md", root / ".codex" / "agents", root / ".codex" / ".ko-quality-install.json"


def read_manifest(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"agents": [], "created_agents_md": False}


def install(args):
    agents_md, agents_dir, manifest_path = targets(args)
    section = (HERE / "AGENTS.section.md").read_text(encoding="utf-8")
    manifest = read_manifest(manifest_path)
    if agents_md.exists():
        text = agents_md.read_text(encoding="utf-8")
        if SECTION.search(text):
            text = SECTION.sub(lambda m: ("\n\n" if m.start() > 0 else "") + section, text, count=1)
        else:
            text = text.rstrip("\n") + ("\n\n" if text.strip() else "") + section
    else:
        agents_md.parent.mkdir(parents=True, exist_ok=True)
        text = section
        manifest["created_agents_md"] = True
    agents_md.write_text(text, encoding="utf-8")
    agents_dir.mkdir(parents=True, exist_ok=True)
    written = set(manifest["agents"])
    for src in sorted((HERE / ".codex" / "agents").glob("*.toml")):
        dst = agents_dir / src.name
        if dst.exists() and src.name not in written and dst.read_bytes() != src.read_bytes():
            print(f"skip {dst}: exists and was not written by ko-quality", file=sys.stderr)
            continue
        dst.write_bytes(src.read_bytes())
        written.add(src.name)
    manifest["agents"] = sorted(written)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"installed: {agents_md} (section), {len(written)} agent files in {agents_dir}")


def uninstall(args):
    agents_md, agents_dir, manifest_path = targets(args)
    manifest = read_manifest(manifest_path)
    if agents_md.exists():
        text = SECTION.sub("", agents_md.read_text(encoding="utf-8"))
        text = text.rstrip("\n") + "\n" if text.strip() else ""
        if not text and manifest.get("created_agents_md"):
            agents_md.unlink()
        else:
            agents_md.write_text(text, encoding="utf-8")
    for name in manifest["agents"]:
        f = agents_dir / name
        if f.exists():
            f.unlink()
    if agents_dir.exists() and not any(agents_dir.iterdir()):
        agents_dir.rmdir()
    if manifest_path.exists():
        manifest_path.unlink()
    print(f"uninstalled: section removed from {agents_md}, {len(manifest['agents'])} agent files removed")


def status(args):
    agents_md, agents_dir, manifest_path = targets(args)
    text = agents_md.read_text(encoding="utf-8") if agents_md.exists() else ""
    m = re.search(r"<!-- ko-quality:begin profile=(\S+) -->", text)
    manifest = read_manifest(manifest_path)
    print(json.dumps({"agents_md": str(agents_md), "section_profile": m.group(1) if m else None,
                      "agents": [n for n in manifest["agents"] if (agents_dir / n).exists()]}, indent=2))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["install", "uninstall", "status"])
    ap.add_argument("--scope", choices=["global", "project"], default="global")
    ap.add_argument("--project")
    ap.add_argument("--codex-home")
    args = ap.parse_args(argv)
    {"install": install, "uninstall": uninstall, "status": status}[args.command](args)


if __name__ == "__main__":
    main()
