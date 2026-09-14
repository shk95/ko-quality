# P6 — Codex build

2026-09-14. Branch `dev`. Flow: `5-preflight/flow.md` §3 P6.

## Result

`python3 -m build.agent_plugin` builds `dist/agent-plugin/{agent-reply,formal-report}/` from the same `normalized/` and `assemble/` inputs as P5. The Codex plugin installs from a local marketplace, and a skill runs under `codex exec`. `python3 -m build.checks` runs 06 §12 checks 1–4 across both harnesses and all four dists with 0 failures. _Channel, custom-agent and hook results: pending._

| Artifact | Path |
|---|---|
| Build | `build/agent_plugin.py` (reuses the Claude Code renderer), `build/mini_toml.py` |
| Installer | `build/ko_quality_codex.py` → `dist/agent-plugin/<profile>/install/ko_quality_codex.py` — `install`, `uninstall`, `status`; `--scope global` (`$CODEX_HOME/AGENTS.md`, `$CODEX_HOME/agents/`) or `--scope project` |
| Output per profile | `plugin.json` (root, `skills: ./skills/`), `skills/` (byte-identical to Claude Code), `install/AGENTS.section.md` (policy between `<!-- ko-quality:begin profile=… -->` and `<!-- ko-quality:end -->`), `install/.codex/agents/korean-{reviewer,writer,editor}.toml`, `provenance/policy.yaml` |
| Marketplace | `dist/agent-plugin/.agents/plugins/marketplace.json` |
| Run logs | `tests/runs/P6/` |

## Checks

| Check | Result |
|---|---|
| 06 §12 check 1 | re-extraction 0 failures; all sidecars recompute, including spans inside the TOML `developer_instructions` strings (76 and 72 upstream spans) |
| Check 2 (policy identical) | Claude Code output-style body = AGENTS.md section body (markers removed) for both profiles; every agent in both harnesses starts with it |
| Check 3 (agents identical) | all 6 agent prompts identical across harnesses |
| Check 4 (skills identical) | `skills/` byte-identical in all 4 dists |
| Installer | In throwaway directories: install twice → one section; second profile replaces the first in place; uninstall restores a pre-existing AGENTS.md byte for byte; an agent file not written by ko-quality is never overwritten; an AGENTS.md created by install is removed by uninstall |
| Plugin install | Throwaway `CODEX_HOME` (auth symlinked): `codex plugin marketplace add dist/agent-plugin` → `codex plugin add ko-quality@ko-quality`: root `plugin.json` accepted, installed as version `local` |
| Skill under `codex exec` | `$ko-rewrite` read the installed SKILL.md and produced the rewrite report (`tests/runs/P6/skill-install.json`) |

## Spec did not know

- **Check 2 needed a normalization.** The Claude Code output-style body begins with the blank line that follows its frontmatter; the AGENTS.md section does not. Blank lines at either end are layout, so checks 2 and 3 compare bodies with them trimmed (06 §12 already excludes frontmatter and wrapping markers).
- **The path note is weaker on Codex (gpt-5.6-luna).** ko-rewrite's upstream step 1 names `references/quick-rules.md`. Claude Code runs (P1–P5, 8 runs) followed our note directly. The Codex run first tried `quick-rules.md` (exit 2), listed the skill directory, then read `taxonomy-rewrite.md`. It recovered at the cost of two tool calls. P1 decision 1 named the fallback (ship the reference under the upstream name). _Decision below._

## Subagent runs

Exploration cap: 1 of 4 used so far.

| # | Tier | Purpose | Tokens | Result |
|---|---|---|---|---|
| 1 | mid (Sonnet 5) | Codex docs: manifest, custom agents and `multi_agent_v2`, AGENTS.md, `developer_instructions`, plugin hooks and trust, MCP resources, removal | _pending_ | _pending_ |
| V | mid (Sonnet 5) | Verification of the done-condition (outside the cap) | _pending_ | _pending_ |
