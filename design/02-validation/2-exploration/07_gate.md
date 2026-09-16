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

### But the loop guard is advisory

The `Stop` payload carries `stop_hook_active`: `false` on the first Stop of a turn, `true` on every retry. That is the whole guard. In a probe where the hook blocked five times in a row, **the harness capped nothing** — six turns ran and the loop ended only because the hook relented.

So 04's `최대 N=2` is not something the harness enforces. **It is a counter the gate has to keep itself**, and a gate that forgets it is an unbounded loop on the user's account.

### Three costs the design did not price

| | Observed |
|---|---|
| **Money** | Six turns and **$0.14** for the prompt `1+1은?`. A retry re-runs the whole turn — tools, context, everything — not just the check |
| **The gate becomes visible** | By the fourth retry the model was explaining the hook to the user: *"Stop hook(gate.py)이 계속 번호만 올려서 응답을 막고 있어요."* A gate that keeps firing stops being infrastructure and becomes part of the product |
| **Latency** | Every retry is a full turn of generation |

The second is the one to take seriously. A gate is supposed to be invisible when it passes and corrective when it fails. Observed, it is neither once it fires more than a couple of times — it turns into a subject the model talks about.

## The conflict nobody recorded

**04's retry is 05a's third leak gate.**

05a lists four ways measurement leaks into judgement and names this one:

> **에이전트에게 값을 보여준다** | "조사 부재율이 0.3이니 다시 써라" | 토큰이 새고, **모델이 지표를 최적화하고, 그 전후 레코드가 비교 불가능해진다**

04's gate instruction is:

> fail이면 **실패 항목만 고쳐** 재호출한다

Telling the model which items failed *is* showing it the values. There is no way to run 04's retry without opening 05a's third door, and the `reason` string measured above is the door — it is the only channel a `Stop` hook has, and it goes straight into the model's context.

Neither document noticed. 05a was written about the logger and 04 about the gate, and nothing compared them.

**This is not a reason to abandon the gate.** It is a reason to state what a firing gate costs: **every record produced after a gate fires is a record of a model that was told what it was being measured on.** Those records are not comparable with records from an unaided turn, and an era that mixes them silently has lost the thing it was measuring.

### What follows for semantics

The resolution is not to soften the message but to **mark the records**.

- A record produced after a gate fired carries `gate_fired: true` and the count of retries.
- Analysis **never pools** gated and ungated records for any measurement the gate's reason mentioned. That is the same rule E4 applied to estimated against measured token counts, for the same reason.
- The control arm is ungated by construction, so an on/off comparison that includes gated records on one side is comparing two different things.

## Where a gate can live

| Site | Enforces | Verdict |
|---|---|---|
| `Stop` hook | the reply | **Works, measured.** The only site that can hold a reply back |
| `PreToolUse(Write)` | a file write | Works by the same mechanism, and is the right site for artifacts |
| MCP tool `ko.gate` | nothing | The model must choose to call it. Useful as a *service* the model can consult, not as a gate |
| The logger | — | **Forbidden.** 06 §2.3 and 05a: it does not judge and does not block |

**And the last row is thinner than it looks.** The logger already runs on `Stop`. It already receives `last_assistant_message`. It already parses the payload. What makes it not a gate is that it prints nothing and always exits 0 — **one `print` statement.** The separation between "the logger never judges" and "the gate blocks" is currently a convention inside one file, not a boundary.

**So: if a gate is built, it is a separate executable, registered as its own `Stop` hook.** Not a mode of the logger, not a flag. The logger's guarantee — that a logging failure can never change a session — is only checkable if the file that makes the guarantee contains nothing that could break it.

## What this era does

`gate:` is not opened, and nothing here changes that. What it hands forward:

- **Semantics.** `on_final_fail: block | emit_with_flag` survives as 04 wrote it. `block` is now known to be implementable on replies, which 04 assumed without evidence.
- **The retry counter belongs to the gate**, because `stop_hook_active` is advisory and the harness caps nothing.
- **A firing gate contaminates the record it produces**, and those records are marked and never pooled.
- **The gate is its own executable**, even though it shares `Stop` with the logger.
- **The `reason` string is a measurement leak by construction.** There is no version of a corrective gate that does not tell the model what it failed. The choice is to accept that and mark the records, or to use `emit_with_flag` and correct nothing.

The last point deserves its own line, because it is the era's honest answer to "what does a gate do when it fires": **a gate that corrects teaches, and a model that has been taught is no longer a sample.** `emit_with_flag` is the only mode that leaves the measurement intact, and it is also the mode that fixes nothing. Choosing between them is a decision about what the tool is for, not a tuning parameter, and it belongs in the era that opens `gate:`.

## One thing confirmed for E4

The `Stop` payload carries `session_id`. E4 found the record has none and proposed adding it; the value is right there in the payload the logger already reads, so the fix is the one line E4 said it was.

## Subagent runs

None. Two live probes, $0.16 in total, settled the questions that mattered; the rest is a comparison between two documents already in the tree. Exploration runs used in this stage remain 8.
