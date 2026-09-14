# P6 — Codex build

2026-09-14. Branch `dev`. Flow: `5-preflight/flow.md` §3 P6.

## Result

`python3 -m build.agent_plugin` builds `dist/agent-plugin/{agent-reply,formal-report}/` from the same `normalized/` and `assemble/` inputs as P5. `python3 -m build.checks` runs 06 §12 checks 1–4 across both harnesses and all four dists with 0 failures. In Codex 0.154.0, headless:

- **Plugin:** installs from a local marketplace, and a skill runs under `codex exec`.
- **Main thread:** the policy section installed into AGENTS.md reaches the main reply.
- **Plugin hook:** a SessionStart hook declared in the plugin runs when hook trust is bypassed.
- **Custom agent:** reaching one named `korean-reviewer` is unreliable. It clearly happened once in six attempts, so that clause is **release-blocked**. The policy still reaches spawned subagents through AGENTS.md, and the one successful spawn carried the agent file's instructions.

| Artifact | Path |
|---|---|
| Build | `build/agent_plugin.py` (reuses the Claude Code renderer), `build/mini_toml.py` |
| Installer | `build/ko_quality_codex.py` → `dist/agent-plugin/<profile>/install/ko_quality_codex.py` — `install`, `uninstall`, `status`; `--scope global` (`$CODEX_HOME/AGENTS.md`, `$CODEX_HOME/agents/`) or `--scope project` |
| Output per profile | `plugin.json` (root, `skills: ./skills/`), `skills/` (byte-identical to Claude Code), `install/AGENTS.section.md` (policy between `<!-- ko-quality:begin profile=… -->` and `<!-- ko-quality:end -->`), `install/.codex/agents/korean-{reviewer,writer,editor}.toml`, `provenance/policy.yaml` |
| Marketplace, install doc | `dist/agent-plugin/.agents/plugins/marketplace.json`, `assemble/install/agent-plugin.md` → `dist/agent-plugin/README.md` |
| Run logs | `tests/runs/P6/skill-install.json`, `channel.json` (batch 1), `channel-rerun.json` (batch 2) |

## Checks

| Check | Result |
|---|---|
| 06 §12 check 1 | re-extraction 0 failures; all sidecars recompute, including spans inside the TOML `developer_instructions` strings (76 and 72 upstream spans) |
| Check 2 (policy identical) | Claude Code output-style body = AGENTS.md section body (markers removed) for both profiles; every agent in both harnesses starts with it |
| Check 3 (agents identical) | all 6 agent prompts identical across harnesses |
| Check 4 (skills identical) | `skills/` byte-identical in all 4 dists |
| Installer | In throwaway directories: install twice → one section; second profile replaces the first in place; uninstall restores a pre-existing AGENTS.md byte for byte; an agent file not written by ko-quality is never overwritten; an AGENTS.md created by install is removed by uninstall |
| Plugin install | Throwaway `CODEX_HOME` (auth symlinked): `codex plugin marketplace add dist/agent-plugin` → `codex plugin add ko-quality@ko-quality`: root `plugin.json` accepted, installed as version `local` |
| Skill under `codex exec` | `$ko-rewrite` read the installed SKILL.md and produced the rewrite report (`skill-install.json`) |

## Channel runs

Each run used its own throwaway `CODEX_HOME` and a marked copy of `dist/agent-plugin`. A marker line was added to the AGENTS.md section (MAIN) and to every agent's `developer_instructions` (AGENT). A SessionStart hook was added to `plugin.json` under `extensions.com.openai.hooks`. Runs use `codex exec --json -s read-only`.

| Run | Model, flags | Agents at | MAIN marker | AGENT marker / spawn | Reading |
|---|---|---|---|---|---|
| main-policy | luna, `--ephemeral` | global | 1 | — | **AGENTS.md policy reaches the main reply** |
| subagent-default | luna, `--ephemeral` | global | 1 | 2: inside the `wait` result and relayed; `spawn_agent` → completed | **Custom agent's instructions reached the subagent** (the event shows no agent-type field) |
| subagent-v2 | luna, `--ephemeral`, `multi_agent_v2` | global | 1 | 1, in the main reply only; `collab spawn failed: no thread with id` ×2 | spawn failed; main read the agent file itself |
| subagent-terra | terra, `--ephemeral` | global | 1 | 0; `wait` ×4 with no receivers; spawn failed | failed |
| hook-bypass | luna, `--ephemeral`, `--dangerously-bypass-hook-trust` | global | 1 | — | **Plugin SessionStart hook ran**: its payload's `session_id` equals this run's thread id; payload keys `session_id, transcript_path, cwd, hook_event_name, model, permission_mode, source` |
| luna-global-repeat | luna | global | 1 | 0; no spawn | the model reviewed in the main thread instead of delegating |
| terra-global | terra | global | 1 | 1, in the main reply only; `wait` with no receivers | not attributable to a spawned agent |
| luna-global-v2 | luna, `multi_agent_v2` | global | 0 | 0 | run exited 1 |
| luna-project | luna, project trusted | project `.codex/agents/` | 1 | 0; "현재 korean-reviewer 에이전트를 호출할 수 있는 도구가 없어" | project-scope agents not reachable (same as the preflight probe) |

Custom agent reached, clearly: 1 of 6 delegation attempts. The policy reaches the main thread through AGENTS.md in every run. The preflight probe (a project AGENTS.md reaching a generic spawned subagent) is the evidence that subagents receive the policy without a custom agent.

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | **Main-thread injection point (06 §9):** global AGENTS.md section with markers, project scope as an option / `config.toml` `developer_instructions` | Global AGENTS.md (+ `--scope project`) | high | main-policy run; installer idempotency tests; `developer_instructions` is a single user key the user may already own |
| 2 | major | **`instructions` channel (06 §9, §10):** none / policy body in a tool-less MCP server / summary (`adapted`) | None | medium-high | AGENTS.md already carries the verbatim body to main (and, per the probe, to subagents); docs say server `instructions` are used "alongside the server's tools", undocumented without tools |
| 3 | major | **Hook distribution (06 §11.5):** plugin bundle (`extensions.com.openai.hooks` in root `plugin.json`) / `install/.codex/hooks.json` | Plugin bundle | medium | hook-bypass run. Users must trust the hook once via `/hooks` (docs); automation needs the bypass flag. Codex's own installed plugins declare `hooks` in `.codex-plugin/plugin.json`; the documented root form worked here |
| 4 | major | **Manifest location:** root `plugin.json` / `.codex-plugin/plugin.json` | Root | medium | accepted by `codex plugin add` and loaded skills; docs name it primary. Installed OpenAI plugins use only `.codex-plugin/`, so the fallback stays in mind for 7-review |
| 5 | major | **Custom agent route:** keep `.codex/agents/*.toml` via the installer (global scope) / drop agents for Codex and rely on AGENTS.md | Keep global agents; mark release-blocked | medium | 1/6 clear success; nothing else carries a named reviewer in Codex. Cheapest to reverse: files are removed by `uninstall` |
| 6 | major | **ko-rewrite path note on Codex:** keep the note / also ship the reference as `references/quick-rules.md` (upstream's name) | Keep the note | medium | The luna run recovered with two extra tool calls; renaming breaks 06 §7's file name and the P1 decision for both harnesses. Re-evaluate in 7-review |
| 7 | minor | **Codex MCP resources (06 §10):** assume tools only / test a resources server | Tools only | medium | docs list STDIO, Streamable HTTP and server instructions only; no tools are shipped in 06 |
| 8 | minor | Check 2/3 comparison trims blank lines at the ends / compare raw | Trim | high | leading blank line is Claude Code output-style layout; 06 §12 already excludes frontmatter and wrapping markers |

## Spec did not know

- **Check 2 needed a normalization.** The Claude Code output-style body begins with the blank line that follows its frontmatter; the AGENTS.md section does not (decision 8).
- **The path note is weaker on Codex (gpt-5.6-luna).** Claude Code runs (P1–P5) followed the note directly. The Codex run first tried `references/quick-rules.md` (exit 2), listed the skill directory, then read `taxonomy-rewrite.md` (decision 6).
- **`--ephemeral` breaks subagent spawns intermittently.** Under `--ephemeral`, spawns failed with `collab spawn failed: no thread with id` (terra, `multi_agent_v2`). Without it, spawns did not fail that way but were often not attempted.
- **Project-scope custom agents were not offered as a tool** even with the project trusted (preflight probe and luna-project). Global agents were reached once.
- **Codex docs do not name the spawn tool's parameters.** No run exposed an agent-type field in the event stream; how a named custom agent is selected is not observable from `--json` output.
- **Hook payload** (SessionStart, 0.154.0): `session_id, transcript_path, cwd, hook_event_name, model, permission_mode, source`. Hook commands get `PLUGIN_ROOT` and, for compatibility, `CLAUDE_PLUGIN_ROOT` (docs) — one hook command can serve both harnesses (P7).
- **Removal traces:** `codex plugin remove` leaves an empty `~/.codex/plugins/cache/<marketplace>/` directory (preflight probe); documented in the install README.

## Differs from spec

- 06 §14.3 "korean-reviewer … 호출되고" is not reliably met in Codex (release-blocked below). 06 §2.2 describes custom agents as a supported channel; the build shows them as unreliable under `codex exec` 0.154.0.
- `dist/agent-plugin/` holds one plugin per profile plus a marketplace, like P5 (decision ②).
- No hooks and no build stamp are shipped yet; P7 adds both.

## Subagent runs

Exploration cap: 1 of 4 used.

| # | Tier | Purpose | Tokens | Result |
|---|---|---|---|---|
| 1 | mid (Sonnet 5) | Codex docs: manifest, custom agents and `multi_agent_v2`, AGENTS.md, `developer_instructions`, plugin hooks and trust, MCP resources, removal | 142.1k | Root `plugin.json` documented as primary, but installed OpenAI plugins use `.codex-plugin/`; custom agents in `~/.codex/agents` and `.codex/agents`, spawn parameters undocumented; hook events, env vars (`PLUGIN_ROOT`, `CLAUDE_PLUGIN_ROOT`), payload fields and per-hash trust documented; MCP resources not listed |
| V | mid (Sonnet 5) | Verification of the done-condition (outside the cap) | _pending_ | _pending_ |

## Release-blocked

- **`korean-reviewer` (and any named custom agent) is not reliably invoked in Codex.** 1 of 6 delegation attempts clearly reached the custom agent (`tests/runs/P6/channel.json` subagent-default). Other attempts did not spawn, spawned without attribution, or failed (`channel.json`, `channel-rerun.json`). Path taken: agents stay in the install (removable), policy for subagents relies on AGENTS.md. To resolve in 7-review: retest with a later Codex release, interactive sessions, or a documented agent selector.
- _(Verification result pending.)_
