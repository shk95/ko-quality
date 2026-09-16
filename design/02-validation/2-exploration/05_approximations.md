# 05. E4 — the approximations, one decision each

> Stage document. `2-exploration`, agenda item E4 (see [`02_scope.md`](02_scope.md)).
> 06 §13.1 is part of the spec, and it says of its nine items: **검증 단계에서 threshold를 걸기 전에 각각을 다시 본다.** This is that pass.
>
> Every item gets one of four dispositions: **resolve now**, **era 03** (needs a real distribution), **era 99** (needs Codex), **delete**. Two items outside the nine are carried here as well — the `register` mismatch, and a field that E7's run showed is false by construction.
>
> Evidence: [`tests/runs/02-E4/approximations.json`](../../../tests/runs/02-E4/approximations.json) and the five records from [`tests/runs/02-E7/`](../../../tests/runs/02-E7/agent-scope-and-visibility.json).

## Summary

| # | Item | Disposition |
|---|---|---|
| 1 | `context_en_ratio` | **resolve now** — return renamed and redefined, as counts, not text |
| 2 | `task_type` | **resolve now** — the rule gets a third value and reads the file extension |
| 3 | `instruction_lang` | **resolve now** — a consumer of E2's exclusion pass |
| 4 | `artifact_lang` mixed | **resolve now** (mechanism) / **era 02 corpus** (the rate) |
| 5 | `output` purity | **resolve now** (mechanism) / **era 02 corpus** (the rate) |
| 6 | `tokens.output` | **resolve now** — measured; the estimate is wrong by 2.6× and does not need to exist |
| 7 | `sub-to-sub` | **resolve now, partially** — not deleted. Observable at session level, not per record |
| 8 | 변경률 | **resolve now** — `ko.change_rate` is E2's Tier 2 |
| 9 | Codex `instructions` | **era 99** |
| + | `register` (06 §6) | **resolve now** — restate, do not drop |
| + | `policy_on`, `injection_point` | **resolve now** for era 02; **era 03** for live sessions. Rename what they actually measure |

Nothing is deleted. One item that 06 pre-authorised deleting turned out to be partly measurable.

## 1. `context_en_ratio` — return, renamed, as counts

06 removed it because the system prompt is invisible to a hook, and allowed it back only under a name that says what it measures.

Tool output *is* visible: `PostToolUse` carries `tool_response`, which the logger already receives and reads only for error counting. Accumulating Hangul and Latin **counts** — not the text — keeps session state O(1) however long the session runs, which is what makes this cheap enough to be worth doing.

**Decision: `tool_output_en_ratio`.** It is a covariate, not a quality feature, and it is distinct from E2's `english_ratio`, which is computed on the reply. The old name is not reused, because the system prompt and skill bodies stay invisible and the value is not the context's English ratio.

## 2. `task_type` — the rule gains a value and a file extension

E7's five records read `writing` on every one, including `한국의 수도는 어디입니까?`. On that sample the field carries **no information at all**: the rule is *coding if an edit tool fired, else writing if a prompt exists*, so every non-editing turn is "writing".

The open finding from era 01 is the same defect from the other side — a design document written through `Write` is recorded as coding.

**Decision: three values, and read the path.** `PostToolUse` carries `tool_input.file_path`, so the rule can separate the two kinds of editing it currently merges:

| Value | Rule |
|---|---|
| `coding` | an edit tool fired on a source file |
| `document` | an edit tool fired only on prose files (`.md`, `.txt`, …) |
| `conversation` | no edit tool fired |

`task_type_method: rule` stays, and the instruction not to escape into an LLM classifier stays with it. This is still an approximation — a `.md` file can hold code and a `.py` file can hold a Korean essay in comments — but it is an approximation that distinguishes cases the current one cannot, and the previous version distinguished nothing.

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

Measured on three single-turn Korean replies:

| Case | Characters | Visible tokens | Tokens per character |
|---|---|---|---|
| 사계절, two sentences | 103 | 118 | 1.15 |
| rebase vs merge, five sentences | 478 | 476 | 1.00 |
| 조사의 역할, ten sentences | 789 | 816 | 1.03 |
| **pooled** | **1,370** | **1,410** | **1.03** |

**Korean prose runs at roughly one token per character**, consistently. The spec's divisor understates by about 2.6×.

**One trap found on the way, worth the spec's attention.** `usage.output_tokens` **includes thinking tokens**. The middle sample reported 1,080 output tokens for 478 characters; 604 of them were thinking. Without subtracting `output_tokens_details.thinking_tokens` the three samples disagree by a factor of two and the estimate looks far worse than it is. Any calibration that skips that subtraction is measuring the wrong thing.

**Decision: era 02 does not estimate.** Its corpus is generated by `claude -p --output-format json`, which returns actual usage, so the generator writes the true count and the `method` becomes `usage`. The estimate stays only as the fallback for records the generator did not produce, with its divisor corrected to ~1.0 for Korean and the field marked so the two are never pooled. Whether one token per character holds on longer and more mixed output is an era 03 question; three short samples fix the order of magnitude, not the constant.

## 7. `sub-to-sub` — not deleted. Partly observable

P7 decided this was unemittable: `SubagentStop` has no parent, and parallel siblings cannot be told from nesting by hook ordering. 06 authorised deleting the value if nothing new appeared.

Something new appeared. The headless result document carries `subagent_stats`:

```json
{"spawned": 2, "max_depth": 2, "spawned_by_subagents": 1, "completed": 2, "by_type": {"general-purpose": 2}}
```

A run in which the main thread spawned a subagent that spawned another reported `max_depth: 2` and `spawned_by_subagents: 1`.

**P7's finding is not overturned — it is bounded.** The *hook* still cannot attribute a record. But the **session** can be labelled, and era 02's corpus is generated by a process that reads that document.

**Decision: keep the field, and emit it only where it can be justified.** A session-level `sub_to_sub_present` flag with `method: session-stats`, available to the corpus generator and not to the hook. Per-record attribution stays absent rather than guessed. There is an ordering heuristic — a nested subagent must finish before its parent, so the first `SubagentStop` would be the nested one — and it is recorded here as a heuristic and **not adopted**, because parallel siblings break it and a wrong label is worse than a missing one.

This is also the first item where era 02's offline architecture buys something the in-hook design could not have had.

## 8. 변경률 — `ko.change_rate` is already specified

06 kept the model's self-reported change rate verbatim in `upstream_report` and assigned the code judgment to this era.

E2 found the material: the diagnose taxonomy's 보존 원칙 are mechanical and `input+output` — proper nouns, numbers, units, dates, currency, quotations, code, URLs, paths, register level. They are not style measurements; they are this judgment.

**Decision: `ko.change_rate` is built here from E2's Tier 2.** The self-report stays in `upstream_report`, untouched and un-promoted; the two never share a field. The constraint E2 attached carries over: the pair only exists when the original text was pasted into the prompt, so the corpus has to include paste-in cases deliberately.

## 9. Codex `instructions` — era 99

P6 closed the channel, which removed the `adapted` row. It returns only if era 99's retests reopen the channel. **Unchanged, and untouched by anything in era 02.**

## The two additions

### `register` (06 §6) — restate, do not drop

E2 established that `formal-report`'s `register: 사용자에게 전달되는 문서` describes a delivery channel the mechanism cannot see: one forced output style applies to everything the model writes, the honorific block addresses the user directly, and measurement is reply-only.

B9 changes the surrounding facts without changing that one. Under unforced styles the profile becomes a **per-project** choice, which is nearer to artifact kind than a per-installation choice — a docs repository versus a code repository — but a project is still not an artifact.

**Decision: restate, do not drop.** 06 §6's `register` becomes a description of the conversational register the profile selects — coding-terse versus 하십시오체 with an address term — and the plugin description follows it. Dropping the distinction was the other candidate and is now the worse one: B9 makes adding a profile cost one style file, so the distinction is cheap to keep and the only thing wrong with it was the description.

### `policy_on` and `injection_point` — false by construction

Not one of the nine; found in E7's run, and the same kind of defect.

The logger sets both from the presence of the build stamp. Three runs in which no output style was selected, and the policy therefore did not apply, recorded `policy_on: true` and `injection_point: output-style`. A fourth recorded `injection_point: agent-definition` for a subagent that ran from a **project** definition carrying no policy at all.

Under the current build the error is mostly invisible, because installing the plugin does force the style. Under B9 it becomes structural, and it makes E2's three-arm control design unmeasurable: arm B records itself as arm C.

**Decision, in two parts.**

- **Rename to what is measured.** `plugin_present` is what the stamp establishes. `policy_on` is reserved for the truth and is not written unless something establishes it.
- **Era 02 supplies the truth from outside the hook.** The corpus generator knows which arm it ran and labels the record. That is enough for this era, and it is another thing the offline architecture makes easy.
- **Era 03 does not have that.** A live session would need the harness to tell a hook which output style is in effect, and P3 already showed `init.output_style` reports the configured value rather than the effective one. Whether any hook payload carries it is unmeasured, and it is the one thing on this page that era 03 cannot start without.

## What this pass changed about the era

Three items were expected to be deferred or deleted and were not:

- **`sub-to-sub`** was pre-authorised for deletion and turned out to be observable at session level.
- **`tokens.output`** was expected to need a calibration exercise and instead needs no estimate at all, because the corpus generator returns the true value.
- **`ko.change_rate`** was the item most likely to slip, and E2 had already found its mechanism.

The common cause is E1. Generating the corpus offline means a process outside the hook sees the whole session document, and three separate items 06 filed as "the hook cannot see this" stop being about the hook.

The cost is on the other side of the same trade: **every one of those three resolutions works for era 02's corpus and not for a live session.** Era 03 inherits a measuring apparatus whose three best-resolved fields are supplied by a generator it does not have.

## Subagent runs

None. Two live runs settled items 6 and 7, and the rest followed from evidence already recorded in E2, E7 and 06. Exploration runs used in this stage remain 4.
