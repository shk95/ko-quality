# 05. E4 — the approximations, one decision each

> Stage document. `2-exploration`, agenda item E4 (see [`02_scope.md`](02_scope.md)).
> 06 §13.1 is part of the spec, and it says of its nine items: **검증 단계에서 threshold를 걸기 전에 각각을 다시 본다.** This is that pass.
>
> Every item gets one of four dispositions: **resolve now**, **era 03** (needs a real distribution), **era 99** (needs Codex), **delete**. Two items outside the nine are carried here as well — the `register` mismatch, and a field that E7's run showed is false by construction.
>
> Evidence: [`tests/runs/02-E4/approximations.json`](../../../tests/runs/02-E4/approximations.json) and the five records from [`tests/runs/02-E7/`](../../../tests/runs/02-E7/agent-scope-and-visibility.json).

## Summary

| # | Item | Disposition | Evidence |
|---|---|---|---|
| 1 | `context_en_ratio` | **resolve now** — return renamed and redefined, counts not text | reasoned from the logger |
| 2 | `task_type` | **resolve now, Claude Code only** — a third value, read the path | reasoned; Codex unverified |
| 3 | `instruction_lang` | **resolve now** — a consumer of E2's exclusion pass | E7's records |
| 4 | `artifact_lang` mixed | **resolve now** (mechanism) / **era 02 corpus** (the rate) | E7's records |
| 5 | `output` purity | **resolve now** (mechanism) / **era 02 corpus** (the rate) | E7's records, E2 |
| 6 | `tokens.output` | **resolve now** — no estimate needed; the fallback estimator is language-branched | **run-verified**, 6 samples |
| 7 | `sub-to-sub` | **resolve now, partially** — not deleted. Session level, not per record | **run-verified** (result doc); hook half inherited |
| 8 | 변경률 | **half.** `ko.preserve` resolves now; `ko.change_rate` is still unspecified | E2; reopened by verification |
| 9 | Codex `instructions` | **era 99** | unchanged |
| + | `register` (06 §6) | **resolve now** — restate, do not drop | E2, B9 |
| + | `policy_on`, `injection_point` | **fix, do not rename.** Era 02 from the generator; **era 03 blocked** | E7's records |

Nothing is deleted. One item 06 pre-authorised deleting turned out to be partly measurable.

**Two of the eleven were tested; the rest were reasoned from code, records and documentation.** The distinction is in the evidence column because it was not visible in the first draft, where all eleven read as equally settled.

## 1. `context_en_ratio` — return, renamed, as counts

06 removed it because the system prompt is invisible to a hook, and allowed it back only under a name that says what it measures.

Tool output *is* visible: `PostToolUse` carries `tool_response`, which the logger already receives and reads only for error counting. Accumulating Hangul and Latin **counts** — not the text — keeps session state O(1) however long the session runs, which is what makes this cheap enough to be worth doing.

**Decision: `tool_output_en_ratio`.** It is a covariate, not a quality feature, and distinct from E2's `english_ratio`, which is computed on the reply. The old name is not reused, because the system prompt and skill bodies stay invisible and the value is not the context's English ratio.

**What it measures, said once so a consumer cannot misread it: English *exposure* through tool output, not the model's own English usage.** A large English file read by `Read` moves it, and that is intended — the hypothesis it serves is that an English-heavy context pulls the reply toward English. It is not evidence about anything the model chose to write.

**What the first draft left unspecified.** `tool_response` is not one shape: `Bash` returns `stdout`/`stderr`, `Read` and `Grep` return file content as a string or a list, `Edit` returns a small confirmation object, and the `Agent` tool nests a subagent's text together with usage and cost telemetry. Counting characters requires a rule for flattening it, and a naive `json.dumps` of the whole object inflates the Latin count with UUIDs, paths, cost figures and JSON keys. **The rule: count only string leaves, and skip keys.** Even then the value is noisy, which is another reason it is a covariate and never a threshold.

**And "O(1)" was about the wrong thing.** Session state stays two integers however long the session runs, which is what makes this safe to keep. The per-call work is proportional to the size of the tool response, so a large file read costs a full scan. Bounded by truncating the scan at a fixed number of characters per call, recorded as truncated.

**This item is reasoned, not tested.** No run exercised it.

## 2. `task_type` — the rule gains a value and a file extension

E7's five records read `writing` on every one, including `한국의 수도는 어디입니까?`. On that sample the field carries **no information at all**: the rule is *coding if an edit tool fired, else writing if a prompt exists*, so every non-editing turn is "writing".

The open finding from era 01 is the same defect from the other side — a design document written through `Write` is recorded as coding.

**Decision: three values, and read the path.** `PostToolUse` carries `tool_input.file_path`, so the rule can separate the two kinds of editing it currently merges:

| Value | Rule |
|---|---|
| `coding` | an edit tool fired on a source file |
| `document` | an edit tool fired only on prose files (`.md`, `.txt`, …) |
| `conversation` | no edit tool fired |

`task_type_method: rule` stays, and the instruction not to escape into an LLM classifier stays with it.

**Three gaps the first draft left open, filled here.**

- **Precedence.** A turn that edits both a source file and a prose file — common in this repository — resolves to `coding`. Any source-file edit wins.
- **Missing path.** If an edit tool fired but no `file_path` is present, the value is `coding` with `task_type_method: rule-nopath`, so the fallback is visible in the record rather than silently indistinguishable.
- **Claude Code only.** `tool_input.file_path` is the Claude Code payload shape. The logger is shared with Codex, whose `apply_patch` conventionally takes one patch blob covering several files and may carry no `file_path` at all. **Unverified; the check is deferred to era 99.** The rule is scoped to Claude Code and Codex keeps the current two-value behaviour until era 99 can check.

**And what this field is for, stated plainly.** `task_type` cannot answer whether the policy improves Korean output — `artifact_lang`, `output` and the feature battery do that. It is a **stratifying covariate**: it lets the analysis ask whether the effect differs by kind of task. The first draft presented the fix as progress on the research question, which it is not. It is a covariate that was carrying no information and now carries some.

## 3. `instruction_lang` — narrow the definition, then apply the exclusion pass

06 asked for the definition to be narrowed to "the Hangul ratio of the immediately preceding user input". That is necessary and turned out not to be sufficient.

E7's run read `en` for a prompt that was Korean prose containing the identifier `korean-writer`. Fourteen Latin characters moved the classification.

**Decision: narrow the definition as 06 said, and compute it after E2's exclusion pass** — inline code, identifiers, paths and URLs removed first. This stops being a separate fix and becomes one more consumer of machinery E2 already requires. The narrowed definition is written identically into the record schema and the features list, which is what 06 asked to check.

## 4. `artifact_lang` mixed — same root, same fix

E7's records read `mixed` wherever a Latin canary token appeared. 06's prescription — extract comments, string literals and markdown paragraphs, drop code tokens, `usable: false` on extraction failure — is E2's exclusion pass under another name.

**Decision: the mechanism resolves now, as a consumer of the exclusion pass. The number 06 asked for — the actual contamination rate on code-plus-Korean-comment output — is measured on era 02's corpus**, which is exactly the kind of thing the corpus exists to answer. The grader must not read this value before that measurement exists.

## 5. `output` purity — same, plus a prohibition already entered

06 prescribes stripping quotations and code blocks and discarding below 20 Korean 어절. The stripping is the exclusion pass. The floor is the `usable` flag.

E2 already established that the flag sits on top of the defect — telegraphic Korean is what `coding.12` and `coding.14` target, and such replies are short — and E7 observed `usable: false` on three of five records, all of them short *correct* Korean.

**Decision: keep the flag, never filter on it** (E2's rule stands), and measure on the corpus the number 06 actually asked for: how often quoted user input survives into the text the mechanical graders read.

## 6. `tokens.output` — measured, and the estimate is wrong

The spec estimates output tokens as characters ÷ 2.5, i.e. 0.4 tokens per character, marked `method: estimate`.

**The first draft measured three Korean-prose replies, found ~1.03 tokens per character, and concluded the spec understates by 2.6×. That conclusion was scoped to Korean prose and stated as though it were general.** Three more samples across the content an agent actually produces:

| Content | Characters | Hangul | Visible tokens | **Characters per token** |
|---|---|---|---|---|
| Korean prose | 103 | 74 | 118 | 0.87 |
| Korean prose | 478 | 283 | 476 | 1.00 |
| Korean prose | 789 | 506 | 816 | 0.97 |
| Korean prose + code block | 1,005 | 304 | 793 | 1.27 |
| Code (English/Python) | 247 | 0 | 89 | 2.78 |
| English prose | 943 | 0 | 269 | 3.51 |

**0.87 to 3.51 — a fourfold range.** The spec's 2.5 is close for code and English and wrong by about −60 % for Korean prose. **It was a compromise for mixed content, not a bad guess** — but a compromise that is worst on exactly the content this project measures. Replacing it with a Korean-calibrated 1.0 would simply move the error onto the coding replies, which is what the first draft proposed.

**One trap found on the way, worth the spec's attention.** `usage.output_tokens` **includes thinking tokens**. The middle sample reported 1,080 output tokens for 478 characters; 604 of them were thinking. Without subtracting `output_tokens_details.thinking_tokens` the three samples disagree by a factor of two and the estimate looks far worse than it is. Any calibration that skips that subtraction is measuring the wrong thing.

**Decision, in two parts.**

**Era 02 does not estimate.** Its corpus is generated by `claude -p --output-format json`, which returns actual usage, so the generator writes the true count with `method: usage`. Estimated and measured values are never pooled.

**The fallback estimator branches by script, not by a single constant.** The logger already has `lang()`; the same character classes give a two-term estimate:

```
tokens ≈ 1.51 × hangul_chars + 0.34 × other_chars
```

Fitted on the six samples above it cuts mean absolute relative error from 48 % to 8 % — in sample. **Checked on four further replies it had never seen: 48 % → 19 %.** Better by a factor of 2.5, and still not good.

| Held-out sample | Actual | ÷ 2.5 | Fitted |
|---|---|---|---|
| Korean prose, long | 712 | −60 % | **−3 %** |
| English + bash | 209 | −2 % | −16 % |
| **Korean with many file paths** | 910 | −74 % | **−47 %** |
| Korean + markdown table | 353 | −58 % | −10 % |

The worst case is the one that matters: 600 characters of Korean containing directory names and paths came to 910 tokens — **0.66 characters per token, denser than Korean prose itself**, because `.claude/agents/` splits into five tokens. The two-term model treats non-Hangul as English-prose density, and punctuation-heavy text is far denser than that. That shape is exactly what an agent's replies about a codebase look like.

**So the estimator is labelled for what it is: an order-of-magnitude indicator, `method: estimate-v2`, never a quantity a threshold reads.** A third term for punctuation would help and would be three parameters fitted on ten samples, which is not a measurement. The real answer stays the first one: era 02 uses actual usage and does not estimate.

## 7. `sub-to-sub` — not deleted. Partly observable

P7 decided this was unemittable: `SubagentStop` has no parent, and parallel siblings cannot be told from nesting by hook ordering. 06 authorised deleting the value if nothing new appeared.

Something new appeared. The headless result document carries `subagent_stats`:

```json
{"spawned": 2, "max_depth": 2, "spawned_by_subagents": 1, "completed": 2, "by_type": {"general-purpose": 2}}
```

A run in which the main thread spawned a subagent that spawned another reported `max_depth: 2` and `spawned_by_subagents: 1`.

**P7's finding is not overturned — it is bounded.** The *hook* still cannot attribute a record. But the **session** can be labelled, and era 02's corpus is generated by a process that reads that document.

**One asymmetry, named rather than hidden.** The easy half — what the result document carries — was run live on 2.1.273. The hard half — that no hook payload carries a parent — is **inherited from P7, which checked 2.1.270**, two point releases earlier, and was not re-run here. Documentation checked since still describes `SubagentStop` as carrying `agent_id` and `agent_type` and no hierarchy field, so the conclusion stands, but it stands on a documentation reading beside a live one. If the hook half ever matters more than the session-level flag, it needs its own run.

**Decision: keep the field, and emit it only where it can be justified.** A session-level `sub_to_sub_present` flag with `method: session-stats`, available to the corpus generator and not to the hook. Per-record attribution stays absent rather than guessed. There is an ordering heuristic — a nested subagent must finish before its parent, so the first `SubagentStop` would be the nested one — and it is recorded here as a heuristic and **not adopted**, because parallel siblings break it and a wrong label is worse than a missing one.

This is also the first item where era 02's offline architecture buys something the in-hook design could not have had.

## 8. 변경률 — half discharged, and the first draft said "resolved"

06 kept the model's self-reported change rate verbatim in `upstream_report` and assigned the code judgment to this era under the name `ko.change_rate`.

**The first draft answered with the wrong capability.** It found that the diagnose taxonomy's 보존 원칙 are mechanical and `input+output`, and concluded that building them *is* the assigned judgment. It is not. 04 §6 specifies two capabilities, not one:

| Capability | Input | Output | Note |
|---|---|---|---|
| `ko.change_rate` | before, after, **preserve_spans** | **ratio** | 형태소 단위. 보존 span은 분모 제외 |
| `ko.preserve` | before, after, kinds | **{violations[]}** | 숫자·고유명사·코드·경로·URL·인용 추출 후 집합 비교 |

They are separate conjuncts in `gate`'s own pass condition — `pass = preserve ∧ change_rate<fail ∧ …` — and separate keys with independent thresholds in the profile config. Upstream's own skill keeps them apart too: `ko-rewrite`'s self-check lists "고유명사·수치·날짜·인용 100% 보존" and "변경률 30% 이하" as two different items.

**A change rate is a quantity; a preservation check is a set of invariants.** They are related in one direction only — the preservation extraction supplies the `preserve_spans` that `change_rate` removes from its denominator. That makes `ko.preserve` a **necessary input, not a substitute**.

**Decision, corrected.**

- **`ko.preserve` resolves now.** E2's Tier 2 has it: extract proper nouns, numbers, units, dates, currency, quotations, code, URLs and paths from both texts and compare the sets. This is real and it is ready.
- **`ko.change_rate` is not resolved.** No edit-distance or similarity procedure is specified anywhere in E2 or E4. 04 says 형태소 단위 — morpheme-level — which makes it a **Tier 1** measurement depending on the unverified analyser, not the Tier 0 one E2 listed it as. That contradiction is E2's and is corrected there too.
- The self-report stays in `upstream_report`, untouched and un-promoted; the two never share a field.
- E2's pairing constraint carries over: the pair only exists when the original text was pasted into the prompt.

**What is owed and by whom.** `ko.change_rate` needs a procedure — what unit, what distance, how preserved spans are excluded — and that is spec work, not exploration. It is named here as an open obligation rather than left inside a claim that the item is closed.

## 9. Codex `instructions` — era 99

P6 closed the channel, which removed the `adapted` row. It returns only if era 99's retests reopen the channel. **Unchanged, and untouched by anything in era 02.**

## The two additions

### `register` (06 §6) — restate, do not drop

E2 established that `formal-report`'s `register: 사용자에게 전달되는 문서` describes a delivery channel the mechanism cannot see: one forced output style applies to everything the model writes, the honorific block addresses the user directly, and measurement is reply-only.

B9 changes the surrounding facts without changing that one. Under unforced styles the profile becomes a **per-project** choice, which is nearer to artifact kind than a per-installation choice — a docs repository versus a code repository — but a project is still not an artifact.

**Decision: restate, do not drop.** 06 §6's `register` becomes a description of the conversational register the profile selects — coding-terse versus 하십시오체 with an address term — and the plugin description follows it. Dropping the distinction was the other candidate and is now the worse one: B9 makes adding a profile cost one style file, so the distinction is cheap to keep and the only thing wrong with it was the description.

### `policy_on` and `injection_point` — a deviation from 06 §11, not an approximation

Not one of the nine, and on a second look not a §13.1 item at all.

**06 §11 already says where these come from:** `policy_on`, `injection_point` and `model` are listed against `SessionStart` — 설정 상태. The build reads them from the build stamp instead. `model` was recorded as a deviation in P7 because Claude Code's headless `SessionStart` does not carry it; the other two silently fell back to the stamp and nothing recorded that.

So the logger's `policy_on` means *a build stamp is present*, which is to say *the plugin is installed*. E7's run shows the consequence: three runs in which no output style was selected, and the policy therefore did not apply, recorded `policy_on: true` and `injection_point: output-style`. A fourth recorded `injection_point: agent-definition` for a subagent that ran from a **project** definition carrying no policy at all.

Under the current build the error is mostly invisible, because installing the plugin forces the style. Under B9 it becomes structural, and it makes E2's three-arm control design unmeasurable: arm B records itself as arm C.

**Decision: fix `policy_on`, do not rename it.** The first draft proposed renaming it to `plugin_present`. That was wrong, and the reason is worth writing down: `policy_on` is not a local field name. It is the name the design's falsifiability argument is written around —

> `policy_on`이 `noun_ending_ratio`를 안 움직이면 … 그건 한국어 품질 엔진이 아니라 일반 문체 린터이고, 다른 프로젝트다.

— and it appears by that name as the stratification axis in `05_composition_spec.md` (§9.3 schema, §"층화용", §11 promotion condition 3), in `05a_findings_measurement.md` twice, in `04a_findings_premise.md`, in `06 §11.3`, and as an asserted key in `tests/logger_test.py`. Renaming it would rename the pivot of the argument to save the implementation's mistake.

`policy_on` already means the right thing. The implementation computes the wrong thing under it.

- **`policy_on` keeps its name and gains its meaning:** true when the policy actually applied. Not written unless something establishes it.
- **`plugin_present` is added** for what the stamp establishes, which is genuinely useful — it is what separates arm A from arms B and C.
- **`tests/logger_test.py` asserts `policy_on` as a required key** and will need the new field alongside it. Named here so the build does not discover it.

**Era 02 supplies the truth from outside the hook** — but the join key does not exist yet.

The corpus generator knows which arm it ran. Attaching that to the hook's records needs a key, and **the record has none.** `06 §11.3`'s schema and the logger both emit `id` (a fresh uuid4 per record) and no `session_id`; the session id exists only as the name of the state file, which is deleted at `SessionEnd`. An earlier draft of this section said the records already carry it. They do not.

**So: add `session_id` to the record.** It is present in every hook payload, the logger already reads it to find its state file, and it is a uuid rather than anything personal. One line in `record()` and one row in `06 §11.3`.

**This blocks two of this page's resolutions, not one.** The session-level `sub_to_sub_present` flag from item 7 needs exactly the same key to reach the records it describes. Without `session_id` neither the arm label nor the nesting flag can be attached to anything, and both were written as though the plumbing existed.

The generator does not author records; it annotates them after the run, joining on `session_id`.

**Era 03 does not have that.** A live session would need the harness to tell a hook which output style is in effect, and P3 showed `init.output_style` reports the configured value rather than the effective one. Whether any hook payload carries it is unmeasured. **It is the one thing on this page that era 03 cannot start without.**

## What this pass changed about the era

Three items were expected to be deferred or deleted and were not:

- **`sub-to-sub`** was pre-authorised for deletion and turned out to be observable at session level.
- **`tokens.output`** was expected to need a calibration exercise and instead needs no estimate at all, because the corpus generator returns the true value.
- **`ko.change_rate`** was the item most likely to slip, and E2 had already found its mechanism.

The common cause is E1. Generating the corpus offline means a process outside the hook sees the whole session document, and three separate items 06 filed as "the hook cannot see this" stop being about the hook.

The cost is on the other side of the same trade: **every one of those three resolutions works for era 02's corpus and not for a live session.** Era 03 inherits a measuring apparatus whose three best-resolved fields are supplied by a generator it does not have.

And that trade has a price the first draft did not name. Each of those fields now needs a provenance tag (`method: usage` against `method: estimate-v2`, `sub_to_sub_method: session-stats`, `policy_on` present against absent) **and two code paths — one for the hook, one for the generator.** "Nothing is deleted" is not free; it is schema surface and branching that the build stage inherits, and it is listed here as an action item rather than left as a pleasant summary line.

## What the verification changed

An independent `mid` run checked this document against the raw runs, the logger source and the spec. Six things changed:

| | Was | Is |
|---|---|---|
| 1 | Rename `policy_on` to `plugin_present` | **Withdrawn.** `policy_on` is the name the design's central argument uses, in five documents and a test. Fix the field, add `plugin_present` beside it |
| 2 | A §13.1 approximation | It is a **deviation from 06 §11**, which assigns these fields to `SessionStart`. Nothing recorded the fallback to the stamp |
| 3 | "The estimate is wrong by 2.6×" | True of Korean prose only. Across ordinary output the ratio spans 0.87–3.51; the spec's 2.5 was a compromise, worst on our content. The fallback is now language-branched, not a new single constant |
| 4 | `task_type` reads the file path | Scoped to Claude Code. Codex's `apply_patch` shape is unverified; the check is deferred to era 99. Precedence and missing-path fallback now defined; the field is named a covariate, not an answer |
| 5 | `tool_output_en_ratio` "accumulate counts, O(1)" | O(1) in state, not per call. `tool_response` shapes, what to count and what the field means are now specified |
| 6 | Eleven dispositions reading as equally settled | Two were run-verified; the evidence column says which |

A later round of verification found three more:

| | Was | Is |
|---|---|---|
| 7 | Item 8 "resolve now — `ko.change_rate` is E2's Tier 2" | **Half.** `ko.preserve` resolves; `ko.change_rate` is a different capability in 04 §6, is 형태소 단위, and has no procedure. The first draft discharged an obligation by substituting an easier measurement |
| 8 | "joined by `session_id`, which every record already carries" | **The record has no `session_id`.** It has to be added, and it blocks the `sub_to_sub_present` flag as well |
| 9 | The token fallback estimator, fitted in-sample | Checked out of sample on four more replies: mean absolute error 48 % → 19 %, but **47 % on path-heavy Korean**, which is what an agent's replies about a codebase look like. It is an order-of-magnitude indicator, not a quantity |

## Subagent runs

| # | Tier | Purpose | Verdict |
|---|---|---|---|
| E4-v | `mid` (Sonnet 5) | Adversarial check of the first draft against the runs, `logger/ko_quality_log.py` and 06 §13.1 | Confirmed items 3–5, 8, 9 and the thinking-token catch. Found the `policy_on` rename's blast radius, the Korean-only scope of the token conclusion, the Codex gap and the three undefined cases in `task_type`, the unspecified `tool_response` handling, the inherited hook half of `sub-to-sub`, and that the summary did not separate tested from reasoned. 88.2k tokens |

Two live runs settled items 6 and 7; three more were added after the check to measure the token ratio on code and English. Exploration runs used in this stage: 5.
