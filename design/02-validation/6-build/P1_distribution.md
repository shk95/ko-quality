# P1 — Distribution under B9

## Summary

One Claude Code plugin `ko-quality` 0.2.0 now carries both profiles as **unforced** output styles, and its three agents carry the agent-reply policy under either style (S1-A). The stamp gains `build_id` and loses `profile` and `injection_point`. `ko-rewrite` has the redirect under upstream step 1 (R3). Checks 5 and 6 are added, `server/` is gone, and `gate/` is reserved. Install docs cover selection, removal including the style selection, and Codex `multi_agent_v2`.
Done-condition: **met on all four clauses** (independent `mid` verification). Release-blocked: **0**.

## Built

| Item | Path | State |
|---|---|---|
| Profiles without `exempt`, `plugin:`, `output_style.force`; `register` restated | `assemble/profiles/*.yaml` | done |
| Build configuration: plugin names and descriptions, version, agent profile | `assemble/build.yaml` | done (new) |
| One plugin, both styles unforced, agents on agent-reply policy, `build_id` stamp | `build/claude_code.py` | done |
| Codex dists: agents on agent-reply policy in both profiles, `build_id` stamp | `build/agent_plugin.py` | done |
| ko-rewrite redirect under step 1; ko-route "active profile" | `assemble/skills/ko-rewrite/SKILL.md`, `assemble/skills/ko-route/SKILL.md` | done |
| Checks 1–6 over the new layout | `build/checks.py` | done; checks 5 and 6 shown to fail on planted violations |
| `server/` removed, `gate/README.md`, layout table | `gate/`, `AGENTS.md` | done |
| Install docs; root README install section | `assemble/install/*.md`, `README.md` | done |
| Old per-profile Claude Code dists | `dist/claude-code/{agent-reply,formal-report}/` | removed by the build |
| Run summaries | `tests/runs/02-P1/build-checks.txt`, `tests/runs/02-P1/canary-and-removal.json` | done |

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | minor | Plugin name, description and version in a new `assemble/build.yaml` / hard-coded in `build/claude_code.py` | `assemble/build.yaml`. 09 §6 says they move to "the build configuration"; a YAML file beside the profiles keeps them out of code | high | 09 §6 change 3 |
| 2 | minor | Codex plugin names: keep `ko-quality` and `ko-quality-formal` / rename | Keep. 09 §13 keeps one Codex dist per profile, and two plugins in one Codex marketplace need distinct names. The removal of `ko-quality-formal` in 09 §13 is about Claude Code | medium-high | 09 §13 |
| 3 | minor | Codex stamp: keep `profile`, drop `injection_point` / keep both | Keep `profile` (one dist per profile, so it is a property of that installation); drop `injection_point`, which the logger now derives from the `AGENTS.md` marker (§11.3). 09 §13 names only the Claude Code stamp | medium | 09 §11.3, §13 |
| 4 | minor | `build_id` inputs: `upstream/normalized`, `assemble`, `build`, `logger` / normalized and assemble only | All four. 09 says "normalized and assembled inputs"; the logger and the build code change what a record contains, so records from different logger code must be separable too. sha256 over sorted path and bytes, first 16 hex | medium-high | 09 §13, §21.1 |
| 5 | minor | ko-route step 1 wording under B9 | "the default preset of the active profile: the selected output style on Claude Code, or the `ko-quality:begin profile=…` section on Codex". No fallback when none is active: 09 names none | high | 09 §9 |
| 6 | minor | Redirect line text | Era 99's tested sentence, verbatim, as a continuation line of step 1 | high | era 99 R3, `codex-channels.json` |
| 7 | minor | Check 6 stdlib detection on Python 3.9, which lacks `sys.stdlib_module_names` | `sys.stdlib_module_names` when present, else module origin under `sysconfig` stdlib and not in `site-packages`; our own modules (repository root and the file's directory) allowed | medium | negative test: `yaml`, `numpy.linalg`, `kiwipiepy` flagged |
| 8 | minor | Removal doc: delete the `outputStyle` line / run `/output-style default` before uninstalling | Both written; the deletion is the step tested. `/output-style default` is untested | medium | removal run |
| 9 | minor | Run summaries under `tests/runs/P1/` (F14) / `tests/runs/02-P1/` | `tests/runs/02-P<n>/`. Era 01's P1–P7 records already occupy `tests/runs/P<n>/`, and era 02's other runs are prefixed `02-` | high | tree |
| 10 | minor | Install docs' logging paragraph: describe the 0.1.0 logger / the §11–§12 logger P2 builds | The P2 logger (one `logs/` file per month, `expanduser`, the added masks). 0.2.0 is not released before P2 | medium-high | 09 §11.4, §12.1 |

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V1 | mid (Sonnet 5) | Verification of the P1 done-condition (outside the cap), on an isolated worktree at `804479d` | 124,208 | All four clauses and all four checks **met**; reported the missing P1 record as a contradiction (written after verification by design) |

Exploration runs: 0 of 4.

## Cost

| Run | Model | USD |
|---|---|---|
| Canary: no selection | claude-sonnet-5 | 0.061 |
| Canary: `agent-reply` selected | claude-sonnet-5 | 0.073 |
| Canary: `formal-report` selected | claude-sonnet-5 | 0.139 |
| Canary: delegation under `agent-reply` | claude-sonnet-5 | 0.334 |
| Canary: delegation under `formal-report` | claude-sonnet-5 | 0.401 |
| Removal: three sessions | claude-sonnet-5 | 0.133 |
| **Total** | | **1.14** (no ceiling set for P1) |

## Differs from spec

- **Run summaries live in `tests/runs/02-P1/`**, not `tests/runs/P1/` as F14 writes, because era 01's step records hold that path (decision 9). Later steps follow the same prefix.
- **The agent YAML files still say `compose: [profile.policy, profile.blocks]`.** Nothing reads the field; the build takes the agent policy from `assemble/build.yaml` `agent_profile`. Left as is, since 09 §17.3's rule ("a field nothing reads is not kept") is written for cases, and changing it has no effect.

## Spec did not know

- **User-scope plugins load in every headless run.** This machine has a user-scope plugin enabled, and it appeared in `init.plugins` in every canary and removal session. It ships no output style, so the canaries are unaffected. For P8, "arm A: plugin not installed" still means every other user-scope plugin is present.
- **A style selection left behind after removal is silent.** With the plugin uninstalled and the marketplace removed, a session with `outputStyle: "ko-quality:agent-reply"` still left in `settings.local.json` started with no error or warning, and `init.output_style` still reported `ko-quality:agent-reply`. 09 §13 expected "the next session asks for a style that no longer exists"; what is measured is that nothing tells the user. After the documented deletion `init.output_style` is `default`. This measures 09 §14.2's B9 removal row.
- **Removal traces are unchanged on 2.1.274:** an empty `"extraKnownMarketplaces": {}` in user settings and an orphaned cache marked `.orphaned_at`. `uninstall --scope local` also leaves `"enabledPlugins": {}` in the project's `settings.local.json`. Restored from a snapshot, and the cache moved to Trash.
- **Canaries route, they do not show compliance.** The short `formal-report` reply carried its canary and used 하십시오체 but no `사용자님`. Whether the policy is followed is P8's measurement, not P1's.
- **An isolated verification worktree starts from `master`**, not from `dev`. The verifier detached to the commit it was given. Later verification prompts name the commit explicitly.

## Verification

Run V1, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned:

> Verification of build stage P1 (Distribution under B9), era 02-validation. I checked out commit 804479d in the worktree (it had been sitting on master/cea6641, not dev/804479d, so I detached to 804479d first — this touched only my own worktree, never the main checkout), symlinked upstream/.cache from the main checkout, and both read the recorded logs and independently reran the reproduction commands.
>
> **Done-condition clauses (10_plan.md §4 P1)**
>
> **1. Two consecutive builds byte-identical, checks 1–6 pass — MET.**
> Evidence: `tests/runs/02-P1/build-checks.txt` records `diff -r build1 build2` → "diff exit 0" and `python3 -m build.checks` → "checks: 0 failures" (checks 1–6 all print ok). I independently reran `python3 -m build.claude_code && python3 -m build.agent_plugin` twice, copied `dist/` between runs, and got `diff -r` exit 0 myself; `python3 -m build.checks` reproduced identically ("check 1 re-extraction: check: 11 files, 1012 fragments, 0 failures" … "checks: 0 failures"). My rebuild's `build_id` (`34ca2331593d24e8`, in `dist/claude-code/ko-quality/ko-quality.stamp.json`) is byte-identical to the one recorded in the canary run — strong evidence the committed tree is exactly what was tested. `build_id()` in `build/claude_code.py:252` is a sha256 over build inputs' path+bytes, explicitly not time-based, which is why rebuilds are byte-identical by design.
> How it could still be wrong: none found; this was directly reproduced twice, independently.
>
> **2. No style without selection; each style applies when selected; shown by canary not settings echo — MET.**
> Evidence (raw `stream.jsonl`, not just the summary): `no-selection` run — `grep -o "KQ-CANARY-*"` over the whole stream returns nothing; `sel-agent-reply`'s raw `"result"` field literally begins `"KQ-CANARY-P1-style-agent-reply-1\n\n리스트는 대괄호..."`; `sel-formal-report`'s raw result begins `"KQ-CANARY-P1-style-formal-report-1\n\n리스트(list)는..."`. The canary is a token appended to the style-body file in a scratch copy (`canary.py`, never touching `dist/`), so its appearance in the model's actual reply text is not a settings echo.
> How it could still be wrong: only 1 prompt per arm was run; a flakier/longer conversation might not repeat the "begin every reply" instruction on every turn (seen in clause 3 below), but for this single-turn check it's conclusive.
>
> **3. Shipped agent's reply carries the agent-reply policy under either selected style — MET.**
> Evidence: `deleg-agent-reply` and `deleg-formal-report` both show `handback_tokens: ["KQ-CANARY-P1-agent-korean-reviewer-1"]`. I pulled the raw `SubagentHandback` tool-input from `deleg-agent-reply/stream.jsonl`: `{"message": "KQ-CANARY-P1-agent-korean-reviewer-1\n\n한 줄 판정: ..."}` — the agent's actual report begins with its file's canary line under both styles. `dist/claude-code/ko-quality/agents/korean-reviewer.md` (read directly) confirms the shipped file's system prompt starts with the Korean agent-reply policy body (S1-A), matching spec's "the system prompt is the same string in every dist, and it starts with the agent-reply policy body" (09_toolkit_spec.md:508).
> How it could still be wrong: only one of the three shipped agents (korean-reviewer) was exercised by canary; korean-writer/korean-editor were canary-marked but never invoked in a live run, so their policy-carrying is untested by canary (only by check 3/4's static comparison).
>
> **4. Removal leaves no style request behind when documented steps are followed — MET.**
> Evidence, raw `removal/log.txt`: after `claude plugin uninstall` + `marketplace remove` but before deleting the `outputStyle` line, `init output_style: ko-quality:agent-reply` still shows (session `removed-style-left`) — this is the honestly-reported *incomplete* case. After the final documented step (deleting the `outputStyle` line, per `assemble/install/claude-code.md`'s "제거" section: "스타일 선택도 지웁니다... outputStyle 줄을 지우거나"), `init output_style: default` (session `removed-style-cleared`). `removal.sh` shows all three documented removal steps were actually executed in order. `assemble/install/claude-code.md` is byte-identical to `dist/claude-code/README.md` (diff exit 0), confirming the doc tested is the doc shipped.
> How it could still be wrong: this measures one project's `settings.local.json`; a project using committed `settings.json` or `--scope project` install was not exercised, though the doc's step covers "또는 `.claude/settings.json`" symmetrically.
>
> **Checks (flow.md §3 P1)**
>
> - **`10_plan.md` P1.1–P1.4** — met, as above.
> - **`plugin.json` name is `ko-quality`** — MET. The single Claude Code `.claude-plugin/plugin.json` has `"name": "ko-quality"`; `dist/claude-code/.claude-plugin/marketplace.json` lists exactly one plugin, `ko-quality`. (The two Codex `agent-plugin` dists correctly still have `ko-quality`/`ko-quality-formal` respectively — P1's scope only merges the Claude Code side, per plan text, so this is not a contradiction.)
> - **No `force-for-plugin` anywhere in `dist/`** — MET. `grep -r "force-for-plugin" dist` returns nothing (exit 1), both in the log and in my own rerun.
> - **Codex dists still build and check 2–4 hold across them** — MET. `python3 -m build.agent_plugin` succeeded; checks output shows `check 2 agent-reply`, `check 2 formal-report`, `check 3 agents: 3 agents across 3 dists`, `check 4 skills: compared 3 dists`, all inside "checks: 0 failures".
>
> Also spot-checked artifacts: `assemble/profiles/*.yaml` have no `exempt`/`plugin:`/`output_style.force` keys and a plain-text `register`; Claude Code stamp (`dist/claude-code/ko-quality/ko-quality.stamp.json`) has `build_id` and no `profile`/`injection_point`, version `0.2.0`; Codex stamps correctly retain `profile` (scope was Claude Code stamp only); `server/` is gone, `gate/README.md` exists; `build/checks.py` contains check 5 (agent names) and check 6 (dependency boundary) as literal functions.
>
> **Contradiction found (not fixed, per instructions)**
>
> **No P1 build record was ever committed.** `design/02-validation/6-build/` contains only `README.md`; there is no `P1_distribution.md` (or similarly named) file, and the progress table in that README still shows `—` in every column for the P1 row. This contradicts:
> - `flow.md` §3, "Common to every P": *"Record: `6-build/P<n>_<name>.md` with the two fixed tables... Commit: one step per commit on `dev`; the record's last commit closes the P."*
> - `6-build/README.md`'s own rules ("P마다 커밋하고 P마다 기록한다" / "P가 끝날 때마다 한 행을 채웁니다").
> - `10_plan.md` §1: *"After a step: record findings in `6-build/P<n>_<name>.md`... A done-condition is confirmed by an independent verification run (`mid`, outside the cap), never by the builder's claim."*
>
> Concretely, three P1 commits exist (`da84fbd`, `ffb48b3`, `804479d`), and the last one only adds `tests/runs/02-P1/*` summaries — no record file, no verification-run transcript, no Decisions/Subagent-runs/Cost tables. This means the required independent `mid`-tier verification run (outside the cap, mandated before the record is written) either did not happen or was not recorded anywhere in the tree — I could not find its verdict in the repository. That is exactly the gap this task itself is filling in from outside. Whether this reflects the stage genuinely being unfinished (record-writing step still pending) or a process omission, I can't tell from the tree alone — but as of commit 804479d, the stage is not formally closed per flow.md/6-build's own rules, even though the underlying evidence for the done-condition and named checks holds up.
>
> No other contradiction to spec 09 / 10_plan.md / flow.md was found in the P1 artifacts themselves.
>
> **Token usage:** I don't have visibility into a precise token counter for this sub-session; based on the volume of tool output read (several full documents, multiple JSON logs, and reproduced build/check runs), I estimate roughly 60–90k tokens consumed in this verification run.

**Builder's note on the contradiction:** the flow is build → commit → verification → record → commit (`6-build/README.md` handoff). The record did not exist at `804479d` because verification comes before it; this file closes P1. The harness counted 124,208 tokens for the run.

## Release-blocked

None.
