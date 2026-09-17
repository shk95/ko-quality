# P8 — Corpus generator and pilot

## Summary

`corpus/` generates headless `claude -p` sessions through the shipped logger in three arms: A a logger-only plugin, B the built plugin with no style, and C a selected style switched to the other profile after the first prompt. Each turn gets an annotation. The prompt set covers all nine strata of 09 §18.3 and records its gaps. The canaries passed in every arm, and a deliberately mislabelled canary was rejected. The pilot (`pilot-01`, 81 sessions, 108 prompt turns) produced 139 log records, and every one joins an annotation and a derived record. The pilot report and the F9 power calculation are reproducible from the corpus home: 63 sessions per arm wherever variance was observed. P8 cost $12.87 of $21.
Done-condition: **met on all four clauses** (independent `mid` verification). Release-blocked: **0**.

## Built

| Item | Path | State |
|---|---|---|
| Generator: arms, per-session scratch project, stream-json one line per turn, arm check, task check, per-turn annotations | `corpus/generator.py`, `corpus/__main__.py` | done (`e288102`) |
| Canary per arm, with a mislabel mode | `corpus/generator.py` `canary()` | done |
| Prompt set, 9 strata × 3, coverage and gaps | `corpus/prompts/set-1.json` | done |
| Fixture project for coding strata (synthetic) | `corpus/fixtures/project/` | done |
| README (Korean) | `corpus/README.md` | done |
| Pilot report: join, exclusion on generated replies, false positives per measurement and per arm, hand-back, truncation, variance, power | `measure/pilot.py`, `python3 -m measure pilot` | done |
| Pilot batch, 81 sessions | corpus home `~/.ko-quality-corpus` (outside the tree) | done |
| Run summaries | `tests/runs/02-P8/`: canaries, sessions, run report, pilot report, cost ledger | done (`4018280`) |

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | Arm A ("not installed") still needs the logger, or it leaves no record: a logger-only plugin / a hook in the scratch project's settings | **Logger-only plugin**: the shipped `hooks/` and `logger/`, no stamp, no styles, skills or agents. The logger records `plugin_present: false`, which is what 05 said separates A. The hook command is byte-identical to B and C | medium-high | 09 §12.1, §18.1; 2-exploration 05 |
| 2 | major | How to get deliberately correct and defective Korean through the real pipeline | **Echo prompts**: the prompt asks for a text we wrote to be copied back unchanged, so the reply holds known zones and known defects. Replies reproduced the text 24/24 | medium | 09 §18.3; P8.3 needs labels on generated replies |
| 3 | major | Arm C session shape | Prompt i under one profile, `/output-style` to the other, prompt i+1 of the same stratum; the starting profile alternates. A and B sessions take prompt i alone. Each C session yields one turn per profile | medium | 09 §18.2 ("one process yields both profiles' turns") |
| 4 | major | Feeding stream-json input: all lines at once / one line per turn | **One line per turn**, after the previous `result` and after every background task has notified. Found on the first pilot start: lines written at once were queued into a running tool turn and merged, so turns and records no longer lined up. That start was stopped after 6 sessions and set aside | high | stopped run; three fix-test runs |
| 5 | minor | Subagents could not read the plugin's skill references (`permission_denied: workingDir`) | `--add-dir <plugin>` in every arm | high | fix test 2 stream |
| 6 | minor | A background agent's notification turn | Folded into the prompt turn before it (`notification_turns`); annotations map to distinct `turn_key`s, so the turn's second main record joins the same annotation | medium | fix test 3 |
| 7 | minor | Annotation fields beyond §12.2 | Added `batch_id`, `build_id`, `stratum`, `turn_key`, `turn_index`, `first_turn_after_switch`, `init_output_style`, `arm_check`, `task_matches_prompt`, `turns_complete`, `notification_turns`, `main_records_in_turn`, `cost_usd`, `is_error`, `log_record_found` | medium | 09 §18.2 (the first turn after a switch is annotated), §18.4 item 3 |
| 8 | minor | Tools | `--permission-mode acceptEdits`, no Bash, `--max-turns 8`, `--model claude-sonnet-5` | medium | F1, F4 |
| 9 | minor | Pilot runs sequentially | Sequential (56 minutes) | high | one writer per log line |
| 10 | minor | False-positive rate for a number | A zero line per primary value (`count > 0`, `ratio > 0`, `balanced is false`, `levels_present > 1`). Six measurements have no zero line and report their distribution | medium | 09 §15.1 |
| 11 | minor | Variance unit | Session mean within a (stratum, arm, profile) cell, SD pooled over cells with ≥ 2 sessions | medium | 10_plan.md P9.1 (session-level) |
| 12 | minor | Homes | Corpus `~/.ko-quality-corpus`, canaries `~/.ko-quality-corpus-canary`, both outside the tree and outside `~/.ko-quality` | high | 09 §18.2, §20 |

Exploration runs: 0 of 4 subagent runs. The live fix tests (three, $0.82) are in the cost ledger.

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V8 | mid (Sonnet 5) | Verification of the P8 done-condition (outside the cap), isolated worktree at `4018280` | 153,948 | All four clauses **met**; cost check met; noted the canary checks style markers only, power computed also for measurements with no zero line, `code_version` hashing an untracked file, no unit test for `pilot.py` |

## Cost

| Run | USD |
|---|---|
| Probe: stream-json style switch | 0.0937 |
| Canaries before the generator fix (3 arms + mislabel) | 0.2758 |
| Stopped pilot start (5 sessions reported; a 6th killed mid-run, cost not reported) | 0.4728 |
| Fix tests 1–3 | 0.8233 |
| Canaries on the committed generator (3 arms + mislabel) | 0.2763 |
| `pilot-01`, 81 sessions | 10.9270 |
| **Total** | **12.87 of $21** (F10) |

Mean cost per session: A $0.073, B $0.126, C $0.206.

## Differs from spec

- **Annotations carry more fields than §12.2** (decision 7).
- **Arm A is a logger-only plugin**, not "not installed" in the literal sense (decision 1).
- **Summaries are under `tests/runs/02-P8/`**, as the user set for this era.

## Spec did not know

- **Headless stream-json input written all at once merges turns** when a turn runs tools.
- **`/output-style` over stream-json** yields its own `init` and `result` and no hook record.
- **Headless subagents cannot read a `--plugin-dir` plugin's files** without `--add-dir`. Era 01 and P1's canaries did not exercise a skill that reads references inside a subagent.
- **The model sometimes runs a shipped agent in the background.** The main turn then replies early ("결과가 도착하면 알려 드리겠습니다"), and a notification turn writes a second main record under the same `turn_key`: 14 of 108 turns (delegation 7, document 6, paste-in 1).
- **Hand-back stub: 0 of 17 sub records** (Wilson 95% [0, 0.18]), across all three agents. 09 §14.2's open question leans toward "real reports reach `SubagentStop` or `SubagentHandback`" on 2.1.274; 17 is small.
- **Truncation: 0 of 139 records.** L2's 100,000-character cap was never reached.
- **Exclusion on generated replies: 0 false negatives on 36 labelled spans** (number 20, code 4, quotation 4, proper noun 4, abbreviation 4).
- **False positives on correct Korean (n = 12 main records):** 0 for 18 measurements. `comma_rate` 4/12, `genitive_ui_ratio` 4/12, `spacing_errors` 4/12. `particle_absence_ratio` 12/12: correct Korean has non-zero absence (noun compounds, P6), so zero is not its clean value and a rate against zero says nothing.
- **F9's standardized effect makes σ cancel:** n = 2 (2.8016 / 0.5)² = 62.79 → **63 sessions per arm cell for every measurement with observed variance.** Two measurements showed no variance: `header_formula` (almost no headings) and `quote_balance` (always balanced). At pilot costs, 63 per (stratum, arm) cell over 27 cells is about $229, above P9's $200 ceiling.
- **The user's own global plugin loads in every arm** (a user-scope plugin in `init.plugins`), equally in A, B and C.

## Verification

Run V8, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned:

> Verified at commit 4018280 (confirmed via `git log -1 --oneline` → "4018280 P8: pilot-01 (81 sessions) with canaries, pilot report and power calculation ..."). No tracked files modified during verification; all data checks used a copy of the corpus home under `$TMPDIR`, never the original `~/.ko-quality-corpus`. No new `claude` sessions were run — a verdict was reachable from static artifacts plus reproduction of the offline pipeline.
>
> ## Done-condition clauses (10_plan.md §4 P8)
>
> **1. Every arm's canary passes; a marker in the wrong arm is rejected; rejection path shown once.**
> verdict: **met**, with a real gap in what the canary actually checks.
> evidence: `tests/runs/02-P8/canary-pilot-01.json` — all three runs (A, B, C) have `"pass": true`, verdict "batch accepted...". `tests/runs/02-P8/canary-pilot-01-mislabel.json` — setup B labelled C: both checks `"pass": false`, `"rejected": true`, verdict "batch rejected: a marker is missing or in the wrong arm". Both are real live runs (real `session_id`s, non-zero `cost_usd`), matching cost-ledger.json lines "canaries, committed generator (3 arms) $0.2066" and "mislabelled canary, committed generator $0.0697".
> how it could still be wrong: `corpus/generator.py` `plugin_copy()` (lines 56–68) writes a marker into **both** each style body (`-style-<name>`) and each agent body (`-agent-<name>`), per flow.md F3 ("each style body and each agent body"). But `canary()`'s check loop (lines 354–358) only searches reply text for `f"{marker}-style-{p}"` tokens — it never builds or checks an `-agent-` token, and the canary prompt (`CANARY_PROMPT`, a generic question) never triggers delegation anyway. So the "per-location" marker device that flow.md F3 describes is only exercised/verified for the style-routing channel; an agent-body routing bug (e.g. an agent's policy text leaking into the wrong arm, or an agent file wrongly present/absent) would not be caught by this canary as built. The done-condition's literal wording ("a marker in the wrong arm is rejected") is satisfied for the scenario actually tested (style selection), but is narrower than the marker scheme F3 specifies.
>
> **2. Every log record in the pilot joins an annotation and a derived record.**
> verdict: **met**.
> evidence: `tests/runs/02-P8/pilot-01-report.json` → `"join": {"log_records": 139, ..., "records_without_annotation": 0, "records_without_derived": 0, "all_joined": true}`. Independently confirmed against the raw corpus home: `wc -l ~/.ko-quality-corpus/{logs,annotations,derived}/2026-09.jsonl` → 139 / 108 / 139, and all annotation rows carry `"batch_id": "pilot-01"` and the same `build_id` as `dist/claude-code/ko-quality/ko-quality.stamp.json` (`51112680979b60c3`), i.e. the home held only pilot-01 data, not contaminated by earlier fix-test/aborted runs.
> how it could still be wrong: the "join" is many-to-one — 108 annotation rows cover 139 log records via `(session_id, turn_key)` matching in `measure/pilot.py::load/join_report` (lines 97–114), because sub-to-orchestrator records and duplicate "notification-turn" main records share a `turn_key` with their parent annotated turn. This is a defensible reading (an annotation identifies which arm/stratum/profile a turn belongs to, and sub records inherit that), but it is not a literal 1-record-to-1-annotation join; a stricter reading of the done-condition could dispute it. I judge it correctly reflects the schema's intent (§12.1's `turn_key` field exists precisely to let sub records be attributed to their turn).
>
> **3. Pilot report gives: exclusion false negatives, per-measurement false-positive rate on the deliberately-correct stratum, hand-back rate, truncation rate, per-measurement variance.**
> verdict: **met**.
> evidence (`tests/runs/02-P8/pilot-01-report.json`):
> - exclusion: `"exclusion_on_generated_replies": {"echo_records": 24, "text_reproduced_verbatim": 24, "zones": {...all zones "false_negatives": 0...}}` — 36 total labelled spans (20+4+4+4+4), 0 missed. Matches commit message "0 exclusion false negatives on 36 labelled spans."
> - false-positive rate: `"false_positive_rate_correct_stratum"` computed only over `a["stratum"] == "correct-korean"` (measure/pilot.py line 144), reported overall and per arm/profile with Wilson 95% intervals (per §16.1's "per arm" requirement), e.g. `em_dash_count`: `"A/none"`, `"B/none"`, `"C/agent-reply"`, `"C/formal-report"`, `"all"` each with `fires/n/fp_rate/wilson_95`.
> - hand-back: `"hand_back": {"sub_records": 17, "stub_outputs": 0, "rate": 0.0, "wilson_95": [0.0, 0.1843]}`. Verified independently against raw logs: all 17 sub-to-orchestrator records span all three shipped agents (`korean-writer`: 9, `korean-editor`: 5, `korean-reviewer`: 3), none equal to the stub string `"I sent my report to the agent that started me."` (the stub string is grounded in `tests/logger_test.py:25` and `tests/runs/02-spec/hook-payloads.json`, not invented for P8).
> - truncation: `"truncation": {"records": 139, "records_with_truncated_calls": 0, "rate": 0.0}`.
> - per-measurement variance: `"variance_and_power"."measurements"` reports `pooled_sd` per measurement (e.g. `em_dash_count: 1.506605`).
> how it could still be wrong: all false-positive rates in the correct-Korean stratum came out at exactly 0 across every measurement shown; with n=12 (Wilson upper bound up to 0.24) this is plausible for a pilot but is a weak signal — a defect in the FP-counting logic that always returns "no fire" would look identical. I spot-checked the `fires()`/`value_of()` logic by hand against `derived/` features for `em_dash_count` and it is consistent, but there is no dedicated unit test for `measure/pilot.py`'s functions (see contradictions below).
>
> **4. Sessions per arm via normal-approximation power calculation, for measurements that can carry a `watch:` candidate; α/power/effect set in 5-preflight; reproducible; parameters recorded.**
> verdict: **met**, with an overreach beyond what the clause names.
> evidence: `measure/pilot.py` lines 29, 182–208: `ALPHA, POWER, EFFECT_SD = 0.05, 0.8, 0.5  # flow.md F9`, formula `n = 2 (z_(1-α/2)+z_(1-β))² σ² / δ²` with `δ = 0.5σ`. Report: `"z_sum": 2.801585, "alpha": 0.05, "power": 0.8, "effect": "δ = 0.5 × pooled session-level SD (flow.md F9)"`. I recomputed by hand from the recorded `z_sum` and `pooled_sd` alone (no raw data needed): for `em_dash_count`, `n = 2*(2.801585/0.5)² = 62.79 → 63`, matching `sessions_per_arm: 63` exactly. I also **fully reproduced the pilot report from scratch**: copied `~/.ko-quality-corpus` to a scratch dir, ran `VPY -m measure run --home <copy>` then `VPY -m measure pilot --home <copy> --batch pilot-01`, and `diff`'d the output against `tests/runs/02-P8/pilot-01-report.json` — **byte-identical**. The run-report (`measure run --report`) was identical except for one field, `code_version` (explained below). α/power/effect are recorded in flow.md F9 as "user, 2026-09-17, U1" and echoed in `09_toolkit_spec.md §22.2`'s open-decision table as "Answered: F9's proposal."
> how it could still be wrong: the clause restricts the computation to "measurements that can carry a `watch:` candidate." Per spec §15.1/§15.7, a measurement with no zero line ("no false-positive rate, no `watch:` value") can never carry a candidate. `measure/pilot.py`'s `PRIMARY` dict marks 6 of 25 measurements with `rule: None` (no zero line): `english_ratio`, `sentence_len_var`, `honorific_address`, `noun_run_length`, `ending_monotony`, `pos_ngram_diversity`. `variance_and_power()` computes `pooled_sd`/`sessions_per_arm` for **all 25** measurements uniformly, including these 6 that structurally cannot carry a `watch:` candidate. This is over-inclusion, not under-inclusion (all eligible measurements are covered), and nothing writes a `watch:` value in P8 (confirmed `assemble/profiles/*.yaml` has no `watch:` key at this commit), so it does not violate the spec's "no threshold without an FP rate" rule — but it is broader than the clause's own wording of "for the measurements that can carry a candidate."
>
> ## Checks (flow.md §3 P8)
> - `10_plan.md` P8.1–P8.4: covered above, same verdicts.
> - "running cost stays under F10's pilot share" ($21 ceiling): **met**. `tests/runs/02-P8/cost-ledger.json`: `"total_usd": 12.869`, itemized across probes, pre-fix canaries, aborted pilot attempts, fix tests, final canaries, and the 81-session pilot ($10.927) — all counted as F10 requires ("canary and probe runs count"). $12.869 < $21.
>
> **Release-blocked:** condition (clause 1 fails) does not hold — not release-blocked.
>
> ## Contradictions / deviations found (not fixed, just reported)
>
> 1. **No P8 build record exists yet, and `design/02-validation/6-build/README.md`'s progress table still shows all dashes for P8** ("P8 | Corpus generator and pilot | — | — | — | — | — |"). AGENTS.md requires "Each build step ends with a commit and a record in `6-build/`," and 6-build/README.md's own rule is "P마다 커밋하고 P마다 기록한다" (record closes on the P's last commit), with "완료 조건은 독립 검증 run이 확인한다... 판정 원문을 기록에 그대로 붙입니다" (the verification run's verdict is pasted verbatim into the record). Since I am that independent verification run, this is very likely a pending step (the record/table row is written after my verdict lands) rather than a violated invariant — but as of commit 4018280 itself, the record is missing.
> 2. **The canary's marker check only covers the style channel, not the agent channel** it also marks (see clause 1 above) — `corpus/generator.py` lines 56–68 vs 354–358.
> 3. **`measure/runner.py::code_version()` (lines 19–24) hashes every `*.py` file under `measure/`, tracked or not.** Re-running `measure run` from a clean checkout of 4018280 reproduced every field of `pilot-01-run-report.json` exactly except `code_version` (committed: `1802e97d460f6402`, reproduced: `0f6c8ac10d2953e7`). Root cause: the outer working copy (not this worktree) has an **untracked** `measure/batch.py` (visible in the conversation's `git status`, presumably early P9 work-in-progress) that gets hashed in when the report was generated there, but is absent from a clean checkout of the commit. This means `code_version` in a run-report is not a pure function of the commit — a cosmetic reproducibility gap, not a correctness one (every substantive field matched).
> 4. **No dedicated unit tests for `corpus/generator.py` or `measure/pilot.py`**, unlike prior stages (`tests/logger_test.py` for P2, `tests/measure_runner_test.py`/`cases`/`exclusion_cases`/`separation` for P4–P6). Confidence in `pilot.py`'s `wilson()`, `fires()`, `variance_and_power()` rests on my manual re-derivation and the full-report reproduction, not on a checked-in test. Not itself a spec/plan violation (none of P8's scope items or done-conditions name a test file), but a discontinuity from the project's established pattern.
> 5. No other scope creep found: the P8 commits (e288102, 4018280) touch only `corpus/*`, `measure/{README.md,__main__.py,pilot.py}`, and `tests/runs/02-P8/*` — `measure/exclusion.py`, `measurements.py`, `runner.py`, `derived_fields.py` (P4–P6 territory) are untouched, and no `watch:` keys were added to `assemble/profiles/*.yaml` (correctly deferred to P9). No real/personal text or paths found in any committed P8 artifact (checked every string >60 chars in `tests/runs/02-P8/*.json` and grepped for home-directory/user-name patterns — none found), satisfying F14.
>
> ## Key files (absolute paths)
> - <worktree>/corpus/generator.py
> - <worktree>/corpus/__main__.py
> - <worktree>/corpus/prompts/set-1.json
> - <worktree>/measure/pilot.py
> - <worktree>/measure/__main__.py
> - <worktree>/measure/runner.py
> - <worktree>/tests/runs/02-P8/pilot-01-report.json
> - <worktree>/tests/runs/02-P8/pilot-01-run-report.json
> - <worktree>/tests/runs/02-P8/pilot-01-sessions.json
> - <worktree>/tests/runs/02-P8/canary-pilot-01.json
> - <worktree>/tests/runs/02-P8/canary-pilot-01-mislabel.json
> - <worktree>/tests/runs/02-P8/cost-ledger.json
> - <worktree>/design/02-validation/6-build/README.md
> - ~/.ko-quality-corpus/{logs,annotations,derived}/2026-09.jsonl (read-only reference, outside tree)

**Builder's notes on the findings:**
1. The record is written after verification.
2. **The canary checks style markers only.** Agent markers are written and never checked, and the canary prompt does not delegate. The done-condition is about arms, and the arm difference between A and B/C for agents is whether the agents exist. P9's canary adds a delegation turn and checks the agent marker: present in B and C, absent in A.
3. **Power for measurements with no zero line:** reported because it costs nothing; P9 reads it only for measurements that can carry a candidate.
4. **`code_version` hashes untracked files under `measure/`.** The pilot's run report was produced with P9's uncommitted `measure/batch.py` present. The substantive fields reproduce. Carried to review; P9's reports are produced from a clean tree.
5. No unit test for `pilot.py`: its output was reproduced byte for byte by V8. Carried to review.

## Release-blocked

None.
