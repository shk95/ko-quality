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

One execution constraint comes with it: a forced output style is exclusive and set at session start, so under the build as it stands the two profiles cannot alternate inside one session — every ablation run has to be made once per profile. The probe below reopens that.

## Measured while scoping: unforced plugin styles are selectable

One plugin can carry several output styles and let the user pick one, and switch between them mid-session, as long as none of them is forced. Seven headless runs, Claude Code 2.1.273, $0.47. Record: [`tests/runs/02-E1/unforced-style-selection.json`](../../../tests/runs/02-E1/unforced-style-selection.json).

| # | Plugin | `outputStyle` | agent-reply canary | formal-report canary |
|---|---|---|---|---|
| A | two styles, unforced | none | 0 | 0 |
| B | two styles, unforced | `ko-quality:formal-report` | 0 | **1** |
| C | two styles, unforced | `formal-report` | 0 | 0 |
| D | formal-report only, forced (control) | none | 0 | 1 |
| E | two styles, unforced | `ko-quality:agent-reply` | **1** | 0 |

- **B and E:** two styles inside **one** plugin each applied when selected, each showing only its own canary. P3's "formal-report is unreachable" holds only *while another style is forced*. Drop `force-for-plugin` and both profiles are reachable from a single plugin.
- **C is new.** The bare name does not resolve; `<plugin>:<style>` is required. P3 recorded both forms as "accepted", but a forced style won every P3 run, so the two forms were never told apart.
- **A is the price.** Installing alone does nothing. That breaks 06 §1's "a tool that is used once installed", which is exactly why `force-for-plugin` was set in the first place.
- **Switching works, both ways, and persists.** A multi-turn run through `--input-format stream-json`: turn 1 `default`, no canary; turn 2 `/output-style ko-quality:formal-report`; turn 3 CANARY-FORMAL. A second process in the same directory, given no setting on the command line, still answered CANARY-FORMAL, switched to `ko-quality:agent-reply` and answered CANARY-AGENTREPLY.
- **The choice is stored per project**, in `<project>/.claude/settings.local.json`. `~/.claude/settings.json` was unchanged (sha1 identical to the pre-run snapshot). Under forcing the profile is a property of the *installation*; unforced, it becomes a property of the *project*.
- **P3 still holds.** P3 found `init.output_style` echoes the configured value rather than the style in effect. Here the two agree, because nothing is forced. The side effect is that in an unforced design the field becomes usable as evidence again, which reopens P7's `injection_point`.

This reopens a decision era 01 closed. Decision ② (P5) chose one plugin per profile because a forced style is exclusive — which is true, and was the only option *given* forcing.

| | Now: forced, two plugins | Alternative: unforced, one plugin |
|---|---|---|
| After install | Works immediately | The user must select once |
| Adding a profile | Another plugin (440K, 84% of it byte-identical skills) | Another style file (~2KB) |
| Switching mid-session | Impossible | `/output-style`, effective from the next turn |
| Scope of the choice | Per installation | Per project, kept in `.claude/settings.local.json` |
| This era's ablation corpus | A separate run per profile | Profiles can alternate inside one session |

The last two rows are why this belongs to E1 and not only to the spec. Under the current build the corpus must be run once per profile, which doubles it; with switching, one process can alternate profiles across turns — and the `--input-format stream-json` shape used for this probe is already the skeleton of the corpus generator.

The per-project scope also blunts the objection. "Installing does nothing" becomes "choose once per project, and it stays chosen", and a per-project profile fits the distinction the toolkit was after better than a per-installation one: formal-report in a docs repository, agent-reply in a code repository.

**Not decided here.** This is a 06 §9 (policy channel) and §12 (distribution layout) revision candidate — **B9**, alongside review §B's B1–B8 — and it is settled in `3-spec`, not in this document. It still waits on E4's reading of whether the profile distinction survives at all (the `register` mismatch below): if E4 drops or restates the distinction, B9's premise changes with it. What is left unmeasured is the marketplace install path — the probe used `--plugin-dir`, not `claude plugin install`.

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
| E4 | Which of 06 §13.1's nine approximations close offline? | 06 §13.1; the concept's table; `assemble/profiles/*.yaml`, P3 | Per item: resolve now / era 03 / era 99 / delete. Includes the `task_type` rule not seeing writing done through `Write`, and the `register` mismatch below |
| E5 | `ruleset` role and eval case format | 06 §15; 04 §13.1 draft; `tests/evals/`, `tests/cases/` | Whether a ruleset provider is adopted upstream or written here; case format; where the runner lives |
| E6 | What does a gate do when it fires? | 04 `on_final_fail`; 06 §15 MCP tools; 05a's four leak gates | Gate semantics and where a gate can live, given the logger sits outside the harness and must not judge |
| E7 | Scope decisions | 06 §16.2; concept open questions 5–6 | stop-slop-ko as a `policy` fragment provider together with restoring `exempt`; what log text may be used for evaluation and for how long |

B1–B8 from review §B are spec input, not exploration questions. They are carried into `3-spec` unchanged.

### E4 carries one more item: `register` describes a channel the mechanism cannot see

`formal-report` declares `register: 사용자에게 전달되는 문서` — documents delivered to the user — and its plugin description says the same. Nothing in the build can act on that distinction.

- The profile's only main-thread channel is one forced output style, which applies to everything the model writes. There is no rule that separates "text going into a file" from "text going into the reply"; the sole exclusion is upstream's own first paragraph (quotes, code, code comments).
- The `honorific` block points the other way. "사용자를 '사용자님'이라고 호칭하고 … 사용자에게 반말이나 비존대로 발화하지 않습니다" is a sentence addressed **to the user**, not one that belongs inside a report.
- Measurement is reply-only as well. C3's mechanical marker was 사용자님 in the *replies*, and the logger records `last_assistant_message`; text written through `Write` never enters a record.

So what actually separates the two profiles is a conversational register (coding-terse vs. 하십시오체 with an address term), not an artifact kind. This is the same wall as the `task_type` rule not seeing writing done through `Write` (review §G, 06 §13.1): every attempt to tell artifact kinds apart runs into a mechanism that only sees the session's register.

E4 decides one of three: fix the rule so artifact kind is observable, restate `register` in 06 §6 to describe what the mechanism does, or drop the distinction. It is a 06 §6 revision candidate either way.

## Method

I investigate directly, and delegate to a `mid` subagent when a judgment is close or the sources are many — the `AGENTS.md` default, confirmed with the user 2026-09-16.

## What this stage left open

- **Concept open question 7 (Codex arrives late).** The offline route is Claude Code only. Whether the instrument stands up on Codex is re-judged when era 99 runs; it does not hold up era 02.
- **Whether the synthetic prompt set is representative.** By construction it is not a sample of real use. The defence is that era 02 produces candidate values and era 03 confirms them — but a prompt set that misses a whole kind of task would also hide a whole feature. E2 has to say what the prompt set covers and admit what it does not.
