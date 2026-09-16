# 07. E6 — what a gate does when it fires, and where it can live

> Stage document. `2-exploration`, agenda item E6 (see [`02_scope.md`](02_scope.md)).
> Sources: 04 §4.4 (`on_final_fail`) and §8 (the `ko.gate` contract), 06 §15, 05a's four leak gates, and a live probe ([`tests/runs/02-E6/stop-hook-gate.json`](../../../tests/runs/02-E6/stop-hook-gate.json)).
>
> `gate:` is not opened this era ([`02_scope.md`](02_scope.md)). What this document owes is the semantics and the placement, decided on evidence, so that the era that opens it is not guessing.

## What 04 designed

| | |
|---|---|
| Where it runs | an MCP tool, `ko.gate`, called by the model just before it emits |
| Retry | "fail이면 **실패 항목만 고쳐** 재호출한다. 최대 `N=2`" |
| After the last failure | `on_final_fail: block \| emit_with_flag` — required, and explicitly non-inheritable |
| Acceptance | "산출물 수락 여부는 `report.pass`로만 결정한다" |
| Claude Code wiring | `Stop, PreToolUse(Write) → ko.gate` |

Two of those four were never tested. This document tests them.

## The mechanism works — better than expected

**A `Stop` hook can send the model back.** A hook that writes `{"decision": "block", "reason": "…"}` to stdout stops the turn from ending, and **the `reason` string reaches the model as an instruction**: told to prefix its answer with a token, the regenerated reply carried it.

So a gate is enforceable on **the reply**, not only on a file write. That is more than 04 assumed — its design leans on an MCP tool the model must choose to call, which is advice of the same kind 06 §13.3 already conceded about preset order. The hook is not advice.

### The harness does cap the loop — and what it does at the cap is worse than stopping

A first draft of this section concluded that **the harness caps nothing** and that a forgetful gate is "an unbounded loop on the user's account". That was wrong, and it was wrong for a bad reason: the probe's hook relented after five blocks, which is *below* the cap, so the cap never fired and its absence was inferred from a run that could not have shown it.

Re-run with a hook that never relents: **it fired nine times and the turn ended anyway.** Documentation gives the default as eight consecutive blocks, raisable with `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`.

**But the result was empty.** `num_turns: 10`, `subtype: success`, `terminal_reason: completed`, and `result: ""`. The documentation describes the cap as ending the turn with a warning and letting the output through; what the caller actually received was nothing at all.

That matters more than the cap itself. A gate that never passes does not degrade into `emit_with_flag` — **it degrades into no answer.** Which means `on_final_fail` is not a choice between two behaviours; it is a choice between two behaviours and a third one the harness imposes if the gate forgets to choose.

`stop_hook_active` — `false` on the first Stop, `true` on every retry — is still the gate's own signal, and 04's `최대 N=2` is still a counter the gate keeps. What changes is the consequence of forgetting: bounded and silent, not unbounded.

### Three costs the design did not price

| | Observed |
|---|---|
| **Money** | Ten turns and **$0.20** for the prompt `1+1은?` — but the breakdown is 625 output tokens against **137,688 cache-read** tokens. The cost is per-turn context, not the retry's own work. The first draft quoted the headline as if it measured retry overhead; it does not |
| **The gate becomes visible** | By the fourth retry the model was explaining the hook to the user: *"Stop hook(gate.py)이 계속 번호만 올려서 응답을 막고 있어요."* A gate that keeps firing stops being infrastructure and becomes part of the product |
| **Latency** | Every retry is a full turn of generation |

The second is the one to take seriously. A gate is supposed to be invisible when it passes and corrective when it fails. Observed, it is neither once it fires more than a couple of times — it turns into a subject the model talks about.

## The conflict nobody recorded

**04's retry is 05a's third leak gate.**

05a lists four ways measurement leaks into judgement and names this one:

> **에이전트에게 값을 보여준다** | "조사 부재율이 0.3이니 다시 써라" | 토큰이 새고, **모델이 지표를 최적화하고, 그 전후 레코드가 비교 불가능해진다**

04's gate instruction is:

> fail이면 **실패 항목만 고쳐** 재호출한다

Telling the model which items failed *is* showing it categories of the measurement. Neither document noticed: 05a was written about the logger and 04 about the gate, and nothing compared them.

**Two channels, and the first draft merged them.** 04's retry runs through the model calling the `ko.gate` MCP tool and reading its own tool result — ordinary function calling, where the caller sees the result by construction. The `Stop` hook is a *second*, harness-enforced route, and it is the one probed here. The probe is evidence about the hook, not about the tool path, which was never exercised. The leak in 04's design is structural to any tool-result self-check and is reasoned from the spec text, not measured.

**And "the only channel" was wrong.** Three routes block a `Stop`, all measured: a JSON `reason`, a `block` with no `reason` at all, and exit code 2 with stderr. Documentation adds a fourth field, `systemMessage`, described as going to the user's transcript rather than to the model — a user-only channel the first draft did not know about and this probe did not exercise.

**This is not a reason to abandon the gate.** It is a reason to state what a firing gate costs: **every record produced after a gate fires is a record of a model that was told what it was being measured on.** Those records are not comparable with records from an unaided turn, and an era that mixes them silently has lost the thing it was measuring.

### Blind blocking is a real third option, and it does not work

`systemMessage` being user-only means a gate can block with a deliberately uninformative `reason` — *does not meet the bar, try again* — telling the model nothing about which check failed, while telling the user something specific. That is neither 04's targeted retry nor `emit_with_flag`: it is **rejection sampling**, and it looked like the clean answer.

It was probed. It is not clean.

| Block mode | Final reply |
|---|---|
| `reason: ""` | `대한민국의 수도는 서울입니다.` **+ "종료 훅 g.py가 응답을 막았지만 이유는 알려주지 않았습니다. 답변 자체는 바뀌지 않으…"** |
| no `reason` key | `…` **+ 'Stop 훅이 "Blocked by hook"…'** |
| exit 2 + stderr | `대한민국의 수도는 서울입니다.` — clean |

**The model notices being blocked and tells the user about it.** In the empty-reason case it also reported that its answer had not changed — it re-emitted the same text with commentary attached. So a blind block does not produce an unaided second sample; it produces a sample from a model that knows it was rejected and is now speculating about why, out loud, to the user.

The exit-2 run was not narrated, but its stderr text was uninteresting, and one sample cannot show that the channel differs.

So rejection sampling is available, is cheaper in leaked information than a diagnostic retry, and still does not give an untainted record. It is worth naming and it does not rescue the design.

### What follows for semantics: split the arms, do not choose between the modes

The first draft closed on a binary — block and accept the leak, or `emit_with_flag` and correct nothing. That framing is too narrow, and the correction came from asking the obvious question it had skipped: *if the gate removes the patterns we do not want, the output is better, and surely that difference is measurable?*

**It is. The first draft confused "this measurement is spoiled" with "measurement is spoiled."** A gate-on against gate-off comparison measures something real — what the user actually receives — and that is arguably the number that matters most to a user. What it cannot do is answer the question *this* era is asking.

| Question | Answered by gate on/off? |
|---|---|
| Is what the user receives better? | **yes** |
| Does the **policy** work? | no |
| Did the **model** get better? | no |

The second row is the era's question, and a gate hides it: **with a gate running, a good policy and a bad one both produce clean output**, because the gate cleans up after either. That distinction has a price attached — the policy is injected at build time and costs nothing per turn, while a gate re-runs the whole turn every time it fires. Pooling them makes it impossible to know which one is doing the work.

**So four arms, not two modes.**

| | gate off | gate on |
|---|---|---|
| **policy off** | floor | the gate's effect alone |
| **policy on** | **the policy's effect alone** — this era's question | what the product actually delivers |

- Left column: does the policy do anything. That is era 02.
- Bottom row: how much the gate adds on top. That is the era that opens `gate:`.
- Bottom right: the product's real quality, which is the number a user cares about.

### Two rules that make the gated arms readable

**1. A gated measurement is tautological in its own arm.** If the gate blocks em dashes and retries until none remain, the em dash count goes to zero. That records that the gate worked, not that the writing improved — measuring whether a filter filtered. **In an arm where a gate fires on a measurement, that measurement is not read.**

**2. Read what the gate was not watching.** Forcing the model to remove an em dash does not remove an em dash; it rewrites the sentence, and the rewrite can damage something nobody is checking.

Upstream already knows this and says so throughout its own taxonomy: `전멸 금지`, `주입 금지`, a whole entry called `삭제 과교정 금지`, and D-9 and D-10's instruction that polishing an ending must not *create* `결국` or `~하는 이유다`. **Fixing one pattern manufactures another**, measured by the people who wrote the patterns.

So the informative measurements in a gated arm are exactly the ones the gate is blind to. They are where displaced defects land.

### And still mark the records

- A record produced after a gate fired carries `gate_fired: true` and the retry count.
- Analysis **never pools** gated with ungated records — the same rule E4 applied to estimated against measured token counts, for the same reason.
- Which measurement the gate fired on is recorded too, because rule 1 above needs it: a reader has to know which column of that record is tautological.

## Where a gate can live

| Site | Enforces | Verdict |
|---|---|---|
| `Stop` hook | the reply | **Works, measured.** The only site that can hold a reply back |
| `PreToolUse(Write)` | a file write | The right site for artifacts. **Asserted, not probed** — and not the same mechanism: its deny is `hookSpecificOutput.permissionDecision` with `permissionDecisionReason`, a different shape from `Stop`'s top-level `decision` |
| MCP tool `ko.gate` | nothing | The model must choose to call it. Useful as a *service* the model can consult, not as a gate |
| The logger | — | **Forbidden.** 06 §11.1 and 05a: it does not judge and does not block |

**And the last row is thinner than it looks.** The logger already runs on `Stop`. It already receives `last_assistant_message`. It already parses the payload. What makes it not a gate is that it prints nothing and always exits 0 — **one `print` statement.** The separation between "the logger never judges" and "the gate blocks" is currently a convention inside one file, not a boundary.

**So: if a gate is built, it is a separate executable, registered as its own `Stop` hook.** Not a mode of the logger, not a flag. The logger's guarantee — that a logging failure can never change a session — is only checkable if the file that makes the guarantee contains nothing that could break it.

**One print statement is the wiring, not the gate.** What the logger already has is the plumbing: registered on `Stop`, receives `last_assistant_message`, parses the payload, always exits 0. What it does not have is any judgement — it computes `usable` (a 20-어절 count) and `masked` (a secret regex), neither of which is one of 04's checks. And 04's five capability modules — `features.py`, `change_rate.py`, `preserve.py`, `lint.py`, `spell.py` — **do not exist anywhere in the repository.** The engine is unbuilt; the socket it would plug into is already live. That is the actual shape of the risk, and it is not "nearly done".

**All of this was probed with `--plugin-dir`, not an installed plugin.** E7's run showed the install path changes other behaviours — namespace resolution, `--scope local` visibility — and confirmed the *logger's* `Stop` hook fires identically under a marketplace install. Nothing confirms that a *blocking* hook behaves the same once installed through the real distribution path. The verdict above is "works, measured" for the scratch load and unmeasured for the shipped one.

## What this era does

`gate:` is not opened, and nothing here changes that. What it hands forward:

- **Semantics.** `on_final_fail: block | emit_with_flag` survives as 04 wrote it. `block` is now known to be implementable on replies, which 04 assumed without evidence.
- **The retry counter belongs to the gate**, but forgetting it is bounded: the harness overrides after eight consecutive blocks (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) — and delivers an **empty result**, which is a third `on_final_fail` behaviour imposed rather than chosen.
- **A firing gate contaminates the record it produces**, and those records are marked and never pooled.
- **The gate is its own executable**, even though it shares `Stop` with the logger.
- **Blocking leaks whether or not it explains.** Three modes were measured and a fourth channel (`systemMessage`, user-only) is documented. A diagnostic `reason` teaches the model the metric; a blank one still tells it that it was rejected, and it says so to the user.
- **PreToolUse(Write) is asserted, not probed**, and its deny contract is a different shape.

- **Four arms, not two modes.** `policy {on, off} × gate {on, off}`. The left column is this era's question; the bottom right is the product's quality. They are different experiments and must not share an arm.
- **In a gated arm, do not read the measurement the gate fired on** — it is tautological — **and do read the ones it was blind to**, because that is where a forced correction displaces the defect.

The honest answer to "what does a gate do when it fires" is therefore two sentences rather than one.

**A gate that corrects teaches, and a model that has been taught is no longer a sample of an untaught model.** Rejection sampling looked like the way out and is not — the model notices being blocked and says so. But that spoils one comparison, not all of them: **an arm with a gate is still a valid sample of a system with a gate**, and that is a real thing to measure. What cannot be done is running one gate configuration and reporting the result as though it answered both questions.

Which mode to ship — corrective or `emit_with_flag` — stays a decision about what the tool is for, and it belongs in the era that opens `gate:`. What this era fixes is that the decision is now separable from the measurement instead of destroying it.

## One thing confirmed for E4

The `Stop` payload carries `session_id`. E4 found the record has none and proposed adding it; the value is right there in the payload the logger already reads, so the fix is the one line E4 said it was.

## Subagent runs

| # | Tier | Purpose | Verdict |
|---|---|---|---|
| E6-v | `mid` (Sonnet 5) | Adversarial check of the first draft against the hooks documentation | Found the central empirical claim false — the harness caps a stuck Stop hook at eight blocks — plus the missing `systemMessage` channel, the conflation of 04's MCP-tool retry with the Stop-hook route, the cache-dominated cost figure, the unprobed `PreToolUse` assertion with its different schema, and a wrong section citation. 112.6k tokens |

Four live probes, about $0.40 in total. The cap was then measured directly rather than taken from the documentation. **This document used one subagent run**; the stage's running total is in [`README.md`](README.md).
