# P7 — server and minimal logger

2026-09-14. Branch `dev`. Flow: `5-preflight/flow.md` §3 P7. **In progress. Stopped at the user's request.**

## Done

| Item | Path | State |
|---|---|---|
| Logger | `logger/ko_quality_log.py` | Committed. One record per `Stop` (main-to-user) and `SubagentStop` (sub-to-orchestrator), built from hook input only (no transcript). Records go to `$KO_QUALITY_HOME` or `~/.ko-quality`, under `logs/<profile>/<yyyy-mm>.jsonl`. Profile, harness and upstream versions come from `ko-quality.stamp.json` in the plugin root (`$PLUGIN_ROOT`, then `$CLAUDE_PLUGIN_ROOT`). Secrets are masked, `usable` needs ≥20 Korean 어절 in prose, and the logger always exits 0 |
| Offline test | `tests/logger_test.py` | Committed. Synthetic payloads: 0 failures |
| Hook wiring | `assemble/hooks/hooks.json` | Six events, each running `python3 "${CLAUDE_PLUGIN_ROOT}/logger/ko_quality_log.py" <event>`. Codex sets `CLAUDE_PLUGIN_ROOT` for compatibility (P6 docs run), so one file serves both harnesses |
| Server | `server/README.md` | Decision: ship no MCP server in 06. Claude Code already carries the policy twice; Codex's instructions channel is none (P6 decision 2) |

## Next (resume here)

1. **P6 is closed.** Its verification finished after the stop and is recorded, including one more release-blocked reservation. **Codex cannot be run in this build**, so step 3's Codex half is deferred; the Claude Code half is not.
2. **Ship logger, hooks and stamp in both builds.** A patch was drafted outside the tree and not applied:
   - In `build/claude_code.py`, add `stamp(profile, harness, injection_point)`. It returns tool, version, profile, plugin name, harness, `injection_point` and `upstream_versions` (name → commit from `upstream/lock.yaml`), with no timestamps, so builds stay reproducible.
   - Add `ship_logger(pdir, …)`. It copies `logger/ko_quality_log.py` → `<plugin>/logger/`, copies `assemble/hooks/hooks.json` → `<plugin>/hooks/`, and writes `<plugin>/ko-quality.stamp.json`. Call it per profile: Claude Code with `"claude-code", "output-style"`, Codex with `"codex", "agents-md"`.
   - In `build/agent_plugin.py`, add `"extensions": {"com.openai": {"hooks": "./hooks/hooks.json"}}` to `plugin.json`.
   - Rebuild both harnesses, run `python3 -m build.checks`, then `claude plugin validate --strict` on both Claude Code plugins.
3. **Live test**, with a scratch `KO_QUALITY_HOME`:
   - Claude Code headless with `--plugin-dir dist/claude-code/agent-reply`: one rewrite prompt, and one prompt delegating to `korean-reviewer` (expect a `sub-to-orchestrator` record with `agent_type`).
   - Codex in a throwaway `CODEX_HOME` (auth symlinked), `--dangerously-bypass-hook-trust`.
   - Expect `usable: true` records from both harnesses, no `logger-errors.log`, and no state files left after `SessionEnd`. Record whether Codex `Stop`/`SubagentStop` payloads carry `last_assistant_message` and `agent_type`.
4. **Decisions to record:** build stamp format (above); `sub-to-sub` is never emitted, because hook input has no parent (06 §13.1: value dropped); `tokens` is estimated at characters / 2.5; server not shipped.
5. **Wrap up:** P7 verification, then update `design/README.md`. After that, 7-review: release-blocked marks are in P5 (open item, non-blocking) and P6 (custom agent route).

## Subagent runs

Exploration cap: 0 of 4 used.
