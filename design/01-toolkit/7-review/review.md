# 7-review — era 01-toolkit

2026-09-15. Branch `review/01-toolkit` off `dev` (`13ebced`). Input: `6-build/P1`–`P7`. **Status: agenda drafted, decisions pending with the user.**

Each item has a recommendation and a confidence. A decision is written into the item's "Decided" line when the user settles it; nothing here is decided by the agent alone.

## A. Release-blocked marks → merge `dev` to `master`

All three marks are on the Codex side. Codex could not be run in this era, so none can be resolved by testing now.

| # | Mark | Stage | Nature | Recommendation | Confidence |
|---|---|---|---|---|---|
| A1 | Named custom agent (`korean-reviewer`) reached in 1 of 6 Codex delegation attempts; project-scope agents never offered; `--ephemeral` breaks spawns | P6 | Harness behavior, not our build. Policy still reaches the main thread (AGENTS.md) in every run | **Accept** for merge. Install doc already says delegation may fail. Retest is a next-era item | medium-high |
| A2 | Subagent policy evidence cannot separate "subagent received the agent file" from "orchestrator saw it and relayed" | P6 | Measurement gap | **Accept**, carry the separate-capture run to the next era | medium |
| A3 | Codex logger records not produced; hook command relies on `CLAUDE_PLUGIN_ROOT` being set by Codex | P7 | Unmeasured, one known risk | **Accept**, with the install doc's existing "unverified" line. Retest deferred | medium |
| A4 | (open, non-blocking) `ko-quality-formal` never went through the marketplace install cycle | P5 | Coverage gap on Claude Code; can run now | **Resolve now**: one install → headless run → uninstall cycle, snapshot `~/.claude` first | high |

Merge options:

1. **Merge now, Codex marked unverified** (recommended). `master` gets a Claude Code build verified end to end and a Codex build whose skills, AGENTS.md policy and installer are verified and whose agents and logger are not. The Codex retests become the first work of the next era.
2. **Wait for the Codex retest**, retest A1–A3, then merge. Blocks `master` until Codex can be run.
3. **Merge Claude Code only**, keep `dist/agent-plugin/` off `master`. Splits the build and breaks checks 2–4's cross-harness scope on `master`.

Decided: —

## B. Spec 06 items the build overturned

Each is either a spec revision (next era's spec) or a build error. All below read as revisions; none is a build error.

| # | § | What the build found | Proposed revision | Source |
|---|---|---|---|---|
| B1 | §7 | SKILL.md body also holds self-check, grades, options and the calling convention; output contracts moved to `references/` for the 100-line budget; references live inside the skill directory | §7: "procedure (steps, invariants, self-check, grades, options) and calling convention; non-step material moves to `references/` first" | P1, P2 |
| B2 | §7 | Taxonomy isolation holds per skill, not per context (diagnose-and-fix loads both into main) | §7: "each skill reads only its own references; context separation is an agent-level property" | P2 |
| B3 | §9 | Composition rule settled (decision ③ table); forcing one style makes the other profile's style unselectable | §9: the P3 table, plus the consequence that leads to ② | P3 |
| B4 | §12 | One plugin per profile per harness plus a marketplace; no `$schema` in Codex `plugin.json`; no `mcp.json`/`.mcp.json`; stamp per plugin root without timestamps | §12 table rewritten to the built layout | P5, P6, P7 |
| B5 | §2.2 | Codex custom agents unreliable under `codex exec` 0.154.0; project-scope agents not offered; installed OpenAI plugins use `.codex-plugin/plugin.json` | §2.2: custom agents marked unreliable with version; manifest location noted | P6 |
| B6 | §13.1 | Removal traces: Claude Code `extraKnownMarketplaces` and orphaned cache; Codex empty cache dir | §13.1 or install section | P5, P6 |
| B7 | §11 | `model` absent from Claude Code hook input headless; `preset` has no hook source; `task_type` rule cannot see writing-through-`Write`; stamp shape | §11.2–11.3: mark `preset` and `model` as possibly unknown; stamp fields | P7 |
| B8 | §5.5 | Positional anchors held over 10 upstream commits; repeated anchors need ` > N`; fence-aware parsing | §5.5: add the `repeated` form and fence rule | P4 |

Decided: —

## C. Decisions to revisit

| # | Decision | Evidence since | Recommendation | Confidence |
|---|---|---|---|---|
| C1 | ko-rewrite path note instead of shipping `references/quick-rules.md` (P1 d1, P6 d6) | Held 7/7 on Claude Code; Codex luna tried the upstream path first and recovered with two extra calls | Keep for now; if the next era's Codex retest shows failures, ship the file under upstream's name in both harnesses (spec deviation, no `adapted`) | medium |
| C2 | Normalized format kept as built (P4 d1): provenance repeated per fragment, text as JSON strings, whole-file references fragmented | P5 was the first consumer and did not need a new shape; the renderer added layout (+1134 lines) | Redesign in the next era only if it is also the era that touches extractors; otherwise keep. Readability of Korean in review is the real cost | medium |
| C3 | `claude plugin eval` at runs 1 (P5 d4) | Trigger cases always delta 1 under ablation; only policy cases informative | Rerun only the two policy cases at runs 3 (~$1) now, or fold into the validation era's eval | medium |
| C4 | Root `plugin.json` for Codex (P6 d4) | Works; installed OpenAI plugins use `.codex-plugin/` | Keep; add `.codex-plugin/plugin.json` only if a Codex release stops reading root | medium |

Decided: —

## D. What preflight missed (input to the next era's preflight)

- **An unavailable harness as a blocker.** Codex could not be run mid-build, which turned three clauses into release-blocked. Next preflight: confirm each harness is available for the planned runs, and list "harness unavailable" as a release-blocked condition with its fallback.
- **Settings echo is not state.** `init.output_style` reports the configured style, not the one in effect (P3). Any check that reads harness state needs a canary.
- **Forced styles are exclusive.** Two forced styles: first loaded wins (P3, P5). This drove decision ②; preflight D4 had the fallback but not the cause.
- **Hook environment per harness.** Variable names in hook commands should be checked live per harness before sharing one hook file (P7).
- **Shell heredoc hazard.** Two stalls from backticks in unquoted heredocs (P4, P5). A process note for `AGENTS.md`: long text goes through file-writing tools or script files.

## E. Subagent tier rules

Runs recorded across P1–P7:

| Tier | Runs | Of which exploration | Tokens |
|---|---|---|---|
| small (Haiku 4.5) | 1 (P1 mechanical diff) | 0 | 67.7k |
| mid (Sonnet 5) | 9 (7 verification, 2 exploration: P4 abstraction test, P6 Codex docs) | 2 | 1,104.8k |
| docs lookup (`claude-code-guide`) | 1 (P5) | 1 | 86.3k |
| large | 0 | 0 | 0 |

Exploration cap use: 3 of 28 (P1–P7 × 4). Total ≈1.26M tokens.

- **large never triggered.** No two `mid` reports disagreed on a major decision, and P4/P7's "weigh four or more sources" case was covered by one `mid` run (P4) or needed no run (P7). There is no evidence either way on whether `large` would change outcomes.
- **Verification runs found real issues** in P1, P3, P4, P6 and P7 (log gaps, a swallowed import error, the P6 evidence reservation, the P7 hook variable). The one-per-stage verification rule earned its cost.
- **The cap of 4 was never close.** Most stages settled decisions from live runs, not exploration.
- **A tier the table lacks:** the docs-lookup agent (P5) is neither mechanical nor judgment.

Recommendation: keep the tiers and the verification rule; lower nothing; add the docs-lookup agent as an allowed `mid`-equivalent for documentation questions; keep the `large` conditions unchanged and re-evaluate after an era that actually uses one. Confidence medium (small sample).

Decided: —

## F. Next era

Candidates:

1. **Validation stage** (06 §15: gate, `features`, `watch:`, eval). The logger now accumulates the records it needs on Claude Code. Recommended first candidate.
2. **Codex channel follow-up** (A1–A3 retests, C1, C4, deferred). Small; could be the first stage of era 02 rather than an era of its own.
3. **Format redesign** (C2). Only worth an era if validation needs readable normalized data.

Decided: —
