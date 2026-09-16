# 02. Scope: what this era can measure without a session corpus

> Stage document. Opens `2-exploration`. Input: [`../1-concept/01_idea.md`](../1-concept/01_idea.md).
>
> This document corrects a premise the concept inherited and fixes the era's boundary. The investigation itself (E2–E7 below) follows in this directory.

## The premise that did not hold

The concept and review §G both treat the logger's accumulating records as this era's material: "the logger now accumulates the records it needs on Claude Code."

It does not. `~/.ko-quality/` does not exist on the development machine — zero records, no `logs/`, no `state/`, no `logger-errors.log`. The A4 install test (review, 2026-09-15) produced exactly one record and was then uninstalled along with the plugin. The toolkit has never been in daily use.

So the era opened with no corpus, and the three things the concept ordered first — `features`, judge validation, `watch:` initial values — had nothing to run on.

## Decision E1: a temporary corpus, built offline, through the real logger

Decided with the user, 2026-09-16.

Era 02 builds its own corpus from headless ablation runs rather than waiting for real sessions. Era 03 repeats the measurement on real session records.

The corpus comes from plain headless `claude -p` runs, with the plugin installed and not installed, and it **passes through the shipped logger** rather than a separate capture path. A4 proved that route works: a headless run fired the `Stop` hook and left a `usable: true` record for profile `formal-report` (review §A).

The consequence is the point of the decision. Era 02's corpus is **real records with a synthetic prompt distribution**. Era 03 swaps the distribution — not the record schema, not the features code, not the graders. Era 03 is a re-measurement, not a rebuild.

`claude plugin eval` is not the corpus generator. It is not established that its runner fires hooks, and C3 found its judge unreliable. It keeps the regression-gate role instead (E5).

**What the offline route buys**

- The control arm is balanced by construction. 05a's 72-strata sampling problem does not arise here: strata are assignable up front, because we choose the prompts.
- The control group costs no user-facing quality. The concept's open question 2 — may we turn the policy off in the user's own sessions — does not have to be answered in this era.
- It is cheap. C3 ran 2 cases × 3 runs × 2 arms for $1.40, about $0.12 per run.

**What it does not buy:** a real distribution. Anything whose answer depends on how the tool is actually used moves to era 03.

## Era boundary

Scope decided with the user, 2026-09-16: era 02 covers E2–E7 (the measuring instrument, gate semantics, and the scope decisions). Era 03 is **not opened now**; it opens at this era's `7-review`. Until then, this table is where its items are parked, and `6-build` records add to it.

### Era 02 settles

| Item | Why offline is enough |
|---|---|
| `features` computation and mechanical graders | Independent of the prompt distribution |
| Judge agreement measurement | Mechanical verdicts are the reference; the comparison does not need real prompts |
| on/off difference per axis | The offline arm is a control group by construction |
| `watch:` clause with candidate thresholds | Candidates only; confirmation is era 03 |
| eval runner and cases | Regression gate, run on fixed cases by design |
| gate semantics | Specified and designed. `gate:` is not opened |
| `ruleset` role | A supply-layer question, not a data question |
| stop-slop-ko + `exempt` | Decided here; whether it helps is measured with the instrument |

### Era 03 settles

| Item | Why it cannot close offline |
|---|---|
| `watch:` → `gate:` promotion | 05a condition 1 (distribution stabilized) needs a real distribution. Condition 2 (false positives measured by hand) can start offline but must be re-measured on real text. Condition 3 (on/off difference) does close offline |
| off rotation scheduler, control-group ethics | Offline "off" is a run configuration; there is no scheduler to build and no user cost to weigh |
| `outcome` field | A task result is only observable in a real session |
| `preset` source, `instruction_lang` (§13.1) | With synthetic prompts these values are the ones we wrote |
| `tokens.output` estimate error (§13.1) | The char/2.5 estimate can be calibrated offline; whether the calibration holds against real output lengths cannot |
| `sub-to-sub`, Codex `instructions` (§13.1) | Already waiting on era 99 |

## Exploration agenda

| # | Question | Sources | Output |
|---|---|---|---|
| E2 | Which rules are mechanically countable, which need an LLM, which need a person? | `upstream/normalized/policy/`, `taxonomy/`, `reference/grammar/`; C3 | The `features` list, each entry marked `mechanical` / `llm` / `human`. This is also where the concept's open question 1 ("what counts as better") gets answered |
| E3 | How much must a judge be measured before it is used? | C3; 05a | Agreement statistic, sample size, reference standard, and the bar below which an `llm` grader is not used |
| E4 | Which of 06 §13.1's nine approximations close offline? | 06 §13.1; the concept's table | Per item: resolve now / era 03 / era 99 / delete. Includes the `task_type` rule not seeing writing done through `Write` |
| E5 | `ruleset` role and eval case format | 06 §15; 04 §13.1 draft; `tests/evals/`, `tests/cases/` | Whether a ruleset provider is adopted upstream or written here; case format; where the runner lives |
| E6 | What does a gate do when it fires? | 04 `on_final_fail`; 06 §15 MCP tools; 05a's four leak gates | Gate semantics and where a gate can live, given the logger sits outside the harness and must not judge |
| E7 | Scope decisions | 06 §16.2; concept open questions 5–6 | stop-slop-ko as a `policy` fragment provider together with restoring `exempt`; what log text may be used for evaluation and for how long |

B1–B8 from review §B are spec input, not exploration questions. They are carried into `3-spec` unchanged.

## Method

I investigate directly, and delegate to a `mid` subagent when a judgment is close or the sources are many — the `AGENTS.md` default, confirmed with the user 2026-09-16.

## What this stage left open

- **Concept open question 7 (Codex arrives late).** The offline route is Claude Code only. Whether the instrument stands up on Codex is re-judged when era 99 runs; it does not hold up era 02.
- **Whether the synthetic prompt set is representative.** By construction it is not a sample of real use. The defence is that era 02 produces candidate values and era 03 confirms them — but a prompt set that misses a whole kind of task would also hide a whole feature. E2 has to say what the prompt set covers and admit what it does not.
