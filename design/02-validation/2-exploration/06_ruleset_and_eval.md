# 06. E5 — the `ruleset` role, the case format, and where the runner lives

> Stage document. `2-exploration`, agenda item E5 (see [`02_scope.md`](02_scope.md)).
> Sources: 06 §5.3 and §15; 04 §6, §13; `01a_findings_survey.md`; the two case formats already in the tree; and a probe of `claude plugin eval`'s validator ([`tests/runs/02-E5/eval-grader-types.json`](../../../tests/runs/02-E5/eval-grader-types.json)).
>
> Three questions: is a `ruleset` provider adopted or written, what shape does an eval case take, and which runner scores what.

## 1. The `ruleset` role — defer it

**What 06 left.** The role table has one line: `(검증 단계) ruleset | 결정론 규칙 | 미정 | 미정`. Both the multiplicity and the provider are undecided, and there is no `ruleset.schema.yaml` in `upstream/interface/` beside the four that exist.

**The provider 04 assumed does not exist in the lock.** 04 names `korean-report-skills` five times — as `lint.py`'s wrapper target, as a vendor directory, and as the value of `lint_ruleset` in two profiles. `upstream/lock.yaml` has four entries and that is not one of them.

**It is not a phantom, though.** `01a_findings_survey.md` found it: *JangHyun-bin/korean-report-skills — 115 치환 규칙 lint.py, 어미 자동 수정*, filed under "L3 gate 규칙", and `02_stack.md` put it at L3. It is a real repository, identified early, deliberately left out of era 01 with the rest of the gate layer. What it has never had is a licence check, a pinned commit, or a normalizer.

**Decision: do not adopt it in this era — but the first draft argued it badly.**

It said korean-report-skills would mainly add *line and column positions*, which measurement does not need. That undersells it. 01a describes **115 substitution rules in a working `lint.py` plus automatic ending correction**, and 04's `ko.lint` returns `{violations[{line, col, rule, level}]}` — where `rule` and `level` are a usable measurement on their own, separate from the positions. 04 also says `--fix`는 노출하지 않음, which means the *detection* code was always the intended reuse, not the positions.

And the comparison the first draft skipped is the expensive one. **E2's ~130 rules are entirely unimplemented.** Weighing a fifth provider against rules "the battery largely already has" compares coverage with coverage and ignores the labour: one side is running code, the other is a classified list nobody has written yet.

So the honest reasons to defer are two, and the load-bearing one is not about positions.

- **The licence has never been checked, the commit has never been pinned.** `upstream/lock.yaml` has four entries and this is not one of them. That is an unconditional blocker, independent of everything else, and it is the P0 work era 01 did for the other four.
- **Adoption is not just acquisition.** An interface schema (none exists for `ruleset`), a normalizer, provenance for every fragment, a build check — the P0-through-P4 apparatus, on a fifth vendor, inside an era whose job is to build a measuring instrument.

**Entry criterion, restated.** The first draft tied reopening to "a gate needs to report positions", which is out of scope this era and might never independently arise. The criterion that matches the real trade is: **revisit when the battery's implementation cost is known.** Once the exclusion pass and the first Tier 0 measurements exist, the question becomes concrete — how much of the remaining ~130 is left, and would 115 implemented rules under a checked licence cost less than writing them. That is a decision with numbers in it rather than a guess, and it belongs in the build stage's record. The licence check is worth doing early regardless, because it gates everything else and costs an afternoon.

## 2. The case format — there are two already, and they do different jobs

| | `tests/cases/*.yaml` | `tests/evals/claude-code/*/` |
|---|---|---|
| Written for | P1 and P2, by hand | `claude plugin eval` |
| Shape | `input` or `input_from: {upstream, path}`, `prompt_prefix`, `expect: {skill_fires, checks: [...]}` | `prompt.md` with frontmatter + `graders/*.md` |
| Who reads `expect` | **nobody** — `checks` is free prose: *"register kept (구어 종결 보존)"*, *"numbers kept"* | the tool's validator and grader engine |
| What it is | a human checklist with provenance | an executable suite |

The first format is not a defect — it did its job, which was to make a build step's verification legible. But `checks` as free prose cannot become an `expect` that a runner evaluates, and 05a's claim that "나중에 `expect:`만 채우면 케이스가 된다" is exactly the assumption 05a itself later retracted.

**04 §13.1's draft is the right starting point** and it is aimed at our runner, not at the tool:

```yaml
id, profile, register, input | task
expect:
  gate_pass: bool
  preserve: [string]
  max_change_rate: float?
  must_not_contain: [string]?
  trigger: bool?
```

**Two changes E2 and E3 force on it.**

- `gate_pass` and `max_change_rate` presume a gate and a change-rate procedure. `gate:` is out of scope this era and `ko.change_rate` has no procedure yet (E4 item 8). **They are dropped, not kept as dead fields**, and reintroduced by the era that builds them — 04 §14 already places both later. A schema that carries fields nothing reads is how `tests/cases`'s `expect` block became decorative.
- **`preserve: [string]` needs a pass condition.** `ko.preserve` returns `{violations[]}`, so listing a kind is not an expectation until the case says what counts as passing it — zero violations of that kind.
- The battery's natural expectation is **not** a boolean. Most measurements emit a ratio or a count, and a single upper bound does not cover them: `noun_ending_ratio` wants a maximum, `pos_ngram_diversity` wants a minimum, and some want a band. The general form, rather than one example:

```yaml
expect:
  <measurement>: {max: float} | {min: float} | {min: float, max: float} | {equals: value}
```

- **`trigger: bool?` is dropped too.** §3 gives the trigger role entirely to `claude plugin eval`, whose `tool_used` graders already do it. Keeping the field would duplicate the check in the runner that was explicitly not given the job.

## 3. Where the runner lives — two runners, and the split is forced

The decisive question was whether `claude plugin eval` can score mechanical rules at all. E3 disqualified its `llm` grader, and if that were the only mechanical-adjacent option the tool would be useless for measurement.

**It is not.** Its validator names six grader types:

```
regex | tool_order | tool_used | file_exists | llm | baseline
```

**There is a `regex` grader.** So mechanical scoring inside the tool is possible without the judge — something the first reading of C3 did not know, and which would have changed how that result was framed.

**But it is presence-matching, and that is the limit.** `regex` takes `pattern`, `flags` and `weight`. Probing for a negation field, `negate`, `must_not_match` and `expect` were all rejected as unrecognized keys. A regex grader passes when its pattern matches.

| E2 needs | Can `claude plugin eval` do it? |
|---|---|
| "contains X" | yes |
| "must not contain X" | only as a negative lookahead written into the pattern |
| "3 or more per paragraph" | only as a repetition count in the pattern |
| **a ratio** — share of sentences ending without `EF`, share of 체언 without a particle | **no** |
| Tier 1, anything morphological | **no** |
| Tier 2, input against output | **no** |

The regex engine is **JavaScript's `RegExp`**: a negative lookahead parses, and an inline `(?i)` is rejected as "unrecognized character after `(?`", so case-insensitivity goes in the `flags` field. The first draft asserted the lookahead route without testing it.

Ratios are most of the battery, and with no code grader there is no route to one. So the split is not a preference:

- **`claude plugin eval` keeps the trigger and regression role.** Does the skill fire, does the plugin load, does the policy reach the reply. Four of the six graders in the existing suite are `tool_used` and they do this well; it is what P5 built the suite for.
- **The measurement runner is ours, offline, over the corpus records.** Tiers 0, 1 and 2 live there, it can compute a ratio, and E1's architecture already requires a process outside the hook.

### Two roles, and a contradiction that came from confusing them

A first draft of this section said the policy channel would be checked with `regex` graders on the em dash and on `사용자님`, "**two of E3's four surviving reference measurements**". [`04_judge.md`](04_judge.md) says the opposite about one of them: `em_dash_count` is marked **do not use**, because `03_features.md`'s own false-positive table has it firing on an em dash inside a quoted sentence or a table. Only `사용자님` is among the four.

The error came from treating one list as if it answered two different questions.

| | Judge reference | Regression grader |
|---|---|---|
| Job | adjudicate a judge's verdict | detect that something changed between arms |
| Requirement | **no interpretive room** — a disagreement has to be the judge's fault | a signal that moves when the thing being tested moves |
| A false positive that fires in both arms | **fatal** — the disagreement is now ambiguous | **harmless** — it cancels in the delta |

So `em_dash_count` is **unfit as a judge reference and perfectly fine as a regression grader.** An em dash inside a quoted sentence is as likely with the plugin as without it, so it contributes nothing to the delta and cannot fake one. E3's disqualification stands and does not reach this use.

**The two `llm` graders in the existing suite are the two policy cases C3 re-ran.** Following E3 they stop scoring and stay as annotations, replaced by `regex` graders.

**One thing is lost in that replacement and has to be said.** The `agent-reply` rubric bundles two rules — *no em dash* **and** *prose sentences end on a predicate with a sentence-final ending*. A regex can carry the first. The second is `noun_ending_ratio`, which is Tier 1 and cannot be expressed here at all. **The trigger suite loses the ending check; the measurement runner gains it.** That is the correct place for it, and the suite is weaker than it looks until the runner exists.

### What the ablation machinery already does

The first draft never mentioned `--ablation with-without`, which is the flag most directly aimed at this era's question.

It runs a no-plugin baseline arm per case and reports a `WITH` score, a `W/OUT` score and a `Δ`, plus an aggregate mean delta. P5 already used it: all four skill triggers and both policy cases passed with the plugin and failed without, 6/6, mean delta 1. And `arm:` is a valid key on **any** grader — probed, it accepts `with-only | both` and rejects anything else — so a `regex` grader can be scored in both arms and get its delta computed by the tool.

**That covers arm A against arm C, and not arm B.** E2's three-arm design needs a middle arm — plugin installed, style unselected — and the ablation is binary: the plugin either loads or it does not. The one arm that isolates the policy from the skills is the one the tool cannot express.

So the mechanical rules that *are* regex-expressible should run through the ablation rather than be duplicated in our runner, and the three-arm comparison stays offline.

### `baseline`, checked rather than skipped

The first draft listed six grader types and analysed three. `baseline` was the one worth looking at, because it takes a `baseline_file` and could have been a stored-reference comparator.

It is not. It requires `baseline_file` (a `.jsonl` transcript) and is **LLM-judged** — a judge decides whether the run satisfies the criteria at least as well as the reference — which puts it under E3's disqualification along with `llm`, and `--max-cost-usd`'s help groups both as paid graders. `file_exists` and `tool_order` are self-evidently irrelevant here.

**And there are no custom-code graders.** `scaffold_script` sets up fixtures *before* the agent runs; nothing post-processes the output. That is what actually proves the claim below, rather than the narrower key-rejection test the first draft rested it on.

## 4. One thing 04 already got right

04 §13.3, written before any of this, requires that the judge model differ from the generating model, and that a subset of cases carry human labels so that judge agreement is recorded alongside the result.

E3 arrived at both independently and did not notice 04 had them. What E3 adds is the arithmetic 04 left out — the bar (each direction's 95 % upper bound under 10 %, from `Se + Sp − 1` attenuation), the sample size (60–70 per direction on a constructed set), and the cost. The requirement was already policy; it had no numbers.

Worth noting that C3 satisfied the first half by accident: the judge defaulted to Haiku while generation ran on Opus.

## Handed to the spec

- The `ruleset` role stays open with `JangHyun-bin/korean-report-skills` named. **Check its licence early** — that is the unconditional blocker. Revisit adoption once the battery's implementation cost is known, not on a gate-position trigger.
- `tests/cases/*.yaml` is a human checklist and is not converted — verified, nothing in `build/` or `tests/` parses it. New cases use 04 §13.1's shape with `gate_pass`, `max_change_rate` and `trigger` **dropped**, `preserve` given a pass condition, and `expect` generalised to `{min, max, equals}` forms.
- Two runners. `claude plugin eval` for triggers and regressions; ours, offline, for measurement. Regex-expressible rules run through `--ablation with-without` with `arm: both` rather than being duplicated offline.
- The two existing `llm` graders stop scoring. The em-dash half becomes a `regex` grader — **fit as a regression signal even though E3 disqualifies it as a judge reference**, because a false positive that fires in both arms cancels in the delta. The sentence-ending half has no expression here and moves to the measurement runner.
- **The tool's ablation gives arm A against arm C only.** Arm B — plugin installed, style unselected — is not expressible, and it is the arm that isolates the policy from the skills.
- Carry 04 §13.3 forward unchanged: judge model ≠ generating model, and human labels on a subset.

## Subagent runs

| # | Tier | Purpose | Verdict |
|---|---|---|---|
| E5-v | `mid` (Sonnet 5) | Adversarial check of the first draft | Found that §3 contradicted `04_judge.md` about `em_dash_count`; that `--ablation with-without` and `arm:` were never mentioned though they are the flags closest to this era's question; that `baseline` was listed and never investigated; that "positions" undersold korean-report-skills against a battery that is 100 % unimplemented; and that the `expect` shape was demonstrated rather than defined. 121.2k tokens |

The grader types, field names, `arm:` values and regex engine behaviour came from the tool's own validator and error messages — no model run, no cost. Exploration runs used in this stage: 8.
