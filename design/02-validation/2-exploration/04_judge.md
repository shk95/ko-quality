# 04. E3 — how much a judge must be measured before it is used

> Stage document. `2-exploration`, agenda item E3 (see [`02_scope.md`](02_scope.md)).
> Inputs: C3's raw output (`tests/runs/review/policy-eval-runs3.json`), `claude plugin eval --help` (Claude Code 2.1.273), 05a, and E2's reference-grade measurements ([`03_features.md`](03_features.md)).
>
> The concept asked: 일치도 몇 퍼센트, 표본 몇 건이 기준인가. This document answers with a statistic, a bar derived rather than chosen, a sample size, and a cost — and revises C3's reading of its own result.
>
> **A first draft was checked by an independent `mid` run and against the tool's own `--help`. Six things were wrong, one of them a recommendation built on a misreading of what C3's flags did.** Corrections are in place below and listed at the end.

## What C3 actually contains

The review reported C3 as twelve replies. The file holds **twelve replies, each carrying three judge votes — 36 judgments** — alongside the two mechanical counts. That is test-retest data, and it was never read as such.

**What produced the three votes matters, and the first draft got it wrong.** From `claude plugin eval --help`:

- `--runs <n>` — "Override per-case runs (default: `case.runs ?? 3`)". The number of **generations** per case. C3's `--runs 3` produced three distinct replies per arm.
- `-j, --concurrency <n>` — "Run up to `<n>` agent runs at once (1–8)". Parallelism, not voting. C3's `-j 3` bought speed and nothing else.
- The three votes per reply come from the `llm` grader itself, which votes internally. **Not a setting we chose, and not one this tool exposes.**

So the first draft's recommendation — judge once per input and spend the saved budget on more distinct inputs — was wrong twice over. `--runs 3` *was* the distinct inputs, and the voting cannot be turned off here. Withdrawn.

**And the judge is Haiku.** `--judge-model <model>` defaults to `haiku`, and C3 passed no override. Everything below is a finding about **the default Haiku grader in `claude plugin eval`, reading a rubric we wrote** — a much narrower object than "an LLM judge".

### Self-consistency: high, and not the reassurance it looks like

| | |
|---|---|
| Replies with three unanimous votes | **11 of 12** |
| Votes agreeing with their reply's own majority | **35 of 36** |

The only split is `agent-reply / without / run 2` — `[false, true, false]`.

**Consistency is precision, not accuracy.** The same twelve replies contain a verdict that is unanimously *wrong* (below). A judge can be perfectly repeatable and repeatably incorrect, and voting defends against the first failure only.

**Does the low split count show the errors are correlated?** Not on its own. Under i.i.d. per-vote error `e`, seeing at most one split in twelve replies happens 47 % of the time at e = 0.05 and 13 % at e = 0.10 — unremarkable. The first draft asserted correlation from this and should not have.

The argument needs both observations at once:

| per-vote `e`, i.i.d. | P(≤ 1 split in 12) | P(≥ 1 *unanimously wrong* verdict in 12) |
|---|---|---|
| 0.05 | 0.47 | 0.001 |
| 0.10 | 0.13 | 0.012 |
| 0.15 | 0.03 | 0.040 |
| 0.20 | 0.005 | 0.092 |

We saw **one split and one unanimously wrong verdict**. A small `e` makes the split count easy and the unanimous error nearly impossible; a large `e` does the reverse. No single i.i.d. rate explains both comfortably, and that is the evidence for correlated error. It is weak — n = 12 cannot separate these hypotheses — and it is stated as weak.

## What can be adjudicated, and what cannot

`formal-report`'s rubric contains a clause a string count decides outright:

> PASS if the reply addresses the user as "사용자님" at least once and speaks to the user in honorific Korean (높임말) throughout. **FAIL if "사용자님" never appears** or any sentence addressed to the user uses 반말.

| Arm | 사용자님 | Judge | Verdict |
|---|---|---|---|
| with, run 3 | 0 | FAIL | correct |
| without, run 1 | 0 | FAIL | correct |
| without, run 2 | 0 | FAIL | correct |
| without, run 3 | 0 | **PASS** | **contradicts its own rubric**, 3 votes to 0 |

`agent-reply`'s rubric has one mechanically checkable clause — no em dash — and one that is not. A FAIL is *permitted* by the second clause, so only replies that do carry an em dash are adjudicable: two, both correctly failed. The three with-plugin replies failed at zero em dashes cannot be adjudicated, because the record keeps a character count and not the reply.

**Six adjudicable, one wrong** — 17 %, 95 % CI **[0.03, 0.56]** (Wilson).

**An asymmetry in this document's own standard, named rather than hidden.** It refuses to adjudicate the agent-reply cases without the reply text, then accepts `sayongjanim = 0` without it. The justification: the formal clause names a literal string, and the record says the count came from the same reply the grader saw, so the only way it misleads is if the count itself is wrong. "Ends its prose in 합니다체" is a judgment no count stands in for. Defensible, not invisible.

**Requirement on any future judge run: retain the judged text and the judge's stated reason.** C3's most-quoted claim — that the judge failed three replies which "carry no em dash and end prose in 합니다체" — rests on reading done during the run. It may well be right. It is no longer evidence.

## What C3's sample could and could not support

| Observation | 95 % interval (Wilson) |
|---|---|
| 0 of 3 | [0.00, 0.56] |
| 0 of 6 | [0.00, 0.39] |
| 1 of 6 | [0.03, 0.56] |

At n = 3, zero events is consistent with a true rate up to about 56 %. **C3 had no power to estimate a rate.**

Its force came from something needing no power: one verdict contradicting a deterministic clause of the judge's own rubric. That is a counterexample, not an estimate — a logical fact about one run, and no amount of judge noise elsewhere dissolves it.

**That asymmetry is the answer to "how much must you measure".** Rejecting can cost one case. Accepting costs dozens.

## The bar, derived rather than chosen

A judge sits between the true difference and the number reported. For a binary verdict, with `Se` for sensitivity and `Sp` for specificity, the observed difference between two arms is the true difference times the **Youden index**:

```
p_observed        = p·Se + (1−p)·(1−Sp)
p_obs(A) − p_obs(B) = (Se + Sp − 1) · (p_true(A) − p_true(B))
```

`(1 − 2e)` — the first draft's formula — is the special case `Se = Sp = 1 − e`. The general factor is what matters, because a judge need not be symmetric.

| `Se + Sp − 1` | Share of the true difference that survives |
|---|---|
| 0.90 | 90 % |
| 0.80 | 80 % |
| 0.60 | 60 % |
| 0.50 | 50 % |
| 0.00 | none |

The effect this era chases is small — the only prior evidence is stop-slop-ko's blind 5:5. An instrument that halves it is not an instrument.

**The bar: each error direction's 95 % upper bound below 10 %**, keeping at least 80 % of whatever difference exists. Not a preference; the consequence of measuring a small effect with a fallible classifier.

### The assumption that can break the whole argument

The formula requires the judge's error rate to be **the same in both arms** (non-differential misclassification). If it is not, the difference picks up an additive term:

```
p_obs(A) − p_obs(B) = (1−2e_A)·p_A − (1−2e_B)·p_B + (e_A − e_B)
```

This is not attenuation. It can **manufacture** a difference where none exists, hide a real one, or reverse its sign, and no upper bound on the error rate constrains it.

**This ablation is exactly where that risk lives.** The arms differ by design — the policy-on arm is more polished, longer-sentenced, more uniformly honorific. A judge more forgiving of text that looks careful has an error rate that depends on the arm. Measuring both error directions does **not** address this: that is `Se` versus `Sp` within one arm, a different thing.

The only defence is to measure error rates **per arm**, which doubles the validation set again. Recorded as a cost, not solved here.

## Sample size

Computed with a **Wilson** interval at 95 %. Stating the method is not optional: at zero observed errors Wilson is the more conservative choice, and an exact Clopper–Pearson bound reaches the same guarantee with about 20 % fewer samples.

| Goal, zero errors | Wilson | Clopper–Pearson |
|---|---|---|
| upper bound under 10 % | n = 35 | n = 29 |
| upper bound under 5 % | n = 73 | n = 59 |

| Errors tolerated at the 10 % bar | Smallest n (Wilson) |
|---|---|
| 0 | 35 |
| 1 | 53 |
| 2 | 69 |
| 3 | 84 |

So **n ≈ 60–70 per error direction tolerates one or two errors, not more.** The first draft said "60–70, at most one or two" while its own table showed two errors failing at n = 64 (10.7 %); the boundary is n = 69.

**The unit of n is one graded reply with known ground truth, for one rule, in one error direction.** Not one judgment — C3's 36 judgments came from 12 replies, and three votes on one reply are not three observations.

**The validation set has to be built, not sampled.** Measuring the false-PASS direction needs replies that genuinely violate the rule. Drawn from ordinary output at rate `p`, reaching 60 of them takes 60/p draws:

| Natural violation rate | Draws needed |
|---|---|
| 5 % | 1,200 |
| 20 % | 300 |

Constructing the set with known labels is the only affordable route, and it carries its own cost: constructed violations may be more obvious than natural ones, which flatters the judge.

## Cost

C3 spent **$1.40 on 12 samples**. The per-run `cost_usd` covers a whole run — generating the reply *and* grading it — and nothing in the file or in `--help` separates the two. The with-plugin arm averaged $0.139 against $0.095 without, the gap being the plugin's context inside the generation, which confirms generation is in the number.

The honest unit is **$0.117 per generate-and-judge sample**, not $0.039 per judgment. The first draft divided a bundled cost by the vote count and attributed all of it to judging.

| Scenario | Cost per rule |
|---|---|
| 64 samples, one direction | $7.49 |
| 128 samples, both directions | **$14.98** |
| Naturally sampled at a 20 % violation rate | ~$35 per direction |
| Naturally sampled at a 5 % violation rate | ~$140 per direction |
| Per-arm error rates (the differential-error defence) | double again |

Against E2's six reference-grade measurements, a constructed-set Tier B is roughly **$90**. Affordable — and six times the first draft's figure, which was used to argue that adding a judge later is nearly free.

## The procedure: three tiers

| Tier | Question | Reference | n | Outcome |
|---|---|---|---|---|
| **A — disqualify** | Does the judge contradict a deterministic clause of its own rubric? | The rubric | as low as 1 | A unanimous contradiction disqualifies. A split one triggers a rerun |
| **B — screen** | Does it agree with a mechanical measurement where one exists? | E2's six reference-grade measurements, on a **constructed, label-balanced** set | ~60–70 per direction, per arm where differential error is a concern | Every upper bound under 10 % |
| **C — qualify** | Does it agree with a person on rules with no mechanical reference? | Human labels | budget-bound | The only thing that licenses use on `llm`-class rules |

The unanimous-versus-split distinction in Tier A is what the data supports: the contradicting verdict was 3 votes to 0, a reproducible state rather than a tail draw.

**Tier A on the existing evidence: the default Haiku grader, with our `formal-report` rubric, is disqualified.** It passed a reply its own rubric requires it to fail, unanimously.

**That verdict is narrower and more perishable than the first draft implied.** It names one judge model — the CLI default, not recorded in the artifact — one rubric wording and one tool version. A `--judge-model` override is a single flag, and **whether a stronger judge clears Tier A is an unrun experiment that costs almost nothing.** The review's phrasing, "the LLM judge is not a reliable instrument here", is true of what was tested and should not be read further.

## The problem the procedure cannot solve

Tier B runs only where a mechanical reference exists — and **where one exists, the judge is not needed.** The rules that require an LLM are the ones E2 classified `llm` precisely because nothing mechanical decides them.

Tier B is therefore a screen, not a qualification. Failing it disqualifies; passing it shows competence on the easy cases. Extending that to the hard ones is an assumption: that a judge validated on em dashes is also right about whether a sentence constituent was omitted but recoverable from context.

Tier C is the only real qualification, its reference is human labels, and 05a already closed the shortcut:

> 오탐률을 손으로 쟀는가 — `watch_hits`가 붙은 레코드를 직접 읽는다. **LLM에게 묻지 않는다.**

## What this means for era 02

**No `llm` grader produces a recorded value in this era.**

1. Tier C has not been run for any rule, and its reference is human reading time — the era's scarcest input.
2. E2 found the mechanical battery covers every rule that could serve as a reference, and much of the rest.
3. The concept already ordered it this way: 측정을 먼저, 판정기를 검증. Validating an instrument is not adopting it.

Instead: run Tier A against the cases that exist, put the bar and the procedure into the spec, and record any `llm` verdict as an annotation no threshold reads, tagged with the judge model and version so it can be discarded wholesale later.

The first draft closed by saying the cheapest-to-reverse path and the best path agree. **At $15 per rule rather than $2.50 that is a weaker claim, and it is stated as one.** Adding a judge later still costs far less than discovering mid-era that recorded judged values were wrong, which would cost the comparability of every record carrying them. The ordering holds; the margin is smaller than advertised.

## Handed to the spec

- Retain the judged text, the judge's reason and the judge model in every run record. Without them the run cannot validate anything, and C3's most-quoted claim is already unreproducible for that reason.
- Measure both error directions separately, and **per arm** where the arms differ by design — pooled rates cannot detect differential misclassification, which can invent a difference rather than shrink one.
- The bar is a 95 % upper bound under 10 % per direction, from the Youden attenuation `Se + Sp − 1`.
- n ≈ 60–70 per direction — one graded reply with known ground truth, not one judgment — on a **constructed, label-balanced** set. State the interval method; Wilson is used here and is conservative at zero errors.
- Tier A first: it can cost a single case, and its verdict attaches to a (judge model, rubric, tool version) triple, not to LLM judging.
- Before concluding anything about LLM judging in this project, run the one-flag experiment C3 never did: `--judge-model` above the Haiku default.

## Corrections to the first draft

| # | Was | Is |
|---|---|---|
| 1 | "Judge once per input; spend the saved budget on more inputs" | Withdrawn. `--runs` is generations, `-j` is concurrency, and the `llm` grader's voting is internal and not exposed |
| 2 | Errors are "plainly not independent" | The split count alone does not show that. The argument needs the split count *and* the unanimous error together, and it is weak at n = 12 |
| 3 | "The judge is consistent, not noisy" | Consistency is precision. The same data holds a unanimously wrong verdict; the two findings are now connected |
| 4 | `(1 − 2e)` attenuation | The general form is `Se + Sp − 1`. The differential-error case, which this ablation invites, is not attenuation at all and is now stated |
| 5 | "$0.039 per judgment", "$2.50 per rule" | $0.117 per generate-and-judge sample; **$14.98 per rule** for both directions, and $35–140 if the set is sampled rather than constructed |
| 6 | "60–70, at most one or two errors" | Two errors need n ≥ 69. The unit of n is a reply, not a judgment. The interval method is Wilson, and Clopper–Pearson would need ~20 % fewer |

## Subagent runs

| # | Tier | Purpose | Verdict |
|---|---|---|---|
| E3-v | `mid` (Sonnet 5) | Adversarial check of the first draft against the raw data — recompute every number, find what is overstated | Confirmed the arithmetic (self-consistency, adjudication, Wilson bounds, the $1.40 sum). Found the cost contradiction, the undeclared interval method, the missing unit of n, the natural-sampling gap, the differential-error assumption and the unsupported independence claim. 82.5k tokens |

The tool facts (`--runs`, `-j`, the internal voting, the Haiku default) were then read directly from `claude plugin eval --help` rather than taken from any report. Exploration runs used in this stage: 4.
