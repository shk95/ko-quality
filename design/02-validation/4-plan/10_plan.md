# 10. Build plan: era 02

> Stage document. **Draft, 2026-09-17. L1–L5 accepted by the user 2026-09-17.** What era 02 builds, in what order, and how each step is known to be done. The implementation target is [`09_toolkit_spec.md`](../3-spec/09_toolkit_spec.md). Entry to this stage is recorded in [`09a`](../3-spec/09a_findings_spec_close.md) §3.
>
> **Depth (user, 2026-09-17):** steps, dependency order, done-conditions. File-level execution flow, probes and pre-decided build choices belong to `5-preflight`.

## 1. Rules for every step

- **Before a step:** read its section here, the matching `5-preflight` section, and the latest record in `6-build/`.
- **After a step:** record findings in `6-build/P<n>_<name>.md`: what differed from 09, what 09 did not know, decisions taken with confidence, subagent runs. Then commit.
- **09 is frozen once the build starts.** Findings that would change it go to `7-review`.
- **A done-condition is confirmed by an independent verification run** (`mid`, outside the cap), never by the builder's claim.
- **A done-condition that cannot be reached does not stop the build.** Take the cheapest-to-reverse path, mark the record **release-blocked**, and continue (`AGENTS.md`).
- **No real text in the tree.** Corpus records live under a corpus `KO_QUALITY_HOME` outside it (§20). Run summaries under `tests/runs/` hold counts, hashes and synthetic text only.
- Step numbers restart at **P1** for this era.

## 2. Decisions settled here

09 §22.2 hands five decisions to this stage. **All five accepted as proposed (user, 2026-09-17).**

| # | Decision | Proposal | Why | Conf. |
|---|---|---|---|---|
| L1 | Directory names `measure/`, `corpus/`, `gate/` (§4) | **As written** | They name what each holds, and nothing in the tree conflicts. `gate/` holds a README only | high |
| L2 | Per-call scan cap for `tool_output_chars` (§11.2) | **100,000 characters per call.** Truncated calls are counted | The field is a covariate, not a measurement: an order of magnitude is enough. The cap bounds the logger's cost on a large `Read` or build log. P8's pilot reports the truncation rate, and 7-review revisits the number if it is high | medium |
| L3 | Extractor reads the rewrite taxonomy directly (§14.2) | **No extractor change in era 02.** See §2.1: the premise in 09 is wrong for 23 of the 24 patterns | Only J-1 is a generator drop, and its signal (excess bold) is already `bold_density`. Changing the selection changes the shipped skill and reverses era 01's flow D5 for one pattern | medium-high |
| L4 | `github` marketplace source for self-application (§21.2) | **The per-machine `marketplace add` step is the plan.** `5-preflight` probes a `github` source. If it loads headlessly from committed settings, P3 adopts it and removes the step | The step is known to work. The probe can only remove a step, so the build does not wait on it | medium |
| L5 | Build step at which self-application is switched on (§21.1) | **P3, right after P1 (plugin with `build_id`) and P2 (logger isolation)** | Every precondition in §21.1 exists after P2, and nothing earlier writes records. Later steps are then built under the policy they measure, which is §21's purpose | high |

### 2.1 Correction to 09: the 24 missing rewrite patterns

09 §14.2, §15.4 and §22.2 (written in `09a` §1.4, G2) say the 24 patterns missing from `normalized/` are ones "upstream's generator drops". Checked against the upstream cache at the locked commit (`ai-tell-taxonomy.md`, 2026-09-17):

| Missing patterns | Count | Upstream's own flag | Meaning |
|---|---|---|---|
| A-12, A-13, A-14, A-17, A-23, B-3, B-4, C-1, C-3, C-4, C-6, C-12, E-3, E-4, E-5, E-6, F-1, F-2, F-3, H-2, I-5, I-6, J-4 | 23 | `quick: false` | **Excluded by upstream's contract.** "strict 전용. 문서 레벨 판단(리듬·구조·분포·POS 분석)이 필요하거나 hold 상태인 패턴" |
| J-1 | 1 | `quick: true` | **A generator drop** (H2 heading, P1) |

Every `quick: true` pattern except J-1 is in `normalized/`, and no `quick: false` pattern is. **09 was corrected in wording on 2026-09-17** (§14.2 row, §15.4 `phrase_battery` coverage note, §22.2 row removed as settled), with a pointer in its header. The L1–L5 answers were entered in 09 at the same time (§4, §11.2, §14.2, §21, §22). `09a` §1.4 G2 carries a forward pointer. The 23 are document-level judgments, not surface signals: they are not a gap in a surface battery, and they are candidates for Tier 1 or `llm` measurement in a later era.

## 3. Order

```text
P1 distribution (B9) ──→ P2 logger ──→ P3 self-application
                                   └─→ P4 exclusion pass + measure/ ──→ P5 Tier 0 ──→ P6 Tier 1, Tier 2
P1 ──→ P7 eval split + judge Tier A
P2 + P6 + P7 ──→ P8 corpus generator + pilot ──→ P9 sized batch + watch: candidates
```

- **P1 before P2:** the logger reads `build_id` and `plugin_present` from the stamp P1 writes.
- **P5 before P6:** Tier 1 measurements run inside the runner, case format and report that P5 builds.
- **P4 before any measurement:** the exclusion pass is built first and validated first (§15.2).
- **P7 is independent of P4–P6** and can run in any order after P1. It is placed before P8 so that the plugin the corpus uses has a green trigger suite.
- **P8 needs P6:** the pilot's purpose is to measure false-positive rates and variance for every tier.

## 4. Steps

### P1 — Distribution under B9

**Scope:** 09 §4–§10, §13. **Prerequisite:** none.

- One Claude Code plugin `ko-quality` with both styles **unforced**. `ko-quality-formal` removed.
- Agents carry the agent-reply policy (S1-A). The ko-rewrite redirect sits under upstream step 1 (R3).
- Stamp gains `build_id`. `profile` and `injection_point` leave the Claude Code stamp. Version `0.2.0`.
- Checks 5 (agent names) and 6 (dependency boundary) added to `build/checks.py`.
- `exempt` removed from profiles; `register` restated. `server/` removed. `gate/` created with a README only (§4, §19; L1).
- Install docs: select once per project; remove, including the style selection; Codex `multi_agent_v2`.

**Done when:**
1. Two consecutive builds are byte-identical, and checks 1–6 pass.
2. With the plugin loaded headlessly: no style applies without selection, and `ko-quality:agent-reply` and `ko-quality:formal-report` each apply when selected. Both shown by canary, not by a settings echo (review §D).
3. A shipped agent's reply carries the agent-reply policy under either selected style (canary).
4. Removal leaves no style request behind when the documented steps are followed. This measures the §14.2 row added in `09a` G3.

**Release-blocked if:** 2 fails (arm B cannot be constructed).

### P2 — Logger

**Scope:** 09 §11, §12.1, §11.4. **Prerequisite:** P1.

- Per-session, per-agent state. All new fields of §12.1, the §11.3 table, `injected_prompts`, `skills_invoked`, three-value `task_type` on Claude Code, `tool_output_chars` with the L2 cap.
- `expanduser` on `KO_QUALITY_HOME`. Storage layout of §11.4 (`logs/` no longer split by profile).
- Masking additions (§12.1). Reserved gate fields absent.
- `tests/logger_test.py` rewritten to the new schema.

**Done when:**
1. `logger_test.py` passes on the recorded payloads for both harnesses (`hook-payloads.json`, era 99 records), including a subagent's edits kept out of the main record and a `<agent-message from=` prompt counted, not taken as `task`.
2. A live headless Claude Code session with a delegation writes one main and one sub record whose fields match §11.3's table.
3. A live `codex exec` session with the plugin's hooks trusted and a custom-agent spawn (`multi_agent_v2`, no `--ephemeral`) writes one main and one sub record whose fields match §11.3's Codex rows.
4. The logger prints nothing and exits 0 on a malformed payload.
5. Check 6 passes.

**Release-blocked if:** 2 fails, or 3 fails. **If Codex is unavailable**, 3 is release-blocked with that reason, and the Codex rows rest on condition 1's recorded payloads (review §D).

### P3 — Self-application

**Scope:** 09 §21. **Prerequisite:** P1, P2.

- Committed `.claude/settings.json`: `KO_QUALITY_HOME: "~/.ko-quality-dev"`, `enabledPlugins`, `outputStyle: "ko-quality:agent-reply"`.
- Per-machine steps in the Korean `README.md`: marketplace add (unless L4's probe removed it), remove a local `outputStyle`.
- The local `outputStyle` on this machine is removed with the user's confirmation, recorded in `5-preflight`.

**Done when:**
1. A session launched at the repository root writes records to `~/.ko-quality-dev` carrying `project` and `build_id`, and none to `~/.ko-quality`.
2. A session launched in a subdirectory is identifiable from its record's `project` (§21.1).
3. The main thread's reply shows the agent-reply policy (canary).

**Release-blocked if:** 1 or 2 fails. They are §21.3's two guards: exclusion by location and by `project`. The cheapest reverse is removing the committed settings file.

### P4 — Exclusion pass and `measure/`

**Scope:** 09 §15.2, §12.3, §20. **Prerequisite:** P2 (record schema).

- `measure/` skeleton: reads `logs/`, joins `annotations/`, writes `derived/`. Virtualenv and pinned `requirements.txt`.
- The exclusion pass, versioned, every zone of §15.2.
- `instruction_lang`, `artifact_lang`, `usable` (S2).
- Retention: at the start of every run, deletes monthly files past 90 days **in `logs/` and every text copy** (judge and grader copies), and reports what it deleted. **`derived/` and `annotations/` never expire** (§20).
- A zone-labelled set under `tests/exclusion-cases/`, written by us. It is not a §17.3 case: its labels are spans per zone, not expected measurement values.

**Done when:**
1. The false-negative count per zone on the labelled set is reported, with `exclusion_version`.
2. On a fixture home holding expired and current monthly files in every directory, retention deletes exactly the expired files in `logs/` and in text-copy locations, reports them, and **leaves every file in `derived/` and `annotations/` in place**.
3. Re-running on unchanged input yields identical derived records.

**Release-blocked if:** a zone's false negatives are not reported (§15.2: the pass is not complete until measured).

### P5 — Tier 0

**Scope:** 09 §15.1, §15.4 Tier 0, §15.6, §17.3. **Prerequisite:** P4.

- Every Tier 0 measurement, with layer and tier declared. `phrase_battery` from `normalized/` with upstream thresholds stored as data.
- Case format of §17.3, and cases for each measurement: correct Korean and defective Korean.
- The runner reports everything §15.6 requires.

**Done when:**
1. Every Tier 0 measurement passes its cases, correct and defective.
2. A run report carries `exclusion_version`, code version, arm and stratum counts, and floor exclusions.

### P6 — Tier 1 and Tier 2

**Scope:** 09 §15.3–§15.4 Tier 1 and Tier 2. **Prerequisite:** P5.

- `kiwipiepy` pinned in `measure/` only (S3). Recipe fixes from E2.
- A committed case set of correct and telegraphic Korean for the two E2 measurements, written by us. E2's own sentences were never committed (`tests/runs/02-E2/`: a throwaway environment).
- `ko.preserve`, all five kinds. `ko.change_rate` not built (§15.5).

**Done when:**
1. On that committed set, `noun_ending_ratio` and `particle_absence_ratio` each separate correct from telegraphic Korean **in the direction E2 measured** (telegraphic higher), and the size of the separation is reported beside E2's recorded values.
2. Each `ko.preserve` kind passes and fails its paste-in cases as expected.
3. Check 6 passes, and the analyser version appears in the run report.

### P7 — Eval split and judge Tier A

**Scope:** 09 §16.3, §17.1–§17.2. **Prerequisite:** P1.

- `tests/evals/claude-code/`: the two policy cases removed, the four trigger cases kept under `--ablation with-without`.
- Tier A with a stronger judge model on the two C3 policy cases, on a scratch copy with the style forced. Records keep text, verdict, reason, judge model.

**Done when:**
1. The trigger suite runs on the P1 plugin and each case's A-vs-B delta is reported.
2. The Tier A verdict is recorded against (judge model, rubric wording, tool version), with every judged text and reason.

### P8 — Corpus generator and pilot

**Scope:** 09 §18, §12.2, §14.2. **Prerequisite:** P2, P6, P7.

- `corpus/`: headless generator through the shipped logger, annotation writer, per-session settings reset, profile alternation, a canary per arm per batch.
- The prompt set, every stratum of §18.3, with coverage and gaps recorded.
- The pilot batch, then measurement over it.

**Done when:**
1. Every arm's canary passes. A batch with a marker in the wrong arm is rejected, and the rejection path is shown to work once.
2. Every log record in the pilot joins an annotation and a derived record.
3. The pilot report gives: exclusion-pass false negatives on generated replies, false-positive rate per measurement on the deliberately correct stratum, the hand-back rate (§14.2), the truncation rate (L2), and per-measurement variance.
4. Sessions per arm are computed by a **normal-approximation power calculation** from the pilot's session-level variance, for the measurements that can carry a `watch:` candidate (§22.2). α, power and the minimum effect of interest are set in `5-preflight`. The computation is reproducible from the pilot report, and its parameters are recorded.

**Release-blocked if:** 1 fails.

### P9 — Sized batch and `watch:` candidates

**Scope:** 09 §15.7, §18.4, §17.4. **Prerequisite:** P8.

- The sized batch. B − C and A − B per measurement, within stratum and layer.
- `watch:` candidates written only where §15.7's two conditions hold.
- The `ruleset` revisit (§17.4), recorded for review.

**Done when:**
1. Per measurement: difference, interval, false-positive rate, and whether it qualifies as a candidate, with the reason. **Intervals:** Wilson for proportions (as §16.1); for B − C and A − B, a **session-level bootstrap**, because profiles alternate within one session (§18.2) and turns are not independent. The method and resample count are stated with every interval.
2. Every candidate in a profile carries `_meta` with batch id, arm and `exclusion_version`.
3. The `ruleset` comparison is recorded.

**Release-blocked if:** the sized batch exceeds the budget ceiling set in `5-preflight`. Fallback: run at the size the ceiling allows, report the power achieved, and mark the results underpowered (review §D: an external limit is a release-blocked condition).

**Not a done-condition:** that any candidate exists. Zero candidates is a result.

## 5. Handed to `5-preflight`

- **Probes:** a `github` marketplace source from committed settings (L4); the canary device for P1 and P8 on the current CLI; `kiwipiepy` install in a virtualenv on this machine.
- **Harness availability:** availability per harness for P2's live runs and P8's batches, with "harness unavailable" listed as a release-blocked condition and its fallback (review §D).
- **Budget:** pilot and batch cost from §18.4's $0.12 per run, with a ceiling the user sets (P9's release-blocked condition).
- **Power parameters for P8.4:** α, power, and the minimum effect of interest per measurement.
- **User actions during the build:** removing the local `outputStyle` in P3.
- **Pre-decided build choices** for P4 (zone set size), P5 (case counts per measurement), P8 (prompts per stratum in the pilot).

## 6. Verification of this plan

| Run | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| 4-plan-v1 | mid (Sonnet 5) | Step order (§3) and done-conditions (§4) against 09, with §2 taken as accepted | ~177k | **Substantially sound.** 3 must-fix, 7 should-fix, 1 note |

Each finding was checked against its source before it was acted on. **Accepted and applied** (user, 2026-09-17):

| # | Finding | Applied |
|---|---|---|
| 1 | P6.1's "E2's set" was never committed | P6 writes its own case set; the condition is E2's direction, with size reported |
| 2 | P4.2's retention wording could delete `derived/` | Deletion limited to `logs/` and text copies; `derived/` and `annotations/` shown to survive |
| 3 | P3 release-blocked on condition 1 only | Conditions 1 and 2, §21.3's two guards |
| 5 | Zone labels do not fit §17.3's case format | `tests/exclusion-cases/` |
| 6 | P8.4 named no sizing method | Normal-approximation power calculation; parameters in `5-preflight` |
| 7 | P9.1 named no interval method | Wilson for proportions; session-level bootstrap for differences |
| 8 | No release-blocked condition for the budget | Added to P9 with a fallback |
| 9 | Codex live session only implied in P2 | P2.3, with the unavailable-harness path |
| 10 | No step creates `gate/` | P1 |
| 11 | P5 → P6 edge unexplained | §3 |

**Rejected:** #4, "P8 needs P3 because 09 §18.2 attributes the canary device to P3". That P3 is era 01's build step, not this plan's self-application step.
