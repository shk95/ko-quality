# 04. E3 — how much a judge must be measured before it is used

> Stage document. `2-exploration`, agenda item E3 (see [`02_scope.md`](02_scope.md)).
> Inputs: C3's raw output (`tests/runs/review/policy-eval-runs3.json`), 05a, and E2's list of reference-grade measurements ([`03_features.md`](03_features.md)).
>
> The concept asked: 일치도 몇 퍼센트, 표본 몇 건이 기준인가. This document answers with a statistic, a number derived rather than chosen, and a procedure — and finds that C3's record supports a different reading of its own result than the review gave it.

## What C3 actually contains

The review reported C3 as twelve replies. The file holds **twelve replies, each judged three times — 36 judgments**, with a per-vote array alongside the majority verdict and the two mechanical counts. That is test-retest data, and it was never read as such.

### The judge is consistent, not noisy

| | |
|---|---|
| Replies with three unanimous votes | **11 of 12** |
| Individual votes agreeing with their reply's own majority | **35 of 36** |

The only split is `agent-reply / without / run 2` — `[false, true, false]`.

This closes off the comfortable explanation. A noisy judge can be improved by voting; an error rate of 50 % per vote falls to 50 % at three votes only if the errors are independent, and here they plainly are not. **Majority voting over three runs bought nothing and cost three times the money.** The first concrete recommendation follows directly: judge once per input, and spend the saved budget on more distinct inputs.

### What can be adjudicated, and what cannot

`formal-report`'s rubric contains a deterministic clause: *FAIL if 사용자님 never appears*. The record carries the 사용자님 count, so every reply with a count of zero has a verdict fixed by the rubric itself.

| Arm | 사용자님 | Judge | Verdict |
|---|---|---|---|
| with, run 3 | 0 | FAIL | correct |
| without, run 1 | 0 | FAIL | correct |
| without, run 2 | 0 | FAIL | correct |
| without, run 3 | 0 | **PASS** | **contradicts its own rubric**, unanimously (3/3 votes) |

`agent-reply`'s rubric has one mechanically checkable clause — no em dash — and one that is not (predicate endings outside headings and lists). Two replies carried em dashes and were correctly failed. The three with-plugin replies that were failed at zero em dashes **cannot be adjudicated from the record at all**: a FAIL is permitted there if the ending clause failed, and the record retains only a character count, not the reply.

So of twelve replies, **six are adjudicable and one is wrong** — a point estimate of 17 %, with a 95 % confidence interval of **[0.03, 0.56]**.

This matters for how the earlier finding is stated. The review wrote that the judge "failed all three agent-reply replies with the plugin, which carry no em dash and end prose in 합니다체". The 합니다체 half of that came from reading the replies during the run; it is not in the record and cannot be re-checked. The claim may well be right. It is simply not evidence any more.

**Requirement on any future judge run:** retain the judged text and the judge's stated reason. A verdict that cannot be re-examined cannot be used to validate anything, and C3's strongest published claim is currently unreproducible for exactly that reason.

## What C3's sample size could and could not support

| Observation | 95 % interval | Rule of three, upper bound |
|---|---|---|
| 0 of 3 | [0.00, 0.56] | 1.00 |
| 0 of 6 | [0.00, 0.39] | 0.50 |
| 1 of 6 | [0.03, 0.56] | — |

At n = 3, observing zero events is consistent with a true rate anywhere up to about 56 %. **C3 had no power to estimate a rate.**

Its force came from something else entirely: a single verdict that contradicts a deterministic clause of the judge's own rubric, reached unanimously. One such observation is decisive regardless of sample size, because it is not a rate estimate — it is a counterexample.

**That asymmetry is the answer to "how much must you measure".** Rejecting a judge can cost one case. Accepting one costs dozens.

## The bar, derived rather than chosen

Picking "90 % agreement" out of the air would repeat the mistake 05a warned about for thresholds — 직감으로 숫자를 박는다. The bar follows instead from what the judge is for.

A judge is a measuring instrument placed between the true difference and the number reported. For a binary verdict with symmetric error rate `e`, a difference in proportions between two arms is observed attenuated by a factor of **(1 − 2e)**:

| `e` | Share of the true difference that survives |
|---|---|
| 0.05 | 90 % |
| 0.10 | 80 % |
| 0.20 | 60 % |
| 0.25 | 50 % |
| 0.50 | 0 % |

The effect this era is chasing is small — the only prior evidence is stop-slop-ko's blind 5:5, which says the difference is hard to see at all. An instrument that halves it is not an instrument.

**The bar: both error rates' 95 % upper bound below 10 %**, which keeps at least 80 % of whatever difference exists. Not a preference — the consequence of measuring a small effect with a noisy classifier.

### The sample size that bar implies

| Goal | Needed |
|---|---|
| 95 % upper bound under 10 % with zero errors | **n = 35** |
| 95 % upper bound under 5 % with zero errors | n = 73 |
| n = 64 with 2 errors | upper bound 10.7 % — just misses |
| n = 100 with 2 errors | upper bound 7.0 % |

So **n ≈ 60–70 per error direction**, tolerating at most one or two errors. Both directions have to be measured separately: C3 showed the judge erring in both, and a judge wrong in both directions has no monotone relationship to the truth, so no offset can correct it.

The cost is not the obstacle. C3 spent $1.40 on 36 judgments — **$0.039 each**. At one vote per input, n = 64 is **$2.50 per rule**. At three votes it is $7.49, for nothing, as shown above.

## The procedure: three tiers

| Tier | Question | Reference | n | Outcome |
|---|---|---|---|---|
| **A — disqualify** | Does the judge ever contradict a deterministic clause of its own rubric? | The rubric itself | as low as 1 | One contradiction disqualifies. No appeal |
| **B — screen** | Does it agree with a mechanical measurement where one exists? | E2's six reference-grade measurements | ~60–70 per direction | Both upper bounds under 10 % to pass |
| **C — qualify** | Does it agree with a person on the rules that have no mechanical reference? | Human labels | budget-bound | The only thing that licenses use on `llm`-class rules |

**Tier A on the existing evidence: the `claude plugin eval` judge is disqualified.** It passed a reply its own rubric requires it to fail, unanimously. That is the finding C3 reached, and it survives re-reading — but it rests on the counterexample, not on the 0/3 pattern the review foregrounded.

This is a verdict on *that* judge with *that* rubric, not on LLM judging in general. The procedure is what transfers.

## The problem the procedure cannot solve

Tier B can only run where a mechanical reference exists — and **where a mechanical reference exists, the judge is not needed.** The rules that require an LLM are exactly the ones E2 classified `llm` precisely because nothing mechanical decides them.

So Tier B is a screen, not a qualification. Failing it disqualifies; passing it establishes only that the judge is competent on the easy cases. Extending that to the hard cases is an assumption, and it is the assumption that a judge validated on em dashes will also be right about whether a sentence constituent was omitted but recoverable from context.

Tier C is the only real qualification, its reference is human labels, and 05a already forbade the shortcut:

> 오탐률을 손으로 쟀는가 — `watch_hits`가 붙은 레코드를 직접 읽는다. **LLM에게 묻지 않는다.**

## What this means for era 02

**No `llm` grader produces a recorded value in this era.** Three things point the same way:

1. Tier C has not been run for any rule and costs human reading time, which is the era's scarcest input.
2. E2 found the mechanical battery covers every rule that could serve as a reference, and a large share of the rest.
3. The concept already ordered it this way — 측정을 먼저, 판정기를 검증. Validating an instrument is not the same as adopting it.

What the era does instead: run Tier A once against the cases that exist, document the bar and the procedure above in the spec, and record `llm` verdicts — if any are produced at all — as annotations that no threshold reads. If a later era wants a judge, the procedure and the numbers are already written.

**The cheapest-to-reverse path and the best path agree here**, which is unusual enough to note. Adding a judge later costs one Tier B run at $2.50 per rule. Recording judged values now and discovering the judge was wrong costs the comparability of every record that carried them.

## Handed to the spec

- Judge once per input. Majority voting over an autocorrelated judge buys nothing (35/36 votes agreed with their own majority).
- Retain the judged text and the judge's stated reason in every run record, or the run cannot be re-examined.
- Measure both error directions separately and report them separately. Never a single accuracy number.
- The bar is a 95 % upper bound under 10 % on each direction, because (1 − 2e) attenuation below that starts eating a small effect.
- n ≈ 60–70 per direction, at most one or two errors.
- Tier A disqualification is a permanent property of a (judge, rubric) pair, and is worth running before anything else because it can cost a single case.

## Subagent runs

None. The sources were one JSON file and two design documents already in context, and the work was arithmetic rather than reading. Exploration runs used in this stage remain 3.
