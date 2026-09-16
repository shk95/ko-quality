# 02. Codex channel retest — observations and verdicts

> Record of the retest this temporary era was waiting for. It ran on 2026-09-16, during era 02's `3-spec`, at the user's request.
> Run record: [`tests/runs/99-retest/codex-channels.json`](../../tests/runs/99-retest/codex-channels.json). Input: [`1-concept/01_idea.md`](1-concept/01_idea.md).

## Setup

- **The version did not move.** codex-cli 0.154.0 and model `gpt-5.6-luna`, the same as era 01. So this is the same test, and the open question of the concept ("what is the baseline if the version changes") does not arise.
- **Environment:** a throwaway `CODEX_HOME` with `auth.json` symlinked, and a scratch `KO_QUALITY_HOME`. The user's `~/.codex` was never the home.
- **Artifact:** a copy of `dist/agent-plugin/agent-reply` with canaries: `MAIN` in the `AGENTS.md` section, and `AGENT` in every agent's `developer_instructions`. A raw-payload dump hook sat beside the logger.
- **Runs:** 11 `codex exec` runs.

## Verdicts

| # | Verdict | What decided it |
|---|---|---|
| A1 | **Resolved, with a condition** | Named agents were reached **3/3** with `--enable multi_agent_v2` and without `--ephemeral` |
| A2 | **Resolved** | `SubagentStop` gives the subagent's own message, `agent_type` and `agent_id` |
| A3 | **Resolved** | Codex sets `PLUGIN_ROOT` **and** `CLAUDE_PLUGIN_ROOT`. 8 logger records were written |
| C1 | **Cause found and fixed on a copy** | The note sat 19 lines above the step that names the path. Moved beside the step: 3/3 direct |
| C4 | **Not meaningfully retested** | Same CLI version. The root `plugin.json` was accepted again |

### A1 — era 01's 1-of-6 mixed three configurations

The tool the model sees depends on two switches, and era 01's six attempts used different combinations of them.

| Configuration | Spawn tool offered | Outcome |
|---|---|---|
| default (`multi_agent`, v1), any | **none**. The model said it has no tool for sub-agents | reviews in the main thread |
| `multi_agent_v2`, `--ephemeral` | `spawn_agent` | **spawn fails**: `collab spawn failed: no thread with id` |
| `multi_agent_v2`, not ephemeral | `collaboration.spawn_agent` with `agent_type` ∈ {`korean-editor`, `korean-reviewer`, `korean-writer`, `default`, `explorer`, `worker`} | **reached, 3/3** |

The custom agents are therefore not unreliable. **They need v2, and v2 needs a persisted thread.** Interactive sessions were not tested, and neither were project-scope agents.

### A2 — the ambiguity is real, and hooks remove it

The ephemeral v2 run failed to spawn. **Its final message still carried the AGENT canary**: the orchestrator read the agent file and relayed its instructions. That is exactly the failure era 01 could not rule out from message text alone.

Hooks separate the two cases. In the three successful runs:

- `SubagentStop` carried `agent_id`, `agent_type: korean-reviewer`, `agent_transcript_path`, and the subagent's own `last_assistant_message`.
- **That message held the AGENT canary and not the MAIN canary.** The subagent received its definition. The `AGENTS.md` section's instruction did not win inside it.
- `PostToolUse` calls made **inside** the subagent carry `agent_id` and `agent_type` too.

In the failed run, no `SubagentStop` fired.

### A3 — the hook command works unchanged

Both `PLUGIN_ROOT` and `CLAUDE_PLUGIN_ROOT` point at the installed plugin root. The shipped `hooks.json` runs as is.

The logger wrote 8 records:
- Every record has `harness: codex`, `model: gpt-5.6-luna` (taken from the payload), and `usable: true`.
- The main thread records `injection_point: agents-md`.
- There are three `sub-to-orchestrator` records with `agent_type: korean-reviewer` and `injection_point: agent-definition`.

**Two things for era 02's logger (09 §11), found here:**
- A subagent's `PostToolUse` shares the parent's `session_id`, so the logger's per-session tool accumulation mixes subagent tools into the main thread's `task_type`. The `agent_id` field is there to separate them.
- `policy_on` and `injection_point` come from the plugin stamp on Codex too. The `AGENTS.md` section is installed by a separate script, so a plugin without the installer would still record `policy_on: true`. This is the same defect E4 found on Claude Code, through a different mechanism.

### C1 — recovery is not direction, and the cause is placement

**Era 01 did not succeed here either.** Its one Codex rewrite run also read `references/quick-rules.md` first (exit 2) and recovered (P6 decision 6). "Success" meant the rewrite completed. Only Claude Code followed the note directly, 7/7. Nothing regressed.

Both retest runs took the same path: `SKILL.md`, `references/quick-rules.md` (exit 1), a directory listing, then `taxonomy-rewrite.md`.

**Why.** The redirecting note is in the skill's header. Upstream step 1, **19 lines further down**, names the literal path: "`references/quick-rules.md`(이 SKILL.md 디렉토리 기준 상대 경로)를 읽어…". Codex (luna) executes the step as written, while Claude Code applies the earlier note.

**Tested.** On a copy, the same redirect was placed as one line of ours **directly under step 1**. All 3 of 3 runs then read `taxonomy-rewrite.md` directly, with no failed read. The upstream sentence is untouched, and an ours line between upstream fragments is structure, so `adapted` stays at 0.

## Decisions this hands forward

| # | For | Proposed | Confidence |
|---|---|---|---|
| R1 | Codex install doc and 09 §2.2 | Require `[features] multi_agent_v2 = true` for the agents, and state that `--ephemeral` breaks delegation. Lift the release-blocked mark on A1 for that configuration | high (3/3, and the failure modes reproduced) |
| R2 | 09 §11 logger | Keep subagent tool calls out of the main thread's accumulation by `agent_id`. Derive `policy_on`/`injection_point` from what took effect, on both harnesses | high |
| R3 | 09 §7, ko-rewrite | Keep `taxonomy-rewrite.md` and put the redirect as an ours line **directly under upstream step 1**, in both harnesses (check 4). Shipping the file under upstream's name is the fallback, not needed | high (3/3 on the failing harness; Claude Code already followed the note) |
| R4 | C4 | No action. Re-check when the CLI version moves | — |
