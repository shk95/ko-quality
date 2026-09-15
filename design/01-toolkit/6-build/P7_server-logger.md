# P7 — server and minimal logger

2026-09-14 (started), 2026-09-15 (built). Branch `dev`. Flow: `5-preflight/flow.md` §3 P7. **Built. Codex half release-blocked** (Codex half not measured; deferred).

## Summary

Both harness builds now carry the minimal logger, its hook wiring and a build stamp. The Claude Code half of the done-condition is met live: on `dist/claude-code/agent-reply` unchanged, a rewrite run and a `korean-reviewer` delegation run left three `usable: true` records (two `main-to-user`, one `sub-to-orchestrator` with `agent_type: ko-quality:korean-reviewer`), no `logger-errors.log`, and no state file after `SessionEnd`. The Codex half is not measured: Codex could not be run in this build, so "Codex logger records not produced" (flow §5) stands and P7 is marked **release-blocked** on it. No MCP server is shipped.

## Built

| Item | Path | State |
|---|---|---|
| Logger | `logger/ko_quality_log.py` | One record per `Stop` (main-to-user) and `SubagentStop` (sub-to-orchestrator), built from hook input only (no transcript). Records go to `$KO_QUALITY_HOME` or `~/.ko-quality`, under `logs/<profile>/<yyyy-mm>.jsonl`. Profile, harness, `injection_point` and upstream versions come from `ko-quality.stamp.json` in the plugin root (`$PLUGIN_ROOT`, then `$CLAUDE_PLUGIN_ROOT`, then the directory above the script). Secrets are masked, `usable` needs ≥20 Korean 어절 in prose, and the logger always exits 0 |
| Offline test | `tests/logger_test.py` | Synthetic payloads: 0 failures |
| Hook wiring | `assemble/hooks/hooks.json` | Six events, each running `python3 "${CLAUDE_PLUGIN_ROOT}/logger/ko_quality_log.py" <event>`. Codex sets `CLAUDE_PLUGIN_ROOT` for compatibility (P6 docs run), so one file serves both harnesses |
| Build stamp and shipping | `build/claude_code.py` (`lock_versions`, `stamp`, `ship_logger`), `build/agent_plugin.py` | Every profile plugin in both dists gets `logger/ko_quality_log.py`, `hooks/hooks.json` and `ko-quality.stamp.json`. Codex `plugin.json` declares `extensions.com.openai.hooks: ./hooks/hooks.json` (the form that ran in P6's hook-bypass run). Claude Code picks up `hooks/hooks.json` by convention |
| Install docs | `assemble/install/claude-code.md`, `assemble/install/agent-plugin.md` | A "로그" note: what is logged, where, masking, `KO_QUALITY_HOME`; Codex needs one-time hook trust via `/hooks` and is marked unverified |
| Server | `server/README.md` | Not shipped (decision 4) |
| Live run summary | `tests/runs/P7/claude-code-logger.json` | Records without id, ts and output text; files left under the scratch home |

Checks after the rebuild: `python3 -m build.checks` 0 failures (checks 2–3 across both harnesses, check 4 over four dists); `claude plugin validate --strict` passes on both Claude Code plugins; a second rebuild leaves `git status` clean (stamp has no timestamps).

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | minor | **Build stamp:** flow leaning (`dist/<harness>/ko-quality.stamp.json` with build commit and built-at) / per plugin root, content-only | Per plugin root: `tool, version, profile, plugin, harness, injection_point, upstream_versions` (name → commit from `upstream/lock.yaml`). No build commit, no built-at | high | A per-harness stamp cannot name the profile, since each profile is its own plugin (decision ②). The plugin root is what both harnesses expose to hooks (`CLAUDE_PLUGIN_ROOT`, `PLUGIN_ROOT`), so no installer has to write a path. Timestamps and the build commit would make every rebuild dirty the tree (the commit that holds `dist/` cannot contain its own hash). `upstream_versions` is what 06 §11.3 asks for; the build is identified by those plus `version` |
| 2 | minor | **`sub-to-sub`:** emit from a parent guess / never emit | Never emitted | high | Hook input carries no parent agent; 06 §13.1 drops the value when there is no method |
| 3 | minor | **`tokens`:** read the transcript / estimate | `characters / 2.5`, `method: estimate` | medium | 06 §11.1 forbids reading the transcript; hook input carries no usage. The factor is a rough Korean-text average, labelled as an estimate in every record |
| 4 | minor | **MCP server:** ship with `instructions` only / ship nothing | Nothing | high | Claude Code already carries the policy twice (output style, agent definitions); a tool-less server would be a third copy. Codex has no instructions channel for it (P6 decision 2). `server/README.md` |
| 5 | minor | **Codex live test:** wait / close P7 with the Codex half release-blocked | Close, release-blocked | high | Flow §3 P7 names this exact fallback; the build does not halt (AGENTS.md). The Codex half stays a resume item for 7-review |
| 6 | minor | **`model` in Claude Code records** | Left `unknown` when hook input has none | high | Observed: all three records read `model: unknown` in headless 2.1.270. 06 §11.2 already allows it (`model` is optional in Claude Code's hook input) |

## Live test (Claude Code)

Claude Code 2.1.270, `claude-opus-5[1m]`, headless, `--setting-sources project,local`, `--no-session-persistence`, empty cwd per run, `KO_QUALITY_HOME` = empty scratch dir, plugin `dist/claude-code/agent-reply` from build 72bf8fc. Two runs, $0.65.

| Run | Prompt | Result | Records |
|---|---|---|---|
| rewrite | 번역투 문단 윤문 | Rewritten paragraph in one turn, no tool calls | `main-to-user`, `injection_point: output-style`, `usable: true`, 56 est. tokens |
| delegate | `korean-reviewer`에게 검토를 맡기고 요약 | One subagent spawned (`ko-quality:korean-reviewer`), summary returned | `sub-to-orchestrator` with `agent_type: ko-quality:korean-reviewer`, `injection_point: agent-definition`, `usable: true`; then `main-to-user`, `usable: true` |

All three records carry `profile: agent-reply`, `harness: claude-code`, the four upstream commits, `instruction_lang: ko`, `artifact_lang: ko`, `masked: false`. After both runs the only file under the home is `logs/agent-reply/2026-09.jsonl`: no `logger-errors.log`, no `state/` file.

## Found

- **`model` is absent from Claude Code hook input in headless runs** (2.1.270): every record reads `unknown` (decision 6).
- **`task_type` rule:** both runs read `writing`, since no edit tool ran. The rule cannot tell a writing task done through `Write` from a coding task; left for the validation stage.
- **Codex payloads unmeasured.** Whether Codex `Stop`/`SubagentStop` input carries `last_assistant_message` and `agent_type` is still open. P6 saw only `SessionStart` (`session_id, transcript_path, cwd, hook_event_name, model, permission_mode, source`). If `last_assistant_message` is missing, the logger writes nothing for that event (it never fails).

## Release-blocked

- **Codex logger records not produced** (flow §5, P7). Not measured: Codex could not be run in this build; not a known mechanism failure. To resolve: in a throwaway `CODEX_HOME` with `auth.json` symlinked, install `dist/agent-plugin/agent-reply`, run `codex exec --dangerously-bypass-hook-trust` once plainly and once delegating to `korean-reviewer`, with a scratch `KO_QUALITY_HOME`; record the `Stop`/`SubagentStop` payload keys and whether `usable: true` records appear.

## Subagent runs

Exploration cap: 0 of 4 used.

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
