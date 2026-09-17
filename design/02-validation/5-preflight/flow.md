# Build flow — era 02-validation, P1–P9

> Preflight document. **Draft, 2026-09-17.** Defines how the autonomous build (`6-build`) runs [`10_plan.md`](../4-plan/10_plan.md), answers the decisions that can be answered now, and collects what blocks release. Once the user accepts this file, the build starts at P1 on `dev` and does not stop.
>
> Read before every P: its section in `10_plan.md`, its section here, and the latest record in `6-build/`. Rules for judgment, subagents and git are in `AGENTS.md` and are not repeated here. Raw material for §1 is in [`explorations.md`](explorations.md).

## 1. Decisions settled in preflight

Pre-decided answers are not reopened during the build. If build evidence shows a premise false, take the cheapest-to-reverse path, record the deviation with the evidence, and continue. Rows marked **pending** wait on an exploration or the user.

| # | Decision | Answer | Counter-argument and the answer to it | Conf. |
|---|---|---|---|---|
| F1 | Claude Code test harness | A **scratch project** per run under the scratchpad, holding `.claude/settings.local.json` with the arm's selection and `env.KO_QUALITY_HOME` pointed at a scratch home. `claude -p "<prompt>" --plugin-dir <dist>/ko-quality --output-format stream-json --verbose --max-turns 8`, launched with the scratch project as working directory | `--plugin-dir` is not how users install. Answer: the install path is measured once in P1.4 and in P3; every other check needs a clean, disposable project, and selection lives in project settings either way (09 §2.1) | high |
| F2 | Codex test harness | Era 01's: `codex exec --json -m <model> -C <workdir>`, temporary `CODEX_HOME` with `auth.json` symlinked, deleted afterwards. **No `--ephemeral` when a custom agent is spawned** (09 §2.2). Load checks `gpt-5.6-luna`, behaviour checks `gpt-5.6-terra`. The user's `~/.codex` is never touched | — | high |
| F3 | Canary device | 02-E1's: a scratch **copy** of the built plugin with a marker line added to each style body and each agent body, never in `dist/`. A marker is a unique token per location (`KQ-CANARY-<arm>-<location>-<n>`). A check passes on the token's presence in the right reply and absence everywhere else | Adding a line changes the thing tested. Answer: the line is outside the policy text, and the unmodified plugin is what the corpus runs (P8); the canary proves routing only | high (X2: held on 2.1.274) |
| F4 | Generator and judge models | Corpus and live checks: **`claude-sonnet-5`**, pinned with `--model`. Tier A judge (P7): **`claude-opus-5`** via `--judge-model`. Judge ≠ generator (09 §17.2) | A user's default model may differ. Answer: era 02's corpus is synthetic; pinning makes batches comparable and cost predictable. The model is recorded in every annotation (§12.2) | medium |
| F5 | P4 zone set | One labelled reply per case, **at least 5 positive spans per row of 09 §15.2's zone table** across the set, and **at least 3 near-miss negatives per row** (text that looks like the zone and is not). Written by us, synthetic, committed under `tests/exclusion-cases/` | A small set hides false negatives. Answer: the done-condition is that the count is reported, not that it is zero; P8.3 measures the pass again on generated replies | medium |
| F6 | P5 cases per measurement | **At least 2 correct and 2 defective cases per Tier 0 measurement**, one of the defective ones at the boundary (a single occurrence). `phrase_battery`: at least one case per scope (paragraph, document) | — | medium |
| F7 | P6 case set | **At least 10 correct and 10 telegraphic sentences**, covering the recipe pitfalls E2 found (trailing punctuation, `VV-I`/`VV-R`, 체언 + `XSV`/`XSA`) | — | medium |
| F8 | P8 pilot shape | **3 prompts per stratum** of 09 §18.3 (9 strata, counting correct and defective Korean as two) × arms A, B, C = **81 sessions**, plus one canary run per arm. Arm C sessions alternate both profiles | Three prompts cannot estimate variance well. Answer: the pilot sizes the batch; its variance estimate is reported with its own uncertainty, and P9's power is reported as achieved (`10_plan.md` P9) | medium |
| F9 | Power parameters (P8.4) | **α = 0.05 two-sided, power 0.8, minimum effect of interest 0.5 of the pilot's pooled session-level SD** for every measurement (user, 2026-09-17, U1) | A standardized effect ignores what matters per measurement. Answer: no measurement has an observed scale yet; era 03 sets measurement-specific effects from real distributions | medium |
| F10 | Budget ceiling (P8, P9) | **Pilot $21, batch $200** (user, 2026-09-17, U2). X5's revised estimate: pilot $6–$12, batch $50–$110 at 30 sessions per arm per stratum. Canary and probe runs count toward the step's ceiling | — | high |
| F11 | Bootstrap (P9.1) | Session-level percentile bootstrap, **10,000 resamples**, fixed seed recorded | — | high |
| F12 | Self-application switch (P3) | The build removes `outputStyle` from `.claude/settings.local.json` (**consent given, user 2026-09-17, U3**). **The running build session is not affected**: settings are read at launch. Sessions started after P3 run under `agent-reply` and write to `~/.ko-quality-dev` | The builder's later sessions become records of the thing being built. Answer: 09 §21.3 accepts that; records from this repository never enter a sample | high |
| F13 | `github` marketplace (L4) | **The per-machine `marketplace add` step stays.** X1: a `github` marketplace in committed settings did not load headlessly, with or without `path` | Interactive trust might load it. Answer: untested, and the build cannot test it headlessly; 7-review may revisit | high |
| F14 | Records of runs | `tests/runs/P<n>/` holds summaries only: counts, hashes, tokens, costs, synthetic text. Corpus records stay under the corpus home outside the tree (09 §20). No personal paths | — | high |
| F15 | The `-ㅁ`/`-음` sentence ending in `noun_ending_ratio` (X3) | **pending: user** (§4, U6). Proposed: a sentence whose final `EF` morpheme is `ᆷ` or `음` counts as a **noun ending** (개조식 명사형 종결, which `coding.12` targets). 09 §15.4's recipe note gains this line before the build | Some `-음` endings are legitimate in 문서체 (`~함을 알 수 있음` in a memo). Answer: the measurement is a rate compared across arms, not a verdict; the case set (F7) includes both kinds and reports them | medium |
| F16 | Codex models | Load checks `gpt-5.6-luna`, behaviour checks `gpt-5.6-terra` (F2). The `large` tier's `gpt-5.6-sol` did not run (X4; not measured in era 02, cause not investigated): a `large` Codex run is replaced by `large` on Claude Code (`claude-opus-5`), recorded as such | — | high |

## 2. Verification run (one per P, outside the cap)

Tier `mid`. The verifier gets the question and the sources, never the builder's conclusion, the record's Decisions table, or its leaning. Carried from era 01 unchanged:

```text
You are verifying whether a build stage met its done-condition. You did not build it.
Done-condition (verbatim from 10_plan.md §4 P<n>): <text>
Checks listed for this stage (verbatim from flow.md §3 P<n>): <list>
Artifacts: <paths>. Run logs: <paths>. Commands to reproduce: <commands>.
For each clause of the done-condition and each check:
  verdict: met | not met | cannot tell
  evidence: file:line or log excerpt (quote it)
  how it could still be wrong: the strongest reason this verdict fails
Then: anything the stage produced that contradicts spec 09, 10_plan.md or flow.md, with evidence.
Do not fix anything. Do not suggest designs.
```

The answer goes into the P record as-is. "not met" or "cannot tell" on a done-condition clause makes the stage release-blocked for that clause; the build continues.

## 3. Stages

Common to every P:
- **Record:** `6-build/P<n>_<name>.md` with the two fixed tables of era 01's `6-build/README.md` (Decisions, Subagent runs), plus sections `Differs from spec`, `Spec did not know`, `Release-blocked`.
- **Commit:** one step per commit on `dev`; the record's last commit closes the P.
- **Spec and plan:** 09 and `10_plan.md` are frozen from P1's first commit.
- **Long text** goes through file-writing tools or quoted heredocs (`AGENTS.md`, Shell).

### P1 — Distribution under B9

- **Inputs:** 09 §4–§10, §13; `build/`, `assemble/`; F1, F3.
- **Steps:**
  1. `assemble/profiles/*.yaml`: remove `exempt`, `plugin:`, `output_style.force`; restate `register`. Build configuration gets the one plugin's name and description.
  2. `build/claude_code.py`: one plugin `ko-quality`, both styles unforced, agents with the agent-reply policy, stamp with `build_id` and without `profile`/`injection_point`, version `0.2.0`. Remove `dist/claude-code/agent-reply/` and `…/formal-report/` from the tree.
  3. `assemble/skills/ko-rewrite`: the redirect line directly under upstream step 1 (R3).
  4. `build/checks.py`: checks 5 and 6.
  5. `server/` removed; `gate/README.md` added; `AGENTS.md` layout table updated (`measure/`, `corpus/`, `gate/`; `server/` gone).
  6. Install docs (`assemble/install/`): select once per project; removal including the style selection; Codex `multi_agent_v2`; era 01 users remove `ko-quality-formal`.
  7. Two builds, byte compare, checks 1–6.
  8. Canary runs (F3): no selection; `agent-reply` selected; `formal-report` selected; one delegation under each selection.
  9. Removal: install from the local marketplace into a scratch project, select a style, follow the documented removal, start a session, record what the harness does.
- **Checks:** `10_plan.md` P1.1–P1.4; `plugin.json` name is `ko-quality`; no `force-for-plugin` anywhere in `dist/`; Codex dists still build and check 2–4 hold across them.
- **Pre-decided:** F1, F3. **Criteria only:** if a canary appears without selection, stop treating arm B as constructible, record it, and continue (release-blocked).
- **Release-blocked if:** P1.2 fails.

### P2 — Logger

- **Inputs:** 09 §11, §12.1, §11.4; `logger/ko_quality_log.py`, `tests/logger_test.py`; `tests/runs/02-spec/hook-payloads.json`, `tests/runs/99-retest/codex-channels.json`; F1, F2.
- **Steps:**
  1. Rewrite `tests/logger_test.py` against §12.1 first, driven by the recorded payloads.
  2. Logger: per-session per-agent state; §11.2's event table; §11.3's table; `tool_output_chars` with the 100,000-character cap and `truncated_calls`; masking additions; `expanduser`; §11.4 layout; `SessionEnd` cleanup.
  3. Malformed-payload test: truncated JSON, missing keys, unknown event.
  4. Live Claude Code: scratch project, plugin via F1, a prompt that makes the main thread delegate to `ko-quality:korean-reviewer`.
  5. Live Codex: F2 with hooks trusted (needs U4's permission rule), global install of the agent-plugin dist, a prompt that spawns a custom agent.
- **Checks:** `10_plan.md` P2.1–P2.5; no record contains an unmasked home path; `logs/` has no per-profile split.
- **Release-blocked if:** P2.2 or P2.3 fails. Codex unavailable, or hook trust not permitted → P2.3 release-blocked with the reason.

### P3 — Self-application

- **Inputs:** 09 §21; F12, F13; the user's consent (§4).
- **Steps:**
  1. Committed `.claude/settings.json`: `env.KO_QUALITY_HOME`, `enabledPlugins`, `outputStyle` (and the marketplace if F13 allows).
  2. Remove `outputStyle` from this machine's `.claude/settings.local.json`.
  3. Per-machine steps in the Korean `README.md`.
  4. A headless session at the repository root; one in `design/`.
- **Checks:** `10_plan.md` P3.1–P3.3; `~/.ko-quality` gains no file during the step (listing before and after).
- **Release-blocked if:** P3.1 or P3.2 fails. Reverse: delete the committed settings file and restore the local style.

### P4 — Exclusion pass and `measure/`

- **Inputs:** 09 §15.2, §12.3, §20; F5.
- **Steps:**
  1. `measure/` package, `requirements.txt` (empty until P6), virtualenv instructions in `measure/README.md`.
  2. Reader for `logs/`, join to `annotations/`, writer for `derived/`, versioned `exclusion_version`.
  3. The pass, zone by zone, on raw lines. Spans are kept per zone for headings, list items and table rows.
  4. `instruction_lang`, `artifact_lang`, `usable`.
  5. Retention (09 §20), run first in every invocation.
  6. `tests/exclusion-cases/` (F5) and a fixture home for retention.
- **Checks:** `10_plan.md` P4.1–P4.3; the proper-noun row is reported as Tier 1 and pending P6.
- **Release-blocked if:** any row's false-negative count is not reported.

### P5 — Tier 0

- **Inputs:** 09 §15.1, §15.4 Tier 0, §15.6, §17.3; `upstream/normalized/taxonomy/*.yaml`; F6.
- **Steps:**
  1. Case loader for `tests/measure-cases/` (§17.3).
  2. Each Tier 0 measurement, declaring layer and tier.
  3. `phrase_battery` built from `normalized/`, thresholds as data.
  4. Run report with §15.6's fields.
- **Checks:** `10_plan.md` P5.1–P5.2; no measurement applies an upstream threshold.

### P6 — Tier 1 and Tier 2

- **Inputs:** 09 §15.3–§15.4; `tests/runs/02-E2/kiwipiepy-recipes.json`; X3; F7.
- **Steps:**
  1. Pin `kiwipiepy==0.23.2` in `measure/requirements.txt`.
  2. Tier 1 measurements with E2's recipe fixes and prefix tag matching.
  3. The proper-noun zone of the exclusion pass (Tier 1) completed; P4.1 re-reported for that row.
  4. `ko.preserve`, five kinds, with paste-in cases.
  5. F7's case set; the separation report beside E2's recorded values.
- **Checks:** `10_plan.md` P6.1–P6.3.
- **Criteria only:** if `kiwipiepy` does not install, Tier 1 is release-blocked and 09 S3's option B applies (Tier 0 and Tier 2 regex only).

### P7 — Eval split and judge Tier A

- **Inputs:** 09 §16.3, §17.1–§17.2; `tests/evals/claude-code/`; F4.
- **Steps:**
  1. Remove `policy-agent-reply` and `policy-formal-report` from the suite; keep the four `*-fires` cases.
  2. Run the suite against the P1 plugin under `--ablation with-without`.
  3. Scratch copy of the two removed policy cases and the plugin with the style forced; run with `--judge-model claude-opus-5`; keep text, verdict, reason, judge model, rubric wording and tool version under the scratch home, and a summary under `tests/runs/P7/`.
- **Checks:** `10_plan.md` P7.1–P7.2.

### P8 — Corpus generator and pilot

- **Inputs:** 09 §18, §12.2, §14.2; F1, F3, F4, F8, F9, F10.
- **Steps:**
  1. `corpus/` generator: per-session scratch project, arm setup, settings reset, stream-json profile alternation, annotation writer, batch id.
  2. The prompt set under `corpus/prompts/`, every stratum, with coverage and gaps.
  3. Canary runs per arm; one deliberately mislabelled canary to show rejection.
  4. The pilot (F8) through the unmodified plugin; then `measure/` over it.
  5. Pilot report and the power calculation (F9).
- **Checks:** `10_plan.md` P8.1–P8.4; running cost stays under F10's pilot share.
- **Release-blocked if:** P8.1 fails.

### P9 — Sized batch and `watch:` candidates

- **Inputs:** 09 §15.7, §17.4, §18.4; P8's report; F10, F11.
- **Steps:**
  1. The sized batch, capped by F10.
  2. Differences within stratum and layer, intervals (F11), false-positive rates.
  3. `watch:` candidates with `_meta`, only where §15.7's conditions hold.
  4. The `ruleset` comparison (§17.4).
- **Checks:** `10_plan.md` P9.1–P9.3.
- **Release-blocked if:** the batch is capped by the budget (report achieved power).

## 4. Needed from the user before the build starts

| # | Question | Needed by | Status |
|---|---|---|---|
| U1 | Power parameters | P8 | **Answered:** F9's proposal |
| U2 | Budget ceiling | P8, P9 | **Answered:** pilot $21, batch $200 |
| U3 | Consent to remove the local `outputStyle` in P3 | P3 | **Answered:** yes |
| U4 | Codex availability and the hook-trust permission rule | P2 | Codex: usable (X4). **Open:** a Bash permission rule allowing `codex exec --dangerously-bypass-hook-trust`, scoped to a temporary `CODEX_HOME`. Without it, P2.3 is release-blocked |
| U5 | Which explorations run now | preflight | **Answered:** all; run 2026-09-17 |
| U6 | F15: count a final `-ㅁ`/`-음` as a noun ending | P6 | **Open** |

## 5. Release-blocked conditions, collected

Merge `dev` → `master` is decided in 7-review; each mark there is resolved or accepted.

| Stage | Condition |
|---|---|
| any | Done-condition clause "not met" or "cannot tell" by the verification run |
| any | An `adapted` fragment without `original`; an upstream sentence changed without `adapted` |
| P1 | No style applies without selection is false, or a selected style does not apply (arm B not constructible) |
| P2 | Live Claude Code records do not match §11.3; live Codex records do not match, Codex unavailable, or hook trust not permitted |
| P3 | Records reach `~/.ko-quality`, or a subdirectory session is not identifiable by `project` |
| P4 | A zone's false-negative count not reported |
| P6 | `kiwipiepy` not installable (Tier 1 falls back to S3 option B) |
| P8 | A canary in the wrong arm, or the rejection path not shown |
| P9 | The batch capped by the budget ceiling |
