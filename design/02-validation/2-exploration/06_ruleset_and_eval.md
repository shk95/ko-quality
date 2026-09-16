# 06. E5 — the `ruleset` role, the case format, and where the runner lives

> Stage document. `2-exploration`, agenda item E5 (see [`02_scope.md`](02_scope.md)).
> Sources: 06 §5.3 and §15; 04 §6, §13; `01a_findings_survey.md`; the two case formats already in the tree; and a probe of `claude plugin eval`'s validator ([`tests/runs/02-E5/eval-grader-types.json`](../../../tests/runs/02-E5/eval-grader-types.json)).
>
> Three questions: is a `ruleset` provider adopted or written, what shape does an eval case take, and which runner scores what.

## 1. The `ruleset` role — defer it

**What 06 left.** The role table has one line: `(검증 단계) ruleset | 결정론 규칙 | 미정 | 미정`. Both the multiplicity and the provider are undecided, and there is no `ruleset.schema.yaml` in `upstream/interface/` beside the four that exist.

**The provider 04 assumed does not exist in the lock.** 04 names `korean-report-skills` five times — as `lint.py`'s wrapper target, as a vendor directory, and as the value of `lint_ruleset` in two profiles. `upstream/lock.yaml` has four entries and that is not one of them.

**It is not a phantom, though.** `01a_findings_survey.md` found it: *JangHyun-bin/korean-report-skills — 115 치환 규칙 lint.py, 어미 자동 수정*, filed under "L3 gate 규칙", and `02_stack.md` put it at L3. It is a real repository, identified early, deliberately left out of era 01 with the rest of the gate layer. What it has never had is a licence check, a pinned commit, or a normalizer.

**Decision: do not adopt it in this era.**

E2 changed the premise this decision was going to be made on. The battery already has roughly 130 classified rules from the four locked upstreams, including ~47 fixed-phrase patterns from im-not-ai and ~46 from yoonmoon, with thresholds upstream derived from their own corpora. A fifth provider's 115 substitution rules would overlap that heavily.

What it would add is the thing measurement does not need: **line and column positions**. `ko.lint` returns `{violations[{line, col, rule, level}]}`, and positions matter when you are telling a model where to fix something — a gate's job, which is out of scope here. Counting does not need them.

What it would cost is a licence check, a commit pin, an interface schema, a normalizer, provenance for every fragment, and a build check — the full P0-through-P4 apparatus, for rules the battery largely already has.

So the role stays open with its candidate named, and the entry criterion is written down rather than left to judgement: **adopt a `ruleset` provider when a gate needs to report positions, not before.** That is era 03 at the earliest.

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

- `gate_pass` and `max_change_rate` presume a gate and a change-rate procedure. `gate:` is out of scope this era and `ko.change_rate` has no procedure yet (E4 item 8). Both become optional and unused rather than required.
- The battery's natural expectation is **not** a boolean. Most measurements emit a ratio or a count, so `expect` needs a numeric form — `expect: {noun_ending_ratio: {max: 0.1}}` — and that is what makes a case checkable at all once thresholds are candidates rather than settled.

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

Ratios are most of the battery. So the split is not a preference:

- **`claude plugin eval` keeps the trigger and regression role.** Does the skill fire, does the plugin load, does the policy reach the reply. Four of the six graders in the existing suite are `tool_used` and they do this well; it is what P5 built the suite for.
- **The measurement runner is ours, offline, over the corpus records.** Tiers 0, 1 and 2 live there, it can compute a ratio, and E1's architecture already requires a process outside the hook.

**The two llm graders in the existing suite are the two policy cases C3 re-ran.** Following E3, they are not deleted but they no longer score: they stay as annotations, and the policy channel is checked mechanically — `regex` for the em dash and for `사용자님`, which are two of E3's four surviving reference measurements.

## 4. One thing 04 already got right

04 §13.3, written before any of this, requires that the judge model differ from the generating model, and that a subset of cases carry human labels so that judge agreement is recorded alongside the result.

E3 arrived at both independently and did not notice 04 had them. What E3 adds is the arithmetic 04 left out — the bar (each direction's 95 % upper bound under 10 %, from `Se + Sp − 1` attenuation), the sample size (60–70 per direction on a constructed set), and the cost. The requirement was already policy; it had no numbers.

Worth noting that C3 satisfied the first half by accident: the judge defaulted to Haiku while generation ran on Opus.

## Handed to the spec

- The `ruleset` role stays open with `JangHyun-bin/korean-report-skills` named as its candidate and an entry criterion: adopt when a gate needs to report positions.
- `tests/cases/*.yaml` is a human checklist and is not converted. New cases use 04 §13.1's shape with `expect` extended to numeric forms, and with `gate_pass` and `max_change_rate` optional.
- Two runners. `claude plugin eval` for triggers and regressions; ours, offline, for measurement. Neither is asked to do the other's job.
- The two existing `llm` graders stop scoring and become annotations; the policy cases they covered are re-expressed as `regex` graders on the em dash and on `사용자님`.
- Carry 04 §13.3 forward unchanged: judge model ≠ generating model, and human labels on a subset.

## Subagent runs

None. The grader types and field names came from the tool's own validator, which reports them in its error messages — no model run was needed and the probe cost nothing. Exploration runs used in this stage remain 7.
