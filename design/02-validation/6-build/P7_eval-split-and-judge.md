# P7 — Eval split and judge Tier A

## Summary

The two policy cases left `tests/evals/claude-code/`; the four trigger cases stay. On a copy of the P1 plugin (build `51112680979b60c3`) under `--ablation with-without`, all four trigger cases fire with the plugin and not without it: A-vs-B delta 1 each. Tier A ran with `claude-opus-5` judging `claude-sonnet-5` replies on scratch copies with one style forced, 3 runs per arm per profile: 12 judged replies, 0 contradictions of a deterministic rubric clause, so the judge is not disqualified for this (judge model, rubric wording, tool version). The tool exposes votes but no reason, so a same-model reason call per text is recorded beside each verdict.
Done-condition: **met on both clauses** (independent `mid` verification). Release-blocked: **0**.

## Built

| Item | Path | State |
|---|---|---|
| Policy cases removed; four `*-fires` cases kept | `tests/evals/claude-code/` | done. **The deletion landed in `b1d7ded` (the P6 record commit)**, see Process note |
| Trigger suite run, per-case delta | `tests/runs/02-P7/trigger-eval.json` | done, $1.67 |
| Tier A runs, style forced on scratch copies | scratch copies (not committed); summary `tests/runs/02-P7/judge-tier-a.json` | done, $1.03 |
| Judged texts, votes, verdicts, reasons, rubric, judge model, tool version | `~/.ko-quality-dev/judge/2026-09.jsonl`, batch `02-P7-tierA` (outside the tree, 09 §20 retention) | done |

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | The judge's reason: the tool records `judgeVotes` and the explanation `judge votes: PASS PASS PASS`, no reason. Mark P7.2 release-blocked / ask the same judge model, same rubric, same text, for a verdict and reason, and record it beside the votes | **Reason call** per judged text (`claude -p`, `claude-opus-5`, structured `{verdict, reason}`, no tools, no settings), labelled as a separate call. It agreed with the tool's verdict 12/12 | medium | 09 §16.3 (reason required); tool output fields |
| 2 | minor | Runs per arm for Tier A | 3, as C3 ran, so the result sits beside C3's | high | review C3 |
| 3 | minor | Arms for Tier A | `with-without`: the plugin-off replies give the rubric's deterministic clauses a chance to be violated (2 of 3 agent-reply baseline replies carry an em dash), which is what Tier A tests | high | 09 §16.2 |
| 4 | minor | Style forcing on the scratch copy | Remove the other style file and add `force-for-plugin: true` to the tested one, so no "first forced style wins" question arises | high | era 01 P5 |
| 5 | minor | Generator model in Tier A | `--model claude-sonnet-5` pinned; judge `claude-opus-5` | high | F4 |
| 6 | minor | Where judged texts live | `~/.ko-quality-dev/judge/`, the text-copy location retention covers; the tree holds hashes, counts and verdicts | medium | 09 §20, F14 |
| 7 | minor | Tier A contradiction rule | A PASS vote where the rubric's deterministic clause decides FAIL (agent-reply: an em dash appears; formal-report: 사용자님 never appears). Non-deterministic clauses (noun-phrase endings, 반말) are not Tier A's question | high | 09 §16.2 |

Exploration runs: 0 of 4.

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V7 | mid (Sonnet 5) | Verification of the P7 done-condition (outside the cap), isolated worktree at `7b0eb90` | 131,140 | Both clauses **met**; steps 1–3 met; noted the deletion committed under the P6 record commit, and that the reason is a reconstructed call, disclosed |

## Cost

| Run | Model | USD |
|---|---|---|
| Trigger suite, 4 cases × 2 arms | the user's default model (no `--model` given; a trigger case tests whether a skill fires) | 1.6677 |
| Tier A agent-reply, 3 × 2 arms, judge included | `claude-sonnet-5` generator, `claude-opus-5` judge | 0.5865 |
| Tier A formal-report, 3 × 2 arms, judge included | same | 0.4451 |
| Reason calls, 12 | `claude-opus-5` | 0.4854 |
| Probe of the reason-call command | `claude-opus-5` | 0.0314 |
| **Total** | | **3.22** (P7 has no ceiling in F10) |

## Differs from spec

- **The reason is not the tool's.** 09 §16.3 asks every judge record to keep "the judge's stated reason"; `claude plugin eval` 2.1.274 does not expose one. The recorded reason comes from a second call with the same model, rubric and text (decision 1).
- **Summaries are under `tests/runs/02-P7/`**, not `tests/runs/P7/` as flow.md §3 P7 writes: the user set `02-P<n>` for this era so era 01's directories are not overwritten.

## Spec did not know

- **The eval tool's `llm` grader output** is `judgeVotes` (three booleans), `explanation` ("judge votes: …") and `evidence` (the judged text, `focus: last_message`). No reason, no per-vote text.
- **With `claude-opus-5` as judge, the C3 failure did not recur.** C3 (Haiku default judge, 2.1.272) failed 3/3 policy-compliant agent-reply replies and passed a formal-report baseline without 사용자님. Here every vote is unanimous and consistent with the mechanical clauses: agent-reply with plugin 3/3 PASS (0 em dashes), without 0/3 PASS (em dash in 2 of 3; the third ends a prose line in a noun phrase); formal-report with 3/3 PASS (사용자님 in each), without 0/3 PASS (never). This is Tier A only: 12 replies say nothing about Tier B's error bounds (09 §16.2 asks 60–70 per direction per arm).
- **The mechanical policy effect reproduces C3:** em dash in 0/3 policy replies vs 2/3 baseline; 사용자님 in 3/3 vs 0/3.
- **One agent-reply policy reply (with, run 0) ends one paragraph line in a noun phrase** by `noun_ending_ratio` (0.125); the judge passed it three times, and its reason names the lines it read as list items. The rubric exempts lists, so this is not a Tier A contradiction.

## Process note

The `git rm` of the two policy cases was staged before the P6 record was committed, and `git commit` took the whole index: `b1d7ded` ("P6 record") contains the deletion. The repository state is right; the commit message does not say so. Nothing was rewritten, because `dev` history is the record.

## Verification

Run V7, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned:

> Verified at commit 7b0eb90 (`git log -1 --oneline` confirms `7b0eb90 P7: eval split (two policy cases leave the tool), trigger suite under ablation, judge Tier A with claude-opus-5 (09 §16.3, §17.2)`). Working tree clean, no files modified.
>
> ## Done-condition (10_plan.md §4 P7)
>
> **Clause 1 — "The trigger suite runs on the P1 plugin and each case's A-vs-B delta is reported."**
> verdict: **met**
> evidence: `tests/runs/02-P7/trigger-eval.json` records `plugin.build_id: "51112680979b60c3"`, which equals `dist/claude-code/ko-quality/ko-quality.stamp.json`'s `build_id` exactly. `diff -rq dist/claude-code/ko-quality <scratchpad>/p7/trigger/ko-quality --exclude=evals` returns no output — the scratch copy used for the eval is byte-identical to the shipped P1 plugin outside the injected `evals/` dir. All 4 kept cases (`diagnose-fires`, `grammar-fires`, `rewrite-fires`, `route-fires`) carry an explicit `"delta_A_vs_B": 1` field; `aggregates: {casesTotal:4, casesPassed:4, meanDelta:1}`. I cross-checked the committed summary against the raw tool output at `<scratchpad>/p7/trigger/ko-quality/evals/results/2026-09-17T09-48-25-551Z/aggregate-result.json` — costs, turns, and grader explanations match verbatim (e.g. diagnose-fires with-arm `costUsd: 0.345735` = summary's `0.3457`).
> how it could still be wrong: I did not re-run the eval myself (not needed to reach a verdict); if the raw scratchpad JSON were itself fabricated rather than genuine tool output, this would look identical. But its `report.html`, per-case `tracePath`s (the tool's temporary `out/trace.jsonl`) and Claude Code version stamps are consistent with genuine `claude plugin eval` output, and the build_id chain ties it to the real dist artifact.
>
> **Clause 2 — "The Tier A verdict is recorded against (judge model, rubric wording, tool version), with every judged text and reason."**
> verdict: **met**
> evidence: `tests/runs/02-P7/judge-tier-a.json` records the triple (`judge_model: claude-opus-5`, `rubric_wording` pointer, `tool_version: claude plugin eval, Claude Code 2.1.274`) and 12 rows (2 profiles × 2 arms × 3 runs) each with `text_sha256`, `tool_votes`, `deterministic_clause`, `tier_a` classification. `~/.ko-quality-dev/judge/2026-09.jsonl` (12 lines, `batch: "02-P7-tierA"`) holds the full text, verdict, judge's reason, judge model, generator model, rubric and tool version per row. I independently recomputed sha256 of all 12 `text` fields — all 12 match the recorded `text_sha256` exactly. I independently recounted `—` (U+2014) and `사용자님` occurrences in the raw text — all 12 match the recorded `deterministic_clause`/`em_dash_count`/`sayongjanim_count` exactly (e.g. `agent-reply/without/run0` has one real U+2014 at "...rebase하지 않는다\" — 히스토리가..."). Judge (`claude-opus-5`) ≠ generator (`claude-sonnet-5`) in all 12 rows, satisfying flow.md F4. Sum of `reason_call.cost_usd` across the 12 jsonl lines = 0.485436, matching the summary's `reason_calls_cost_usd: 0.4854`; per-profile `judge_cost_usd` sums (0.14135, 0.06559) match the raw `aggregate-result.json` `judgeCostUsd` sums exactly. Result: `contradictions: 0, judged: 12, verdict: "not disqualified"` — and manually re-applying the stated Tier A rule ("rubric's deterministic clause forces FAIL, vote is PASS") to every row confirms zero contradictions.
> how it could still be wrong: the tool's own grader exposes only vote booleans plus a non-explanatory string (`"judge votes: PASS PASS PASS"`), not a reason. The build supplies the "reason" via a second, same-model/same-rubric/no-tools call (`<scratchpad>/p7/reasons.py`) that re-asks for {verdict, reason} on the identical evidence text. This is disclosed in the record's `method` field, not hidden, and `reason_call_agrees: true` in all 12/12 rows — but strictly this reconstructed reason is not necessarily the reasoning the original 3-vote grading calls used internally, only a plausible after-the-fact rationalization that happens to agree with the vote every time.
>
> ## Checks (flow.md §3 P7, steps 1–3)
>
> 1. "Remove `policy-agent-reply`/`policy-formal-report`; keep the four `*-fires` cases" — **met**. `tests/evals/claude-code/` at 7b0eb90 contains only `diagnose-fires/`, `grammar-fires/`, `rewrite-fires/`, `route-fires/`; grep for `policy-agent-reply`/`policy-formal-report` across `tests/evals/` and `design/02-validation/6-build/` returns nothing.
> 2. "Run the suite against the P1 plugin under `--ablation with-without`" — **met**, same evidence as Clause 1.
> 3. "Scratch copy of the two removed policy cases and the plugin with the style forced; run with `--judge-model claude-opus-5`; keep text/verdict/reason/judge model/rubric wording/tool version under the scratch home, and a summary under `tests/runs/P7/`" — **met**, using the era's redirected path `tests/runs/02-P7/` as directed. I confirmed the scratch copies' style-forcing is genuine: `<scratchpad>/p7/judge-agent-reply/ko-quality/output-styles/` contains only `agent-reply.md`, with `force-for-plugin: true` added to its frontmatter (absent from the real dist copy) — `force-for-plugin` is a real, previously-used mechanism throughout this repo (P1, P3, P5, E1, E7), not invented for this step. Both judge scratch copies' `ko-quality.stamp.json` carry `build_id: 51112680979b60c3`, matching P1's shipped build. The case content reused is byte-identical to the original C3 case (`git show 21845c7:tests/evals/claude-code/policy-agent-reply/prompt.md` == the scratch copy's `prompt.md`), and the rubric text matches exactly (verified via `git show 21845c7:.../graders/policy.md`).
>
> ## Contradictions / notable findings (not asked to fix)
>
> 1. **Commit misattribution.** The actual deletion of `tests/evals/claude-code/policy-agent-reply/` and `policy-formal-report/` (plan step P7.1) was committed in `b1d7ded`, whose message is "P6 record: Tier 1 and Tier 2 verified, 0 release-blocked" — it does not mention removing eval cases at all (`git show b1d7ded --stat` shows the two deletions alongside the P6 record markdown). `b1d7ded` is `7b0eb90^`. This means the task prompt's own suggested inspection command, `git show 7b0eb90^:tests/evals/claude-code/policy-agent-reply/graders/policy.md`, fails (`fatal: path ... does not exist in '7b0eb90^'`) because the file is already gone at that commit; it is visible one commit further back, at `7b0eb90^^` (`21845c7`) or `92832da`. Functionally the repository state at 7b0eb90 is correct, but this is a violation of AGENTS.md's "Commit messages in English, one step per commit" — a P7 step shipped bundled into, and undocumented in, a P6-labeled commit.
> 2. **Missing build record / verification / progress update.** As of 7b0eb90, no `design/02-validation/6-build/P7_*.md` exists, `6-build/README.md`'s progress table still shows `—` for every P7 column (record/verdict/release-blocked/cost/last commit), and no independent verification subagent run for P7 is logged anywhere. AGENTS.md requires "Each build step ends with a commit and a record in `6-build/`" and "A stage's done-condition is confirmed by an independent verification subagent, not by the builder's own claim"; `6-build/README.md` itself states "P마다 커밋하고 P마다 기록한다." This doesn't falsify either done-condition clause (both are satisfied purely by the artifacts already committed), but the stage's own closing bookkeeping is incomplete at this commit — this verification run itself appears to be the missing piece, likely to be followed by a P7 record commit.
> 3. No other contradictions of spec 09, 10_plan.md, or flow.md were found. `python3 -m build.checks` failed with an unrelated `IndexError` in this worktree (check 1's re-extraction subprocess produced no output) — this looks like a machine-local `measure/.venv` (kiwipiepy) not being present in this worktree, per 6-build/README.md's own note that the venv "is installed on this machine and not committed"; it is unrelated to P7's scope and I did not chase it further.
>
> Files referenced: `tests/runs/02-P7/trigger-eval.json`, `tests/runs/02-P7/judge-tier-a.json`, `dist/claude-code/ko-quality/ko-quality.stamp.json`, `tests/evals/claude-code/*`, `design/02-validation/6-build/README.md`, `design/02-validation/4-plan/10_plan.md` (§4 P7), `design/02-validation/5-preflight/flow.md` (§3 P7, F4), `design/02-validation/3-spec/09_toolkit_spec.md` (§16–17), `design/01-toolkit/7-review/review.md` (C3), `tests/runs/review/policy-eval-runs3.json`, `~/.ko-quality-dev/judge/2026-09.jsonl` (outside tree).

**Builder's notes on the findings:**
1. The commit misattribution is recorded above under Process note.
2. The record is written after verification, as in every P.
3. Check 1's `IndexError` in a fresh worktree comes from the missing `upstream/.cache/` (V6 found the same), not from the virtualenv: `upstream/.cache/` is not committed. Carried to review with P6's note.

## Release-blocked

None.
