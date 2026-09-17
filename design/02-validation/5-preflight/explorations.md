# Preflight explorations — raw material, not decisions

2026-09-17. What `flow.md` needs to know before it can pre-decide the build. **Nothing below is decided**: decisions are in `flow.md` §1. Each exploration names the question, why the build needs the answer, the method, and its status. Probe records go to `tests/runs/02-preflight/`.

## Environment

| Item | Value | Note |
|---|---|---|
| Claude Code | 2.1.274 | 09 §2.1's facts were measured on 2.1.270–2.1.273. X2 re-checks the ones the build depends on |
| Codex | codex-cli 0.154.0 | Unchanged since era 01 and era 99 |
| Python | 3.9.6 (system) | The logger and build stay stdlib on this version. `measure/` uses a virtualenv (S3) |
| Branch | `dev`, clean | — |
| This repository's local style | `.claude/settings.local.json` holds `outputStyle: "Concise"` | P3 removes it (09 §21.2), with the user's consent (`flow.md` §4) |

## X1 — `github` marketplace source from committed settings (L4)

- **Question.** Does a marketplace declared in the committed `.claude/settings.json` with a `github` source (this public repository, `dist/claude-code` path) load the plugin in a headless session launched at the repository root, with no per-machine `marketplace add`?
- **Why.** If yes, P3 drops a per-machine step (09 §21.2). If no, the step stays. The build does not depend on the answer.
- **Method.** Scratch clone of the repository at a pushed commit, no user-scope marketplace, one headless run with a canary style. Cleanup: remove any marketplace and cache the run registered.
- **Caveat.** A `github` source reads the pushed remote, not the working tree. Until P1 is pushed, the remote holds era 01's layout, so the probe tests the mechanism, not the new plugin.
- **Status.** Not run.

## X2 — canary device and B9 facts on 2.1.274

- **Question.** On the current CLI: (a) an unforced plugin style applies only when selected in the project's `settings.local.json`; (b) it resolves as `<plugin>:<style>`; (c) a shipped agent's canary appears under either selected style; (d) no hook payload carries the selected style. These are the facts P1.2–P1.3 and P8.1 rest on.
- **Why.** 09 §2.1 measured them on 2.1.273. A changed fact would change P1's done-conditions or P8's arm construction, and must be known before the build.
- **Method.** 02-E1's device: throwaway plugin under the scratchpad, two unforced styles each emitting a canary token, one agent with its own canary, a raw-payload dump hook. Runs: no selection, each selection, one delegation. About 5 headless runs.
- **Status.** Not run.

## X3 — `kiwipiepy` in a virtualenv on this machine

- **Question.** Does `kiwipiepy` 0.23.2 install into a virtualenv on Python 3.9.6 here, and do E2's two fixed recipes run?
- **Why.** P6 pins it (S3). E2 installed it once, in a throwaway environment that was removed.
- **Method.** Scratch virtualenv, install, analyse two sentences, record versions, remove the environment.
- **Status.** Not run.

## X4 — harness availability

- **Question.** Can each harness run P2's live runs (both harnesses) and P8–P9's batches?
- **Why.** In era 01, Codex could not be run mid-build, which produced three release-blocked marks (review §D).
- **Method.** One minimal headless run per harness now.
- **Status.** Not run.

## X5 — cost of the pilot and the batch

- **Question.** What do P8's pilot and P9's batch cost, so the user can set a ceiling?
- **Why.** P9 is release-blocked if the sized batch exceeds the ceiling (`10_plan.md` P9).
- **Method.** Arithmetic from 09 §18.4 ($0.12 per headless run, C3 and E1) and the pilot shape pre-decided in `flow.md` §1, checked against the cost of X2's runs on the current CLI and the pinned generator model.
- **Estimate (before X2).** Pilot: 9 strata × 3 prompts × 3 arms = 81 sessions, plus 3 canaries. Arm C alternates both profiles in one session, so its sessions are about two turns. At $0.12–$0.25 per session: **about $10–$21.** The batch cannot be estimated until the pilot's variance exists: at 30 sessions per arm per stratum it would be about 9 × 30 × 3 = 810 sessions, **about $100–$200.**
- **Status.** Estimate only.

## X6 — hook trust for Codex in automation

- **Question.** Can the build run `codex exec` with the plugin's hooks trusted, in a temporary `CODEX_HOME`?
- **Why.** P2.3 needs a live Codex session with the logger. In era 01, `--dangerously-bypass-hook-trust` was blocked by the auto-mode classifier until the user granted a permission rule. Era 99 ran with hooks.
- **Method.** Confirm the rule is still in place with one throwaway run (scratch `CODEX_HOME`, `auth.json` symlinked, never the user's `~/.codex`).
- **Status.** Not run.

## What `flow.md` must still settle

- The power parameters for P8.4 and the budget ceiling: **the user's** (`flow.md` §4).
- Whether X1–X4 and X6 run now, in preflight, or whether some are left to the step that needs them.
