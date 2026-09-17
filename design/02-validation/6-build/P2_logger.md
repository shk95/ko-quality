# P2 — Logger

## Summary

The logger now records only what a hook payload establishes (09 §11–§12.1). It keeps state per session and per agent, captures the delegation prompt and the `SubagentHandback` report, counts harness-injected prompts, fills §11.3's policy fields per harness, and writes one `logs/<yyyy-mm>.jsonl` under an expanded `KO_QUALITY_HOME`. `tests/logger_test.py` replays the recorded payload shapes of both harnesses. Live runs on Claude Code 2.1.274 and Codex 0.154.0 each wrote one main and one sub record matching §11.3.
Done-condition: **met on all five clauses** (independent `mid` verification). Release-blocked: **0**.

## Built

| Item | Path | State |
|---|---|---|
| Logger: §11.2 event table, §11.3 policy fields, §12.1 record, masks, `expanduser`, §11.4 layout | `logger/ko_quality_log.py` | done; shipped byte-identical in all three dists |
| Test: replays of `hook-payloads.json` and era 99 runs `a1-1`, `r1`; scenarios; malformed payloads | `tests/logger_test.py` | done, 0 failures |
| Live session summaries | `tests/runs/02-P2/live-sessions.json` | done |
| Test and checks output | `tests/runs/02-P2/logger-test-and-checks.txt` | done |

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | Claude Code sub record: hold it until the `Agent` tool's PostToolUse brings the delegation prompt / write at `SubagentStop` with no prompt | Hold it in session state and write on the matching `agentId`, or at the next `Stop` or `SessionEnd` without the prompt. The recorded order is `SubagentHandback` → `SubagentStop` → `PostToolUse(Agent)`, so writing at `SubagentStop` would never carry 09 §12.1's "delegation prompt if captured". Reversible in one function | high | `hook-payloads.json` order; live run: sub `task` holds the prompt |
| 2 | major | Count `<task-notification>` prompts as injected, like `<agent-message from=` / only the prefix §11.2 names | Both prefixes. §11.2's rule is "a harness-injected prompt is not a task"; on 2.1.274 a background agent's completion arrives as `<task-notification>`, and the first live run recorded it as the task of a fourth main record | medium-high | live run `cc` (before) and `cc-default` (after) |
| 3 | minor | Masks: 주민등록번호 with a hyphen only / also 13 bare digits | Hyphen required. Thirteen bare digits also match millisecond timestamps. Phones: `0N(N)-NNN(N)-NNNN` with hyphen or space, `+82`, and 010-style numbers without separators. Cards: four groups of four with separators. Home: the literal `Path.home()`, then any `/Users/<name>` or `/home/<name>` → `~` | medium | scenario test |
| 4 | minor | Sub record `task` when no delegation prompt was captured: `""` / `null` | `""`, as §12.1 types `task: string` | medium-high | 09 §12.1 |
| 5 | minor | Codex delegation prompt: parse the spawn tool's input / leave uncaptured | Uncaptured. §11.2 names only Claude Code's `Agent` tool, and the recorded Codex payloads carry key names, not the spawn input's shape | medium | `codex-channels.json` |
| 6 | minor | `skills_method` when no skill ran: the harness's method / `null` | The harness's method (`tool` or `path-read`): an empty list with a method says "looked, found none". `null` only when the harness is unknown | medium | 09 §12.1 |
| 7 | minor | Codex "a name the installer wrote": read `.ko-quality-install.json` / run `ko_quality_codex.py status` in the hook | Read the manifest the installer writes, in `CODEX_HOME` and in `.codex/` of each directory from `cwd` to the git root; a name counts only if its file still exists (as `status` reports). No subprocess in a hook | medium-high | `build/ko_quality_codex.py` |
| 8 | minor | Codex marker search: project `AGENTS.md` from `cwd` up to the git root (nearest first), then global | As stated. Codex concatenates both; a project section is the more specific one if two markers differ | medium | 09 §11.3 |
| 9 | minor | Prose extensions for `task_type: document` | `.md .markdown .mdx .txt .rst .adoc .org`; `NotebookEdit` paths count as source | medium | 05 E4 item 2 |
| 10 | minor | Per-turn counters with several `Stop`s in one user turn (background agents) | Counters reset only at a non-injected prompt, so each main record of that turn repeats the turn's tool counts. Recorded, not deduplicated | medium | live run `cc-default` |
| 11 | minor | Harness with no stamp: `null` / inferred | Inferred from the payload (`turn_id` → codex, `prompt_id` → claude-code), since `plugin_present: false` records still need a harness | medium | test `edges` |

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V2 | mid (Sonnet 5) | Verification of the P2 done-condition (outside the cap), isolated worktree at `59c0f95` | 138,147 | All five clauses and both checks **met**; noted that the P2 record did not yet exist |

Exploration runs: 0 of 4.

## Cost

| Run | Model | USD |
|---|---|---|
| Claude Code live, first (logger before decision 2) | claude-sonnet-5 | 0.297 |
| Claude Code live, default prompt | claude-sonnet-5 | 0.290 |
| Claude Code live, foreground prompt | claude-sonnet-5 | 0.332 |
| Codex live (`gpt-5.6-terra`, 83,703 input and 318 output tokens) | gpt-5.6-terra | not computed (API-equivalent cost not computed; token counts recorded) |
| **Total** | | **0.92**, Codex excluded (no ceiling set for P2) |

## Differs from spec

- **Two injected-prompt prefixes, not one** (decision 2). 09 §11.2 names `<agent-message from=`; the logger also treats `<task-notification>` as injected.
- **A Claude Code sub record is written after `SubagentStop`**, when its delegation prompt arrives (decision 1). 09 §11.2 lists the sub record under `SubagentStop`.

## Spec did not know

- **On 2.1.274 a delegation runs in the background by default.** `subagent_stats.started_in_background` was 1 whenever the prompt did not ask for the foreground. The main thread then stops once while waiting, once with the report, and once more after the `<task-notification>` prompt: three main records per user turn. Asked for the foreground, one main and one sub record. P8's generator and analysis have to key main records by `turn_key` and expect several per turn, or prompt for the foreground.
- **The hand-back message was delivered as an injected prompt in the foreground run too** (`injected_prompts: 1`), and `SubagentHandback` carried the report in every live delegation. 09 §14.2's hand-back row: 3 of 3 live delegations on 2.1.274 used it, plus 2 of 2 in X2.
- **A sub record's `prompt_id` is the subagent's own**, not the orchestrator's turn. The sub record's `turn_key` therefore does not equal the main record's; joining them needs `session_id` and order.
- **The `Agent` tool's PostToolUse fires after `SubagentStop`** (recorded order, confirmed live). This is what decision 1 answers.
- **Codex `--json` shows no spawn item**, only `collab_tool_call` items with `tool: wait`, while the hooks saw the spawn. The Codex sub record's output is `SubagentStop`'s own message, as era 99 found.
- **Hooks on Codex were trusted with `--dangerously-bypass-hook-trust`**, as U4 and X6 set up. An interactive trust prompt was not exercised.

## Verification

Run V2, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned:

> **Verification: P2 — Logger (design/02-validation/4-plan/10_plan.md §4 P2)**
>
> Checked out `59c0f95` (detached). Symlinked `upstream/.cache` (already present). All commands reproduced independently; nothing taken on the builder's claim.
>
> **Done-condition clauses**
>
> **1. `logger_test.py` passes on recorded payloads for both harnesses, including subagent edits kept out of the main record and `<agent-message from=` counted not as `task`.**
> - verdict: **met**
> - evidence: `python3 tests/logger_test.py` → `logger test: 0 failures` (reproduced, exit 0). `tests/logger_test.py:116` reads `tests/runs/02-spec/hook-payloads.json` (13 events, Claude Code), `:149` reads `tests/runs/99-retest/codex-channels.json` (14 runs, Codex). Line 127: `check(main.get("injected_prompts") == 1, "cc replay: the <agent-message from= prompt is counted in injected_prompts")`; line 128: `check(main.get("task") == "Use the Agent tool...", "cc replay: injected prompt does not overwrite task")`. Subagent-edit exclusion: lines 189–190 inject an `Edit` on `agent_id="ag-2"` (`ko-quality:korean-editor`) touching `src/app.py`, and line 210 asserts `(m1.task_type, m1.task_type_method) == ("document", "rule")` with comment "subagent's .py edit excluded".
> - how it could still be wrong: the subagent-edit-exclusion and both counter behaviors are proven via `test_scenarios`' hand-written payloads, not literally inside the two *recorded* payload replays (`hook-payloads.json` / `codex-channels.json`). If the clause is read as requiring these specific behaviors to be shown from the recorded fixtures themselves (not synthetic scenarios), this is weaker — though the `<agent-message from=` counting *is* also asserted directly on the `hook-payloads.json` replay (line 127–128 above operate on `test_claude_code_replay`, which is the replay, not a scenario).
>
> **2. Live headless Claude Code session with a delegation writes one main and one sub record matching §11.3's table.**
> - verdict: **met**
> - evidence: `tests/runs/02-P2/live-sessions.json` "foreground" run (committed logger, `build_id 51112680979b60c3`). Independently re-read the raw record file at `<scratch>/p2/cc-foreground/home/logs/2026-09.jsonl`: exactly 2 lines — sub: `{policy_on: True, injection_point: "agent-definition", profile: None, policy_method: "agent-type", agent_type: "ko-quality:korean-reviewer"}`; main: `{policy_on: None, injection_point: None, profile: None, policy_method: None, model: None}`. Both match §11.3 rows exactly ("sub, shipped agent" and "main, Claude Code").
> - how it could still be wrong: only one of the three CC runs (`cc-foreground`) produced exactly one main + one sub; the "default"/background runs produced 3 main records (background-wait, summary, `<task-notification>`-triggered `Stop`) + 1 sub. If "writes one main and one sub record" means *every* live CC session must do so (not just one sampled session), the background runs would not satisfy it — though their extra main records are themselves correctly shaped per §11.3, just more than one.
>
> **3. Live `codex exec` session with hooks trusted and a custom-agent spawn (`multi_agent_v2`, no `--ephemeral`) writes one main and one sub record matching §11.3's Codex rows.**
> - verdict: **met**
> - evidence: raw `<scratch>/p2/cx/home/logs/2026-09.jsonl` (independently read): exactly 2 lines — sub: `{agent_type: "korean-reviewer", policy_on: True, injection_point: "agent-definition", profile: None, policy_method: "agent-type", model: "gpt-5.6-terra"}`; main: `{policy_on: True, injection_point: "agents-md", profile: "agent-reply", policy_method: "agents-md-marker", model: "gpt-5.6-terra"}`. `<scratch>/p2/cx/codex-home/config.toml` has `[features] multi_agent_v2 = true`; `.ko-quality-install.json` lists 3 installer-written agents. `live-sessions.json` method string: `codex exec --json -m gpt-5.6-terra -s read-only -C <workdir> --dangerously-bypass-hook-trust <prompt>. No --ephemeral.`
> - how it could still be wrong: "hooks trusted" is achieved via `--dangerously-bypass-hook-trust` (gated behind a permission rule added per `flow.md` U4 / explorations X6), not an interactive hook-trust prompt. This is the project's established meaning for headless automation (era 01/99 precedent, X6), but if a stricter reading of "trusted" is intended, this substitutes a bypass for it.
>
> **4. The logger prints nothing and exits 0 on a malformed payload.**
> - verdict: **met**
> - evidence: independently invoked the logger directly (outside the test suite) with (a) truncated JSON `{"session_id": "b", "last_assistant_mess`, (b) `not json at all` with no event arg, (c) a payload with wrong-typed fields (`agent_id: 5`, `last_assistant_message: ["x"]`). All three: exit 0, empty stdout/stderr, no record written to `logs/`. `tests/logger_test.py:268-276` (`test_edges`) covers 6 malformed variants the same way, subprocess-checked (`r.returncode == 0 and r.stdout == "" and r.stderr == ""`, line 63), and passes.
>
> **5. Check 6 passes.**
> - verdict: **met**
> - evidence: `python3 -m build.checks` (reproduced, exit 0) → `check 6 dependency boundary: 23 files under logger, build, upstream, dist, 0 third-party imports`, `checks: 0 failures`. `build/checks.py:26` `BOUNDARY = ("logger", "build", "upstream", "dist")` (excludes `measure/`, the one place third-party imports are allowed per `AGENTS.md`).
>
> **Checks (flow.md §3 P2)**
>
> - **10_plan.md P2.1–P2.5**: same as done-condition clauses 1–5 above — met.
> - **No record contains an unmasked home path**: **met**. `grep -c "/Users/<user>"` on all four live runs' raw `home/logs/*.jsonl` → 0 hits, despite the same string appearing 7–8 times in each run's raw `stream.jsonl` (plugin path, tool `file_path`, memory paths) — confirming masking is actually exercised, not just coincidentally absent. `mask()` (`logger/ko_quality_log.py:60-71`) replaces the literal `Path.home()` string first, then a generic `HOME_PATHS` regex (`/Users/…`, `/home/…`, one path segment) → `~`.
> - **`logs/` has no per-profile split**: **met**. All four run homes contain only `home/logs/2026-09.jsonl` directly (no subdirectory). `append()` (`logger/ko_quality_log.py:253-258`) writes to `HOME / "logs" / f"{now:%Y-%m}.jsonl"` unconditionally — no profile parameter anywhere in the path.
>
> **Supporting checks (independently reproduced, not previously claimed as done-condition)**
>
> - Live records match §12.1's field set exactly: read a raw `cc-foreground` record's keys → 29 fields, exactly the spec's YAML block, with all 5 reserved gate fields (`gate_on`, `gate_fired`, `gate_retries`, `gate_fired_on`) and all 5 removed-era-01 fields (`preset`, `instruction_lang`, `artifact_lang`, `usable`, `upstream_report`, `expect`) absent.
> - Masking additions (§12.1: phone, 주민등록번호, card, home path) are new in this stage: `git diff ffb48b3 f2293d8 -- logger/ko_quality_log.py` shows the mobile-number regex, `HOME_PATHS`, and the `Path.home()` literal-replace as newly added; the 5 secret patterns (API key, `sk-`, GitHub token, AKIA, email) predate this stage (era 01, commit `84ff6ae`).
> - `SubagentHandback` capture genuinely exercised live (not the era-01 stub): `cc-default`/`cc-foreground` sub-record `output` fields contain real Korean review text ("AI 가능성: 중간 / 신뢰도: 낮음…"), not the stub `"I sent my report to the agent that started me."`
> - `state/` cleanup at `SessionEnd`: all four live-run `home/state/` directories are empty (0 files) after the session ended, and no `logger-errors.log` exists in any of them (no exceptions during live use).
> - All three `dist/*/logger/ko_quality_log.py` copies are byte-identical to `logger/ko_quality_log.py`; all three `dist/*/hooks/hooks.json` are byte-identical to `assemble/hooks/hooks.json`, which lists only `SessionStart, UserPromptSubmit, PostToolUse, Stop, SubagentStop, SessionEnd` (no `PreToolUse`/`SubagentStart`, per §11.5).
>
> **Contradictions / open items against spec 09, 10_plan.md or flow.md**
>
> - **`design/02-validation/6-build/P2_logger.md` does not exist**, and `6-build/README.md`'s progress table still shows P2 as `—`/unstarted (`진행: ... P1 끝, P2 진행 중`) at commit `59c0f95`. `flow.md` §3 states every P has "Record: `6-build/P<n>_<name>.md`" and "the record's last commit closes the P." At the commit under verification, P2's technical work (logger, tests, checks, both live sessions) is done and reproducible, but the stage's own record-and-close step per `flow.md` had not yet happened. This is a process-sequencing gap, not a failure of any done-condition clause — it likely reflects that this verification run itself is meant to feed that record, consistent with `AGENTS.md`'s rule that "a stage's done-condition is confirmed by an independent verification run, not by the builder's own claim."
> - No other discrepancy found against 09 §11/§12.1/§11.3/§11.4/§14.2, `10_plan.md` §4 P2, or `flow.md` §1 (F1, F2)/§3 P2. The "first" Claude Code run in `live-sessions.json` (build `7e055919440959f5`, pre-`<task-notification>`-fix) shows the old bug (notification miscounted as `task`), but this is explicitly labeled as the before-fix comparison run, not the stage's evidence for done-condition 2 — the committed-logger runs (`51112680979b60c3`) are, and those are correct.
>
> I did not re-run any live Claude Code or Codex session (not needed — all clauses were decidable from existing logs plus direct, low-cost local invocations of the logger and test/check scripts).

**Builder's notes.** The verifier's account name in one grep command is replaced by `<user>` above (public repository). On condition 2's "how it could still be wrong": the background runs are recorded under Spec did not know as a harness behaviour P8 must handle; the logger writes one record per `Stop`, as 09 §11.2 specifies.

## Release-blocked

None.
