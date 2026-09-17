# 09a. Findings: closing the spec stage

> Between-stages document. It records how `3-spec` was closed and what the closing found, before `4-plan` opens. [`09_toolkit_spec.md`](09_toolkit_spec.md) stays the implementation target and may still be revised until `5-preflight`.
>
> Three steps, agreed with the user on 2026-09-17:
> 0. **Is the spec actually finished?** Check it against fixed criteria, with independent runs (§1).
> 1. **Closing review.** Bundle 4 with the user, §22 settled, READMEs aligned (§2).
> 2. **Entry to `4-plan`.** Inputs, the plan document's shape, and the entry verdict (§3).

## 1. Step 0: closure check

### 1.1 Criteria (user, 2026-09-17)

1. **Traceability.** Every item handed to the spec is in 09, or deferred in 09 with the stage or era that takes it. Sources: era 01 review §B and §G, `01_idea.md`, `02_scope.md`, `03`–`08`, the 2-exploration README's handoff section, era 99 R1–R4.
2. **Review status.** Every bundle was reviewed with the user, and changes made after review were confirmed.
3. **Open items.** §22.2 leaves nothing that 3-spec must settle, and each open item names where it is settled.
4. **Internal consistency.** Section references, the §23 map and Basis lines resolve, and sections do not contradict each other.
5. **Evidence.** Every fact stated as measured has a record.

### 1.2 Bundle 3 after review (step 0-2)

Bundle 3 was marked reviewed in `aaf34b4`. The two edits that followed its draft (`daf00b6`, `2ebc70a`) were committed 44 and 52 seconds after it, so the reviewed text included them (inferred from commit times; confidence medium). The only later change to §15–§18 was the verification fix `7701002`:

| # | Where | Change |
|---|---|---|
| C1 | §17.1 | An in-tool regex rule must have a skill or agent as its subject. A main-thread policy regex cannot be one |
| C2 | §17.2 | States that moving the em-dash check out of the tool reverses an E5 handoff, and why: under B9 neither tool arm applies the style |
| C3 | §22.1 | Row wording |

The same commit changed bundle 2: the §11.2 scan cap handed to `4-plan`, the `policy_method` column in §11.3, and `truncated_calls` in §12. **The user accepted all of these on 2026-09-17.** Bundles 2 and 3 are reviewed as they now stand.

### 1.3 Runs

| Run | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| 0-3a | small (Haiku 4.5) | Inventory of items handed to the spec; reference checks on 09 | ~106k | References: none broken. **Inventory incomplete**: it skipped `03_features.md` and `05_approximations.md` (neither has a "Handed to the spec" section), and its per-source counts (79) did not match its total (67). Its § check reported 26 missing subsections from a regex that ignored `###`; a re-check found 0. Used as a starting list only, with the gaps named to the next run |
| 0-3b | mid (Sonnet 5) | The five criteria over 09 and its sources | ~235k | Criteria 1–4 **pass with gaps**, criterion 5 **pass**. Gaps G1–G5 (§1.4) and bundle 4 unreviewed |
| 0-4 | mid (Sonnet 5) | Re-verify the G1–G5 edits only | ~134k | G1, G2, G3, G5 **closed**. G4 closed on the letter but weakly grounded. No new inconsistency. New factual claims checked against `upstream/normalized/` and the upstream cache |

Every gap the runs reported was checked against the source by the builder before it was acted on.

### 1.4 Gaps and dispositions (user, 2026-09-17)

| Gap | Criterion | Found | Disposition |
|---|---|---|---|
| **G1** | 1 | Era 01's open finding "the ko-rewrite grade rule caps unchanged text at B" (P1, review §G, `01_idea.md`) had no disposition in 09 | §14.3: a structural limit. Upstream's sentence, not edited; a grade is a self-report and reaches no measurement (§1) |
| **G2** | 1 | "Upstream ships 85 patterns, the generator loaded 61" (`03_features.md:160`, "open item for the spec") was not taken up | **Option A.** The battery is built from the 61 and §15.4 states the gap. Whether the extractor reads the taxonomy directly is handed to `4-plan` (§14.2, §22.2). Option B, fixing the extractor first as a precondition, was not taken |
| **G3** | 3 | §13 calls the style-selection removal step "not yet measured", untracked in §14.2 | §14.2 row, checked in `6-build` |
| **G4** | 3 | §22.2 "Codex `task_type` third value" named no stage or era | First edit said "era 03 or later". Re-verification found no source ties a Codex arm to era 03, so the row now says: not in era 02, whose corpus is `claude -p` only (§18.2); no era assigned |
| **G5** | 4 | §5.3, §5.6, §14.2 called the `ruleset` licence unchecked and the blocker; §17.4 records it checked (Apache-2.0) | All three aligned with §17.4. §22.2's `ruleset` row now also names the exclusion pass as §17.4 does (noted by 0-4) |

### 1.5 Noted, not changed

- **`03_features.md:160`'s illustrative list of missing ids is inaccurate** (0-4): it includes a nonexistent F-6 and omits B-3, B-4, C-12 and J-4. Its totals are right: 85 upstream headings, 61 normalized, 24 missing, J-1 among them, each confirmed against the files. 2-exploration is a record and is not edited. `4-plan` should take the missing set from the files, not from that line.
- **The Apache-2.0 check has no run record under `tests/runs/`.** §17.4 cites the GitHub API and a HEAD commit. Acceptable while adoption is deferred. It is re-checked, with a record, if `ruleset` is adopted.

### 1.6 Verdict

**Criteria 1, 3, 4 and 5 are met after the fixes. Criterion 2 is met for bundles 1–3.** Bundle 4 has not been reviewed with the user, and that is step 1. Step 0 is closed.

## 2. Step 1: closing review

### 2.1 Bundle 4 (§19–§23), reviewed with the user 2026-09-17

| # | Question | Decision | Change to 09 |
|---|---|---|---|
| 1 | §19: reserve `gate/` and the four gate record fields now, though no gate runs in era 02? Cost: the fields are empty all era. Benefit: era 03 opens `gate:` without a schema change | **Reserve** | §22.1 gate row names the reservation |
| 2 | §20: does the runner delete expired monthly files automatically, or only report them? | **Automatic**, irreversibility accepted. It keeps "enforced by a program, not a habit" | §20 retention row; §22.1 retention row |
| 3 | §21: at which build step is self-application switched on? 09 fixed the preconditions, not the timing | **`4-plan` decides.** Leaning: right after the step that builds the logger's isolation (`~` expansion, `project`) and `build_id` | §21.1 pointer; new §22.2 row |
| 4 | §22.2: keep "effective output style observable live on Claude Code" as an era 03 blocker only? Era 02's corpus labels its arms itself, so it is unaffected | **Keep as is** | none |
| 5 | Status alignment | Bundle 4 marked reviewed; `design/README.md` and the era README say `3-spec` closed | header; both READMEs |

No run was made for this step. The decisions are the user's, and the edits are wording that records them.

### 2.2 §22 as settled

§22.1 records decisions 1 and 2 above. §22.2 now holds, by settling point:

- **`4-plan`:** directory names; per-call scan cap; extractor reads the rewrite taxonomy directly (61 → 85); `github` marketplace source; build step for self-application.
- **`6-build`:** sessions per arm (after the pilot); subagent hand-back routing (first batch); `ruleset` adoption (record, then review).
- **Later:** effective output style observable (era 03 blocker); Codex `task_type` third value (no era assigned).

Nothing in §22.2 is owed to `3-spec`. **`3-spec` is closed.** 09 stays revisable through `5-preflight`, as the design README allows.

## 3. Step 2: entry to `4-plan`

### 3.1 Inputs

| Input | Where |
|---|---|
| The implementation target | [`09_toolkit_spec.md`](09_toolkit_spec.md) |
| Decisions owed to `4-plan` | 09 §22.2: directory names; per-call scan cap (§11.2); extractor reads the rewrite taxonomy directly, 61 → 85 (§14.2); `github` marketplace source (§21.2); build step for self-application (§21.1) |
| The missing rewrite pattern ids | From the files (`upstream/normalized/taxonomy/rewrite.yaml` against the upstream taxonomy), not from `03_features.md:160` (§1.5) |
| What era 01's preflight missed | [`review.md`](../../01-toolkit/7-review/review.md) §D: harness availability, settings echo is not state, hook environment per harness, heredoc hazard. Input to `5-preflight`, and it shapes step boundaries in the plan |

### 3.2 Shape and depth of the plan (user, 2026-09-17)

- **`4-plan/10_plan.md`** (English) is the plan. **`4-plan/README.md`** (Korean) is the stage map.
- Modelled on 06 §14. Build steps are numbered from **P1** again, per era.
- The document holds common rules, then per step: scope (09 sections), prerequisites, done-condition (checkable by an independent verification run), release-blocked conditions, and the `4-plan` decisions settled there.
- **Depth: steps, dependency order and done-conditions.** File-level execution flow belongs to `5-preflight`.

### 3.3 Order, as a starting sketch

Direction only; `10_plan.md` settles it.

1. Logger revisions (§11–§12): `session_id`, `policy_on` / `plugin_present`, `project`, `~` expansion, scan cap, `build_id`, reserved fields
2. Self-application switched on (§21), right after 1
3. Exclusion pass (§15.2), built and validated first among measurements
4. Measurement runner: Tier 0 → Tier 1 (`kiwipiepy`, build check 6) → Tier 2 (§15), with retention deletion (§20)
5. Eval runner split (§17)
6. Corpus generator, pilot, then batches (§18)
7. Judge Tier A (§16.3)
8. Extractor taxonomy handling, placed by the `4-plan` decision

### 3.4 Verdict

**Entry confirmed** (user, 2026-09-17). `3-spec` is closed and every input exists. `4-plan` is open.
