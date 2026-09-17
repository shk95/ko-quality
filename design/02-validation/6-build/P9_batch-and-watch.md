# P9 — Sized batch and `watch:` candidates

## Summary

`batch-01` ran 1,458 sessions: 18 rounds over 81 (prompt, arm) cells, which is 54 sessions per (stratum, arm) cell, 4 at a time. It cost $191.11 including canaries, against the $200 ceiling. The pilot's power calculation asked for 63 per cell (about $229.5), so the batch ran at the size the ceiling allowed. Achieved power is 0.738 for a 0.5 SD effect, and the results are **underpowered**. Six sessions failed a turn check and are excluded whole. Per measurement, within stratum and layer, `measure/batch.py` reports B − C and A − B with session-level bootstrap intervals (10,000 resamples, seed 20260917) and false-positive rates with Wilson intervals. Six measurements meet 09 §15.7's two conditions, and their candidates are written with `_meta` in both profiles. The `ruleset` comparison is recorded.
Done-condition: **met on all three clauses** (independent `mid` verification); release-blocked handling met. Release-blocked: **1** (the batch was capped by the budget).

## Built

| Item | Path | State |
|---|---|---|
| Batch analysis: B − C per profile and A − B per stratum and layer, agent layer on sub records, bootstrap, Wilson, candidates | `measure/batch.py`, `python3 -m measure batch` | done (`0b7b303`, `274c129`) |
| Generator: `--replicates` in rounds, `--jobs` under a ceiling that counts sessions in flight | `corpus/generator.py`, `corpus/__main__.py` | done (`0b7b303`) |
| Canary: one delegation per arm, agent marker checked (P8 V8) | `corpus/generator.py` `canary()` | done; all six runs pass, mislabel rejected |
| Sized batch `batch-01` | corpus home `~/.ko-quality-corpus-batch` (outside the tree) | done, 1,458 sessions |
| `watch:` candidates with `_meta` | `assemble/profiles/agent-reply.yaml`, `formal-report.yaml` | done (`274c129`) |
| Rebuild after the profile change | `dist/` stamps (`build_id` `51112680979b60c3` → `12ccf56e8e070cfa`) | done; second build byte-identical; checks 1–6 pass |
| `ruleset` revisit | `tests/runs/02-P9/ruleset-revisit.md` | done |
| Reports | `tests/runs/02-P9/`: batch report, summary (sizing, power, cost, exclusions), run report, sessions, canaries | done (`1ce4c82`) |

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | Batch size: 63 per cell as the pilot computed (≈ $229.5, above the ceiling) / the size the ceiling allows | **54 per (stratum, arm) cell**, 18 rounds × 3 prompts. Rounds run over every cell, so a ceiling stop would still leave the cells balanced. Release-blocked by the plan's own fallback | high | 10_plan.md P9; F10; pilot cost per cell $3.64 |
| 2 | major | Run time: sequential (≈ 17 h) / concurrent | **4 jobs.** Each record is one `write` to an `O_APPEND` file; every one of 2,392 log lines parsed | medium-high | 5-minute health check; run report |
| 3 | major | Candidate condition (2), "a non-zero B − C difference" | Its 95% bootstrap interval excludes zero, in at least one (stratum, profile) | medium | 09 §15.7 |
| 4 | major | Candidate value: 09 §15.7 gives the shape, not the rule | 95th percentile of arm C session means in the correct stratum for that profile (`max`); the 5th percentile (`min`) where the defect side is low. The value is a candidate nobody reads | low-medium | 09 §15.1, §15.7 |
| 5 | minor | Candidate condition (1), "an observed false-positive rate" | The measurement has a zero line and correct-stratum records. `particle_absence_ratio` qualifies with a rate of 1.0, which is observed but says the zero line is not its clean value (P8) | medium | 09 §15.1 |
| 6 | minor | Sessions that failed a turn check | Excluded whole: 6 sessions, 8 annotations, 7 log records. Five reached `max_turns` 8 in one turn (that turn left no main record, and the next turn's record was matched to the wrong prompt); one delegation session produced a second `result` without a detected `task_notification`, so its turn count did not match | high | annotation checks (P8 decision 7) |
| 7 | minor | Separate corpus home per batch | `~/.ko-quality-corpus-batch`; batches are never pooled, and the pilot home stays as it was | high | 09 §18.4 item 3 |
| 8 | minor | Where candidates live, given `mini_yaml` | Block maps under `watch:` (the reader has no flow maps); values parse as strings, and nothing reads them | high | `build/mini_yaml.py` |

Exploration runs: 1 of 4 (R9-1, `ruleset`).

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| R9-1 | mid (Sonnet 5) | `ruleset` revisit (09 §17.4): clone at `05ce76d`, count and classify rules, coverage against this repository, cost, licence | 157,544 | 136 rules (not 115); ~63 tied to one fictional example; 4 covered, ~4 classes partly covered; the cheapest high-value gap is §10 대화 잔재; adoption would bring the first NOTICE obligation |
| V9 | mid (Sonnet 5) | Verification of the P9 done-condition (outside the cap), isolated worktree at `1ce4c82` | 187,555 | All three clauses **met**; F9–F11, F14 met; batch report reproduced byte for byte; noted `ko.preserve` and `delegation_prompt_*` outside the analysis, `particle_absence_ratio`'s candidate at a false-positive rate of 1.0, and a summary file written by an inline script |

## Cost

| Run | USD |
|---|---|
| Canaries: 3 arms style + 3 arms agent channel | 0.8314 |
| Mislabelled canary | 0.0701 |
| `batch-01`, 1,458 sessions | 190.2118 |
| **Total** | **191.11 of $200** (F10) |

## Results (for review)

Session means, B − C, 95% bootstrap interval. Only intervals that exclude zero are listed. The unit is the session. Arm C sessions contribute one turn per profile.

| Measurement | Strata where B − C ≠ 0 (both profiles unless noted) | Direction |
|---|---|---|
| `em_dash_count` (per 100 어절) | conversation (+1.58), english (+1.57), delegation (+0.95/+0.90), paste-in (+0.76/+0.74), coding-reply (+0.53/+0.59), document (+0.18) | **policy removes em dashes** |
| `noun_ending_ratio` | paste-in (+0.19/+0.20), delegation (+0.12/+0.14), coding-reply (+0.07/+0.09), document and conversation (agent-reply) | **policy reduces noun-phrase endings** |
| `particle_absence_ratio` | coding-reply, conversation, delegation, paste-in (+0.12 to +0.14) | **policy reduces particle absence** |
| `speech_level` (levels present) | conversation (+0.43/+0.61), document (+0.14); english (−1.0) | fewer mixed levels in Korean replies; in the english stratum C replies are Korean (see below) |
| `phrase_battery` (total count) | coding-reply, conversation, english (−1.2 to −3.4), coding-edit, delegation, document (formal-report) | **more hits under the policy**; a raw count, confounded with length (below) |
| `genitive_ui_ratio` | coding-edit, coding-reply, conversation (−0.008 to −0.018) | slightly more 의 under the policy |
| `honorific_address` | every stratum but correct/defective, formal-report only | 사용자님 appears under formal-report (no zero line: not a candidate) |
| `english_ratio` | english (+0.88/+0.94), coding-reply, conversation, document | less Latin under the policy (no zero line) |

A − B intervals exclude zero in 29 (measurement, stratum) pairs, mostly in delegation, document and paste-in, where skills and agents act. The agent layer (sub records A against B/C) cannot be compared: arm A has no shipped agents and wrote no sub records.

Candidates written, identical in both profiles: `em_dash_count` max 0.0, `phrase_battery` max 0.0, `noun_ending_ratio` max 0.0, `particle_absence_ratio` max 0.3636, `speech_level` max 1.0, `genitive_ui_ratio` max 0.0667.

## Differs from spec

- **The batch is smaller than the pilot's sizing** (decision 1): release-blocked.
- **Candidate values follow a rule 09 did not give** (decision 4).
- **Summaries are under `tests/runs/02-P9/`**, as the user set for this era.

## Spec did not know

- **The policy translates English prompts.** In the english stratum, arm B replies have Latin share 1.00 and arm C replies 0.12 (agent-reply) and 0.06 (formal-report); `speech_level` shows Korean sentence endings in C and none in B. The spec's own stratum note says "the policy must not force translation (`coding.06`)". This is the largest B − C effect in the batch, and it is against the policy's intent.
- **`phrase_battery.total` is a raw count, so it grows with length and with Korean.** Outside the english stratum, C replies average 354 characters against 292 in B, with 208 Hangul syllables against 155. The top entries under C are `rewrite.A-10` (~할 수 있다, 0.72 per reply vs 0.40), `diagnose.056`, `diagnose.099`. A per-어절 rate would separate length from policy; P5 emitted counts per entry, as 09 §15.4 says.
- **Candidate values rest on three echoed texts.** The correct stratum's replies copy three fixed texts, so a 95th percentile over 54 sessions is the value of one of those texts (`particle_absence_ratio` 0.3636 is one text's own value). A value of 0.0 (`em_dash_count`, `noun_ending_ratio`, `phrase_battery`) means any occurrence exceeds it.
- **The agent layer cannot be compared as §18.1 states** ("A against B/C"): arm A has no shipped agents, and no sub records. In B and C, sub records split `korean-writer` 129, `korean-editor` 89, `korean-reviewer` 53, and 2 `general-purpose`.
- **The `ruleset` count in 09 §17.4 (115) is stale:** 136 at `05ce76d`. Adoption stays deferred.
- **`max_turns` 8 ends a turn in 5 of 1,458 sessions** (delegation and document in arm A, document in arm C), leaving that turn without a main record. **One background-agent turn was not detected** by the generator (a second `result` with no `task_notification` before it).
- **Prompts repeat.** 54 sessions per cell are 18 runs of each of 3 prompts. The intervals reflect sampling variance on three prompts per stratum, not prompt variance.

## Verification

Run V9, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned:

> Verified at commit 1ce4c82 (`git log -1 --oneline` → "1ce4c82 P9: batch-01 (1458 sessions, 54 per stratum-arm cell) reports, ruleset revisit (10_plan.md P9.1-P9.3)"). No tracked files were modified; `upstream/.cache` was symlinked read-only from the main checkout for `build.checks` and removed afterward (`git status --short` clean before and after). All reproduction used a copy of `~/.ko-quality-corpus-batch` under a scratch dir, never the original.
>
> ## Done-condition clauses (10_plan.md §4 P9 / flow.md P9.1–P9.3)
>
> **1. Per measurement: difference, interval, false-positive rate, candidate qualification with reason. Wilson for proportions, session-level bootstrap for B−C/A−B, method+resample count stated with every interval.**
> verdict: **met**
> evidence: `measure/batch.py` computes, per measurement × stratum: `B_minus_C/<profile>` (policy layer) and `A_minus_B` (skill layer), each with `difference`, `interval` (percentile bootstrap), `interval_method: "session-level percentile bootstrap, 10000 resamples, 95%"`; `false_positive_rate_correct_stratum` with Wilson `wilson_95` per arm/profile (`false_positive_method: "Wilson score interval, 95%"` top-level); and a `candidate` object with `qualifies` + `reason` (e.g. `tests/runs/02-P9/batch-01-report.json`: `measurements.em_dash_count.candidate` = `{"fp_observed": true, "qualifies": true, "reason": "both 09 §15.7 conditions hold"}`). I **fully reproduced this report**: copied `~/.ko-quality-corpus-batch`, ran `VPY -m measure run --home <copy>` then `VPY -m measure batch --home <copy> --batch batch-01`, and `diff`'d against the committed `batch-01-report.json` and `batch-01-run-report.json` — **byte-identical on both**, including `code_version` (unlike P8, where an untracked file caused drift — carried builder's note 4 held). I hand-verified the Wilson formula (n=54,k=0 → `[0.0, 0.0664]`, matches exactly) and the achieved-power formula in `batch-01-summary.json` (`0.7383` from `Φ(sqrt(54/2)·0.5 − 1.959964)` — recomputed independently, exact match). The 6 excluded sessions (arm_check/task_matches/turns_complete/is_error) reconcile exactly against the raw scratch progress log (`.../scratchpad/p9/batch/batch-01.progress.jsonl`, 1458 lines, 6 failing the same rule, sums to the same $190.2118), and `sessions_by_arm` (A 483, B 485, C 484 = 486−excluded-per-arm) matches precisely.
> how it could still be wrong: `measure/batch.py`'s `PRIMARY` dict (imported from `pilot.py`) covers only the 25 Tier 0/1 numeric measurements; it has **no entry at all** for `ko.preserve` (Tier 2) or the "Capture-dependent" `delegation_prompt_*` family that 09 §15.4 also lists as measurements — no difference, interval, FP rate or candidate check is computed for them anywhere in the P9 batch. This continues P8's own convention (same `PRIMARY` list), so it's not a new gap, but 10_plan.md's P9 scope text ("B − C and A − B per measurement...") doesn't explicitly exempt them, so a stricter reading could dispute "per measurement" being satisfied for the full §15.4 list. Also: skill-only-layer measurements (e.g. `bold_density`) can structurally never qualify as candidates because §15.7's condition 2 literally requires "a non-zero B − C difference" and B/C never differ in the skill layer by design — a defensible literal reading (the `watch:` block lives in the *policy* profile YAML), but worth flagging since the plan doesn't spell this out.
>
> **2. Every candidate in a profile carries `_meta` with batch id, arm and `exclusion_version`.**
> verdict: **met**
> evidence: `assemble/profiles/agent-reply.yaml:26-30` and `formal-report.yaml:26-30`: `_meta: {source: "corpus batch-01", arm: C, exclusion_version: "ex-3", status: candidate}` — exact match to 09 §15.7's literal YAML shape. Both files' `watch:` blocks (6 measurements each: `em_dash_count`, `phrase_battery`, `noun_ending_ratio`, `particle_absence_ratio`, `speech_level`, `genitive_ui_ratio`) are byte-identical to `batch-01-report.json`'s `candidates.agent-reply`/`candidates.formal-report` objects (checked programmatically). I rebuilt `dist/` from these profiles (`python3 build/claude_code.py`, `python3 build/agent_plugin.py`) — output was byte-identical to the committed `dist/` (`diff -rq` empty), confirming the "rebuild is byte-identical" claim in 274c129's commit message, and `python3 -m build.checks` (checks 1–6) passed with 0 failures. `watch:` does not leak into any built `dist/` file (`grep -rl "watch:" dist/` empty), consistent with 09 §15.7 ("nothing reads `watch:` at runtime").
> how it could still be wrong: condition (1) of §15.7 ("an observed false-positive rate on correct Korean") is satisfied merely by the rate being *computable*, not by it being low. `particle_absence_ratio` fires 54/54 (100%, Wilson `[0.9336, 1.0]`) in **every** arm/profile cell of the correct-Korean stratum — the same zero-line problem P8 already flagged ("correct Korean has non-zero absence... zero is not its clean value") — yet it still qualifies and ships a `max: 0.3636` candidate in both profiles. This is a literal, defensible reading of the frozen spec text, inherited from a pre-existing property of the measurement rather than a new P9 defect, but the resulting candidate rests on a false-positive baseline that P9's own report shows is closer to unusable than "observed cleanly."
>
> **3. The `ruleset` comparison is recorded.**
> verdict: **met**
> evidence: `tests/runs/02-P9/ruleset-revisit.md` — one `mid` exploration run (R9-1, Sonnet 5, 157,544 tokens) re-cloned `JangHyun-bin/korean-report-skills` at the locked commit `05ce76d`, recounted rules (136, not the spec's stale "115"), classified coverage against this repo's Tier 0/1/exclusion-pass measurements, listed implementation costs for uncovered classes, and gave both a case for adopting now and a case for deferring (matching the AGENTS.md verification-run pattern: "both sides... where it breaks"). Builder's reading at the end: adoption stays deferred, consistent with 09 §17.4's own "adoption stays deferred" and 10_plan.md's "recorded for review" instruction. Satisfies 09 §17.4's revisit requirement.
> how it could still be wrong: none found — this is a straightforward documentary clause and the artifact is substantive and self-consistent.
>
> ## Release-blocked condition
> **"the sized batch exceeds the budget ceiling set in 5-preflight. Fallback: run at the size the ceiling allows, report the power achieved, and mark the results underpowered."**
> verdict: **met (substantively), with one formal gap**
> evidence: `tests/runs/02-P9/batch-01-summary.json`: `"sizing": "63 per (stratum, arm) cell × 27 cells at pilot mean cost per cell ($3.64...) = $229.5 > $200; the ceiling allowed 53, rounded up to 18 rounds × 3 prompts = 54"`, `"achieved_power": {"n_per_arm": 54, "power": 0.7383, ...}`, `"cost_usd": {"canaries": 0.9015, "batch": 190.2118, "total": 191.1133, "ceiling": 200}`. The commit message states plainly: "is underpowered by the plan's fallback." I recomputed the achieved-power figure independently and it matches exactly; the $229.5/$200/54-session arithmetic also checks out against the raw progress log.
> how it could still be wrong: **there is no `design/02-validation/6-build/P9_*.md` build record at this commit**, and `6-build/README.md`'s progress table still shows all dashes for P9 ("P9 | ... | — | — | — | — | —"). AGENTS.md requires "Each build step ends with a commit and a record in `6-build/`," and the mandated record format has a `## Release-blocked` table that should carry this exact condition. Right now the only place "underpowered"/"release-blocked" is stated is commit-message prose, not a structured record. This exactly mirrors what V8 found at P8's commit 4018280 before a separate "P8 record" commit (9592171) landed — so it is very likely a pending, imminent step rather than a violated invariant, but as of 1ce4c82 itself the formal record is missing. I rate the *substance* of the release-blocked handling as met; the *recording* of it is not yet present at this exact commit.
>
> ## Checks (flow.md §3 P9: 10_plan.md P9.1–P9.3)
> Same three clauses as above — all **met**, same evidence.
>
> ## flow.md §1 rows
> - **F9** (α 0.05, power 0.8, effect 0.5×pooled SD): matches `measure/pilot.py:29` (`ALPHA, POWER, EFFECT_SD = 0.05, 0.8, 0.5`) and `batch-01-summary.json`'s achieved-power block. **Met.**
> - **F10** ($200 ceiling; canary and probe runs count): canary costs (0.9015, independently resummed from `canary-batch-01.json` + `canary-batch-01-mislabel.json`'s per-run `cost_usd` fields) plus batch cost (190.2118, summed from all 1458 progress-log lines **including the 6 failed sessions**) total 191.1133 < 200. **Met.**
> - **F11** (session-level percentile bootstrap, 10,000 resamples, fixed seed recorded): `measure/batch.py` `RESAMPLES, SEED = 10000, 20260917`; report's `"bootstrap": {"resamples": 10000, "seed": 20260917}`. Reproduction with the same seed gave byte-identical results. **Met.**
> - **F14** (no real text, no personal paths): scanned every string >150 chars across all seven `tests/runs/02-P9/*` files — only one long string found, and it is the sizing-arithmetic prose, not generated text. `grep` for <user name>/`/Users/` across those files and across `dist/` returned zero matches. **Met.**
>
> ## Contradictions / deviations found (not fixed, just reported)
> 1. **No P9 build record exists yet** and `6-build/README.md`'s progress table is unfilled for P9 (see release-blocked section above) — likely pending, per the P8 precedent, but true as of 1ce4c82.
> 2. **`measure/batch.py`'s measurement coverage omits `ko.preserve` (Tier 2) and `delegation_prompt_*` (capture-dependent)** entirely — no B−C/A−B/candidate computation for either, inherited from P8's `PRIMARY` list rather than newly introduced, but not flagged anywhere in a P9 record (none exists) as a scoping decision.
> 3. **`particle_absence_ratio` qualifies as a `watch:` candidate in both profiles despite a 100% false-positive rate on correct Korean** in this batch (same defect P8 already identified) — a literal but arguably hollow satisfaction of §15.7's condition 1.
> 4. **`batch-01-summary.json`'s `achieved_power`/`sizing` figures are not produced by any committed, testable code** (unlike `pilot.py`'s `variance_and_power()`) — I hand-verified the formula and arithmetic and they check out, but nothing in the repo would regenerate this file/reproduce this specific claim mechanically the way `batch-01-report.json` is reproduced by `measure batch`.
> 5. No scope creep otherwise: `git show --stat` on all three P9 commits (0b7b303, 274c129, 1ce4c82) touches only `corpus/{generator,__main__}.py`, `measure/{batch,__main__}.py`, `assemble/profiles/*.yaml`, `dist/*/*/ko-quality.stamp.json`, and `tests/runs/02-P9/*` — no P4–P8 territory (`measure/exclusion.py`, `measurements/`, `runner.py`, `pilot.py`) was modified.
>
> ## Key files (absolute paths)
> - <worktree>/measure/batch.py
> - <worktree>/measure/pilot.py
> - <worktree>/measure/__main__.py
> - <worktree>/corpus/generator.py
> - <worktree>/corpus/__main__.py
> - <worktree>/assemble/profiles/agent-reply.yaml
> - <worktree>/assemble/profiles/formal-report.yaml
> - <worktree>/tests/runs/02-P9/batch-01-report.json
> - <worktree>/tests/runs/02-P9/batch-01-summary.json
> - <worktree>/tests/runs/02-P9/batch-01-run-report.json
> - <worktree>/tests/runs/02-P9/batch-01-sessions.json
> - <worktree>/tests/runs/02-P9/canary-batch-01.json
> - <worktree>/tests/runs/02-P9/canary-batch-01-mislabel.json
> - <worktree>/tests/runs/02-P9/ruleset-revisit.md
> - <worktree>/design/02-validation/6-build/README.md (progress table, unfilled for P9)
> - <worktree>/design/02-validation/6-build/P8_corpus-and-pilot.md (precedent for record-after-verification pattern)
> - ~/.ko-quality-corpus-batch/{logs,annotations,derived} (read-only reference, outside tree)
> - <scratchpad>/p9/batch/batch-01.progress.jsonl (read-only reference, outside tree)

**Builder's notes on the findings:**
1. The record is written after verification; this file closes the release-blocked recording.
2. **`ko.preserve` and `delegation_prompt_*` are not in the batch analysis.** `ko.preserve` is a pass/fail per kind on paste-in pairs, not a number with a zero line, and `delegation_prompt_*` is the policy layer applied to sub records' delegation prompts. Both are computed per record in `derived/` and carried to review, not analysed for B − C here.
3. **`particle_absence_ratio`'s candidate is hollow**, as Spec did not know says: condition (1) is met literally at a false-positive rate of 1.0. Carried to review.
4. **`batch-01-summary.json` was produced by an inline script**, not committed code. Its figures are the sizing arithmetic and the achieved-power formula, both reproduced by V9.

## Release-blocked

| Condition | Evidence | Cheapest reverse taken | Resolve in review by |
|---|---|---|---|
| The sized batch was capped by the budget ceiling (10_plan.md P9) | Pilot sizing 63 sessions per (stratum, arm) cell ≈ $229.5 > $200 (`tests/runs/02-P8/pilot-01-report.json`, `tests/runs/02-P9/batch-01-summary.json`); ran at 54, achieved power 0.738 at 0.5 SD | Ran at the size the ceiling allowed; results and candidates marked underpowered; nothing reads `watch:` | Accepting the underpowered batch as era 02's result, or raising the ceiling for a top-up batch (a new batch id; batches are not pooled) |
