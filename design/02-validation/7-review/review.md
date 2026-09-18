# 7-review — era 02-validation

2026-09-18. Branch `review/02-validation` off `dev`. Reviews the build at tag `era02-6build-end` (`240c1de`); era 98's later changes in `dev` are not under review here (era 98 review, R3). Input: `6-build/P1`–`P9`. **Status: closed. All items decided (2026-09-18).** Era 03 starts from section G.

Each item has a recommendation and a confidence. A decision is written into the item's "Decided" line when the user settles it; nothing here is decided by the agent alone.

## A. Release-blocked: P9, the batch capped by the budget

The pilot asked for 63 sessions per (stratum, arm) cell, about $229.5 at pilot cost; the ceiling was $200 (F10). `batch-01` ran 54 per cell, API-equivalent cost $191.11, achieved power 0.738 at 0.5 SD (`tests/runs/02-P9/batch-01-summary.json`).

What more sessions would and would not change:

- **Would:** power for a 0.5 SD effect, from 0.738 to 0.8. F9's standardized effect makes σ cancel (P8), so every measurement needs the same 63.
- **Would not:** the effects that carry the batch already have intervals far from zero (`em_dash_count` +0.5 to +1.6 per 100 어절, `noun_ending_ratio`, `particle_absence_ratio`, the english-stratum translation). The batch's larger limits are not about size: each stratum has **three prompts** repeated 18 times, so intervals reflect sampling on three prompts and not prompt variance; candidate values rest on **three echoed correct texts**; `particle_absence_ratio` qualifies at a false-positive rate of 1.0; `phrase_battery` is a raw count confounded with length (section B). More sessions of the same prompts leave all four as they are.
- **Era 03 re-measures** on real records with measurement-specific effects (F9's own answer), and nothing reads `watch:`.

| # | Option | Cost | Where it breaks |
|---|---|---|---|
| A1 | **Accept `batch-01` as era 02's result, marked underpowered.** Candidates stay `status: candidate`; the mark is carried in `_meta`'s record, not removed | 0 | A small effect (near 0.5 SD) may be missed; no candidate is promoted on this batch alone |
| A2 | New standalone batch `batch-02` at 63 per cell under the current build (`build_id` `12ccf56e8e070cfa`, not `batch-01`'s `51112680979b60c3`, so no pooling) | ≈ $231 API-equivalent incl. canaries; one sixth longer than `batch-01` at the same 4 jobs | Reaches 0.8 on the same three prompts per stratum and the same echoed texts; spends more than the whole era so far to confirm effects already outside zero |
| A3 | Top-up of 9 per cell (3 rounds) under `batch-01`'s own `build_id`, rebuilt from its commit, pooled with it. 09 §18.4 forbids pooling only across `build_id`s | ≈ $33 | P9 decision 7 chose "never pooled"; the CLI and model may have changed since the batch, which the `build_id` does not see. A pooled batch mixes two run dates |

Recommendation (first draft): **A1.** Confidence: medium-high. The shortfall is 0.74 against 0.8, and the batch's real limits are prompt coverage and candidate rules, which era 03's spec should fix before any batch is sized again.

**Revised after the user asked about A3.** A3's two doubts were checked against the raw data:

- *Pooling after seeing results.* The target of 63 was fixed by the pilot before `batch-01` ran; the ceiling stopped it short. Completing a pre-set size is not optional stopping.
- *Changed conditions.* `batch-01` ran in about four hours on Claude Code 2.1.274 with `claude-sonnet-5`, at commit `0b7b303` (generator `f73882f9c82f024a`, `build_id` `51112680979b60c3`, both matching every `batch-01` annotation). The current CLI is 2.1.276. Pinning 2.1.274 and running from a worktree at `0b7b303` leaves the model as the only condition not under control. The generator resumes from its progress file, so rounds 19–21 run under the same batch id and cells stay balanced.
- P9 decision 7 ("never pooled") was stricter than 09 §18.4 (not across `build_id`s); the review may overturn it.

Revised recommendation: **A3 with the CLI pinned.** Confidence: medium-high. It completes the planned power for about $33 and resolves the mark instead of accepting it. It does not touch the structural limits above; those go to era 03.

Decided (user, 2026-09-18): **A3, CLI pinned to 2.1.274.** P9 decision 7 is overturned for this top-up only. Ceiling for the top-up: $40 API-equivalent.

**Result.** Record: [`tests/runs/02-review/`](../../../tests/runs/02-review/) (`batch-01-pooled-summary.json` is written by the committed `pooled_summary.py`).

- Canaries under 2.1.274: all six pass. Rounds 19–21: 243 sessions, 0 failed, 0 skipped. Every stream of both runs reports Claude Code 2.1.274.
- API-equivalent cost of the top-up: $31.11 plus $0.86 of canaries, $31.97 of $40. Batch total $221.32.
- 63 sessions in each of the 27 cells; achieved power **0.801** at 0.5 SD (0.738 before). The same 6 sessions are excluded as in P9.
- Before pooling, the current analysis code reproduced P9's committed report exactly on a copy of the pre-top-up corpus, so every difference below comes from the data.
- **Candidates: the six measurements and their values are unchanged** (`n` in the basis 54 → 63). The profiles' `watch:` blocks carry no `n`, so they, `dist/` and `build_id` stay as they are.
- B − C pairs whose interval excludes zero: 68 before, 68 after. Of 314 (measurement, stratum, comparison) pairs, 8 changed side, all with an interval that touched zero: 5 became non-zero (`bold_density`, `paragraph_initial_repeat` and `spacing_errors` in A − B; `english_ratio` in two B − C pairs), 3 became zero (`noun_run_length` in two B − C pairs, `pos_ngram_diversity` in A − B). Every effect section B cites keeps its side.

**The release-blocked mark is resolved**, not accepted. P9's record stays as written; this section is its resolution.

Verification (run VR, section D), answers in short: (1) same conditions hold: `build_id` and `generator_version` identical in all 2,268 annotations; `claude_code_version` 2.1.274 and model `claude-sonnet-5` in every stream of both runs; arm A log records carry no `build_id` by design. (2) Pooling is permitted by §18.4 as written; 63 unique sessions in each of the 27 cells. (3) `batch-01-pooled-report.json` reproduced byte for byte from a copy of the corpus home. (4) `pooled_summary.py` reproduced the summary byte for byte; power and costs recomputed independently. (5) No period effect between rounds 1–18 and 19–21 in arms B and C for `em_dash_count`, `noun_ending_ratio`, `particle_absence_ratio`, `speech_level`; the check has low power (late n 69–81 per arm), so this reads "not visible", not "absent". (6) No host state in the six files, by check 7 and by hand. Caveats it named: only version and model fields of `init` were compared, not every field; exclusions were taken from `measure/batch.py`, not re-derived.

## B. Findings that revise spec 09 (era 03 spec input)

From each P record's "Spec did not know" and "Differs from spec". Grouped by what they touch; each is a revision candidate, none is a build error unless marked.

| # | Finding | Source | Proposed direction | Conf. |
|---|---|---|---|---|
| B1 | **The policy translates English prompts.** english stratum: Latin share 1.00 in B, 0.12/0.06 in C; the largest B − C effect, and against 09's own stratum note (`coding.06`) | P9 | Product defect in the policy text. Fix the profile policy (reply in the prompt's language) and add a policy case; this is the first thing a candidate threshold must not reward | high |
| B2 | `phrase_battery.total` is a raw count; C replies are longer and more Korean | P9 | Report per 어절 (or per 100 어절) like `em_dash_count`; keep per-entry counts | high |
| B3 | Candidate rule: 09 §15.7 gave the shape, not the value rule; the builder chose the 95th/5th percentile of arm C in the correct stratum (low-medium confidence). Values rest on three echoed texts; 0.0 values mean "any occurrence"; `particle_absence_ratio` qualifies at FP 1.0 | P9 dec. 3–5 | §15.7 condition 1 needs a bound on the false-positive rate, not "observed"; the correct stratum needs many texts; the value rule belongs in the spec | medium-high |
| B4 | The agent layer cannot be compared as §18.1 says: arm A has no shipped agents and no sub records | P9 | Restate the agent-layer comparison as B against C only, or add an arm with agents and no policy | medium |
| B5 | `ko.preserve` and `delegation_prompt_*` are computed per record but not in the batch analysis | P9 V9 | Spec says how each enters B − C (pass/fail proportions with Wilson) | medium |
| B6 | Batch sizing and achieved power came from an inline script, not committed code | P9 V9 | `measure batch` writes the summary; a figure in a committed summary is reproduced by committed code | high |
| B7 | `ruleset`: 136 rules, not 115; ~63 tied to one fictional example; cheapest valuable gap is §10 대화 잔재; adoption brings the first NOTICE obligation | P9 R9-1 | Keep deferred; decide separately whether §10 대화 잔재 enters `phrase_battery` as our text | medium |
| B8 | The analyser tags transliterated technical nouns as NNP (`로더`, `캐시`, `스레드`, `쿼리`), so the proper-noun zone removes them: 5 false positives of 9 negatives | P6 | A loanword stoplist or a dictionary check before masking NNP | medium |
| B9 | `의존명사 + 용언` and noun compounds make correct Korean non-zero in `particle_absence_ratio` | P6, P8 | The measurement needs a baseline, not a zero line (ties to B3) | medium-high |
| B10 | `claude plugin eval` exposes votes, not a reason; the reason is a second same-model call | P7 | 09 §16.3 accepts a reconstructed reason, labelled as such | high |
| B11 | Headless generation: stream-json input merges turns; delegations run in the background by default (several main records per `turn_key`); `max_turns` 8 cut 5 of 1,458 sessions; one background turn went undetected | P2, P8, P9 | Spec the generator's turn protocol (one turn at a time, foreground or notification-aware) | high |
| B12 | Removal: a leftover style selection is silent; `marketplace remove` rewrites committed project settings | P1, P3 | Install doc already says it; spec §13/§21 record the measured behaviour | high |
| B13 | User-scope plugins load in every headless arm | P1, P8 | Corpus runs under an isolated config home, or the arm definition names the confound (also host state: era 98) | medium |
| B14 | Hand-back stub 0 of 17 sub records; truncation 0 of 139 | P8 | Closes §22.2's hand-back question provisionally; era 03 recounts on real records | medium |

Decided (user, 2026-09-18): **all fourteen go to era 03 as spec input, with the directions above.** Whether each enters the spec is era 03's `3-spec` decision.

## C. Process findings (input to era 03's plan and preflight)

- **Exploration was almost unused:** 1 run of a cap of 36 over nine steps. Major decisions at low-medium or medium confidence (P9 decisions 3 and 4, the candidate rules) were taken without an exploration run. `AGENTS.md`: "Low confidence means re-verify before acting." Recommendation: preflight names the decisions that must get an exploration run.
- **Every verification run reported "the record does not exist yet"** (V1–V9), because the record is written after verification by design. The noise is harmless but repeated nine times. Recommendation: the verification prompt says the record comes after.
- **One commit carried a change it does not name** (P7 process note: a `git rm` inside the P6 record commit). History was not rewritten.
- **Preflight's cost estimate was low:** X5 estimated $50–$110 for the batch at 30 per cell; the pilot measured $3.64 for one session in each of the 27 cells and asked for 63. The ceiling, not the estimate, set the batch.

Recommendation: hand the four to era 03's plan and preflight. Decided (user, 2026-09-18): **write them into `AGENTS.md` now**, one line each: a measured cost probe in preflight (Process); an exploration run for a major decision below medium-high confidence, named in preflight (Decisions during build); a verification prompt that says what does not exist yet and forbids glob deletion (Subagents, together with era 98 review §E); a staged-set check before each commit (Git).

## D. Subagent runs

| Kind | Runs | Tier | Tokens |
|---|---|---|---|
| Verification (V1–V9), outside the cap | 9 | mid (Sonnet 5) | 1,261,860 |
| Exploration (R9-1, `ruleset`) | 1 of 36 | mid (Sonnet 5) | 157,544 |
| `large` | 0 | — | — |
| Review verification (VR): the pooled batch, outside any cap | 1 | mid (Sonnet 5) | 81,236 |

Every verification run met its done-condition and also reported findings the builder carried forward (P4's four defects fixed in P5; P5's three notes fixed in P6; V9's four notes carried here). `large` was never triggered, so era 01 review's question (does `large` reach a different conclusion than `mid`) has no new data.

## E. Merge `dev` to `master`

`dev` holds era 02's build and era 98's closed work (era 98 review R2: both reach `master` together after this review). With section A resolved, no release-blocked mark remains in era 02 or era 98.

Decided (user, 2026-09-18): **merge at the end of this review.** `review/02-validation` merges to `dev`, then `dev` to `master`; era 98 goes with it. Pushing is asked separately.

## F. Next era

Era 03 was planned as "re-measure on real records, `watch:` → `gate:`, control rotation" (`02_scope.md`). What the real records look like now: this repository's self-application home holds 279 records from 8 sessions over two days, and **`profile` is empty in all 279**. 09 §22.2 named "effective output style observable live on Claude Code" an era 03 blocker; the records confirm it. Without `profile`, no real record can be assigned to a policy arm, so the planned re-measure cannot start.

Inputs era 03 receives: section B (B1–B14), section C, 09 §22.2's open rows, the items `02_scope.md` handed on (`watch:` → `gate:`, off rotation and control ethics, `outcome`, §13.1 items that need a real distribution), and era 98 review §G (`project` across machines, stale `state/` in a product user's home, the cleanup notice channel).

| # | Scope | What it does first | Where it breaks |
|---|---|---|---|
| F1 | **As planned:** real-record re-measure, `watch:` → `gate:`, control rotation | Opens on the blocker | Blocked at once by `profile`; real records are too few to size anything |
| F2 | **Prerequisites first:** the observability blocker, the policy fix (B1), measurement rules (B2, B3, B5, B9), the generator's turn protocol (B11), with a corrected synthetic batch (more prompts per stratum, many correct texts). Real records accumulate meanwhile; re-measure and `gate:` go to the era after | Makes `profile` observable and the policy correct before anything is measured again | Real-record measurement moves one era later; the era is broader than its name |
| F3 | **Narrow:** only the blocker and B1; everything else waits | Smallest era | Measurement rules stay as they are, so any batch in between repeats P9's limits |

Recommendation: **F2.** Confidence: medium. The blocker has to go first whatever the scope, and B1 is a product defect that a threshold would otherwise learn from.

Decided (user, 2026-09-18): **F2, prerequisites first.** Real-record re-measure and `watch:` → `gate:` go to the era after 03.

## G. Handed to era 03

- **Scope (F2):** prerequisites first. Make the effective output style observable in live records (09 §22.2's blocker; `profile` empty in all 279 self-application records); fix the policy's translation of English prompts (B1); fix measurement rules (B2, B3, B5, B9) and the generator's turn protocol (B11); then a corrected synthetic batch with more prompts per stratum and many correct texts. Real records keep accumulating. Real-record re-measure and `watch:` → `gate:` go to the era after.
- **Spec input:** section B, B1–B14.
- **Plan and preflight input:** section C, now also rules in `AGENTS.md`.
- **Data:** `batch-01`, pooled to 63 per cell, is era 02's result; its `watch:` candidates stay `status: candidate`, and nobody reads them.
- **From era 98 review §G:** `project` if records are pooled across machines; stale `state/` files in a product user's `~/.ko-quality`; the cleanup notice channel (whether the UI shows `systemMessage`).
- **Still open from 09 §22.2:** Codex `task_type` third value (no era assigned); `ruleset` adoption (deferred, B7).
