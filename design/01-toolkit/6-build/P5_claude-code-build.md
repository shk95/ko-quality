# P5 — assemble and Claude Code build

2026-09-14. Branch `dev`. Flow: `5-preflight/flow.md` §3 P5.

## Result

`python3 -m build.claude_code` builds two Claude Code plugins from `upstream/normalized/` and `assemble/`: `ko-quality` (profile agent-reply) and `ko-quality-formal` (profile formal-report). A local marketplace lists both. For the ten P1–P3 hand-built files, the build output is byte-identical to the hand files; formal-report's output style differs only by now being forced in its own plugin. `claude plugin validate --strict` passes for both plugins and the marketplace. `python3 -m build.checks` runs 06 §12 checks 1–4 with 0 failures; checks 2 and 3 compare within Claude Code until P6. The plugin installed from the local marketplace, fired a skill in a headless run, and uninstalled. `claude plugin eval` with ablation: all four skill triggers and both profiles' policy cases pass with the plugin and fail without it (6/6, mean delta 1). On a marked copy of the formal-report plugin, the forced style reached the main reply and its korean-reviewer carried the formal policy into the subagent. On the agent-reply plugin, `korean-editor` ran `ko-rewrite` and then `ko-grammar`. The Claude Code part of 06 §14.3 is met: installed, policy on main and subagent, `korean-reviewer` and `korean-editor` invoked, checks 2–4 pass.

| Artifact | Path |
|---|---|
| Profiles, presets, agents | `assemble/profiles/{agent-reply,formal-report}.yaml`, `assemble/presets.yaml`, `assemble/agents/{reviewer,writer,editor}.yaml` |
| Skill templates (4) | `assemble/skills/{ko-rewrite,ko-diagnose,ko-grammar,ko-route}/` — directives `@frag`, `@blocks`, `@quick-rules`, `@presets` |
| Install and removal doc | `assemble/install/claude-code.md` → `dist/claude-code/README.md` |
| Build | `build/claude_code.py`, `build/mini_yaml.py` (the assemble YAML subset; no PyYAML), `build/checks.py` |
| Output | `dist/claude-code/{agent-reply,formal-report}/` (plugin.json, skills ×4, output-styles ×1, agents ×3, provenance), `dist/claude-code/.claude-plugin/marketplace.json` |
| Evals | `tests/evals/claude-code/` (6 cases) |
| Run logs | `tests/runs/P5/` |

## Decisions settled here

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | structural | **Decision ② — build-time profile, one plugin per profile** / runtime profile in one plugin (formal-report unreachable, P3) / formal-report agent-only (flow D4 fallback) | Build-time, one plugin per profile; both listed in one local marketplace | medium-high | Both profiles reach the main thread with a forced style of their own (eval policy cases; formal channel run below). The only cost is that a user must enable one plugin, written into the install doc |
| 2 | major | **Agent–profile binding (06 §8)** follows ②: the same agent names rendered with each profile's policy / profile-suffixed agent names | Same names per plugin | high | Only one plugin is enabled at a time, so names never collide; check 3 compares the same agent across harnesses per profile |
| 3 | major | **`policy` as a preset step (06 §6)**: none (already injected) / re-inject the policy body at step time | None | medium | P3 runs showed no fading in the replies tested; re-injection would duplicate 6 KB per step. `presets.yaml` maps `policy: null`; ko-route says it is already active |
| 4 | major | **`claude plugin eval` scope**: one on/off case per skill trigger + one policy case per profile, runs 1 / 3 runs per case (default) | Minimum from flow, runs 1 | medium | 12 runs, $2.46; enough to show each channel fires and differs from baseline. Rerun with 3 runs in 7-review if variance matters |
| 5 | major | **Renderer input**: add layout (tag lines as fragments, blank-line counts) to normalized files / render whole-file skills from upstream sources directly | Layout in normalized | high | AGENTS.md: `normalized/` is the only upstream content downstream reads. Extractor output changed by +1134 lines (only `blanks:` and 24 tag fragments; 0 other changes); check still 0 failures |
| 6 | minor | Templates in `assemble/skills/<skill>/` with line directives / Python layout code per skill | Templates | medium | Ours text stays visible as text; ko-rewrite's template was generated from the P1 sidecar and reproduces P1 byte for byte |
| 7 | minor | Install test in the real `~/.claude` with local scope and cleanup / throwaway `CLAUDE_CONFIG_DIR` | Real config, cleaned up | medium | A throwaway config dir has no login (Keychain entry is keyed to it); cleanup verified against a snapshot |
| 8 | minor | Keep one kept upstream sentence naming the `Read` tool in ko-grammar step 1 / `selected` it out | Keep | medium | Harmless in both harnesses (both read files); no sentence change |

## Build vs hand

| Hand file (P1–P3, `dist/claude-code/`) | Built file (`dist/claude-code/agent-reply/`) | Result |
|---|---|---|
| `skills/ko-rewrite/SKILL.md`, `references/taxonomy-rewrite.md` | same paths | identical |
| `skills/ko-diagnose/SKILL.md`, `references/{scoring-and-report,taxonomy-diagnose,lread-rubric,katfishnet-research,xdac-research}.md` | same paths | identical |
| `output-styles/agent-reply.md`, `agents/korean-reviewer.md` | same paths | identical |
| `output-styles/formal-report.md` | `dist/claude-code/formal-report/output-styles/formal-report.md` | description line shortened and `force-for-plugin: true` added (decision 1); body identical |
| `SKILL.provenance.yaml`, `provenance/policy.yaml`, `.claude-plugin/plugin.json` | rebuilt | Source names point at the templates; tag lines are now `upstream` spans (they were `ours` in P2); plugin version 0.1.0 with author. All sidecars recompute (checks 1) |

New in P5: `ko-grammar` (SKILL.md 97 lines, body 91; guidelines, rules, common-errors in `references/`), `ko-route` (ours only), `korean-writer`, `korean-editor`.

## Checks

| Check | Result |
|---|---|
| 06 §12 check 1 | `check: 11 files, 1012 fragments, 0 failures`; all 10 sidecars recompute |
| Check 2 | Within Claude Code: every agent of each profile starts with that profile's output-style body. Across harnesses: P6 |
| Check 3 | Within Claude Code only (one harness); across harnesses: P6 |
| Check 4 | `skills/` byte-identical between the two profile plugins |
| `claude plugin validate --strict` | passed ×3 (two plugins, marketplace) after adding author and marketplace description |
| Install | local marketplace add → `install --scope local` → headless run fired `ko-quality:ko-rewrite` without `--plugin-dir` → uninstall → marketplace remove (`tests/runs/P5/install-test.txt`) |
| `claude plugin eval` | 6/6 with plugin, 0/6 without (`tests/runs/P5/plugin-eval.json`) |

## Channel runs (`tests/runs/P5/channel.json`, $1.08)

| Case | Plugin | Markers (formal style / formal reviewer) | Calls | Observed |
|---|---|---|---|---|
| formal-main | copy of formal-report | 2 / 0 | one denied `Bash` (looking for the draft file) | Forced formal-report style applied: marker present; reply addresses 사용자님 in 하십시오체 |
| formal-subagent | copy of formal-report | 2 / 5 | `Agent: ko-quality-formal:korean-reviewer` → `Skill: ko-quality-formal:ko-diagnose` → its references | Formal policy in the subagent ("사용자님께서 요청하신 대로 원문은 수정하지 않았습니다") |
| editor-agent-reply | agent-reply | — | `Agent: ko-quality:korean-editor` → `Skill: ko-rewrite` → `taxonomy-rewrite.md` → `Skill: ko-grammar` → `guidelines.md` | Preset `edit` order held; grammar fixed 금새→금세, 될꺼라고→될 거라고 after rewrite |

## Spec did not know

- **Removal leaves two traces** (2.1.270): an empty `"extraKnownMarketplaces": {}` in `~/.claude/settings.json`, and the plugin copy under `~/.claude/plugins/cache/<marketplace>/`, marked `.orphaned_at` for Claude Code's own later sweep. Both were cleaned by hand after the test and are documented in the install README.
- **`claude plugin eval` treats `tool_used: Skill` as a with-only indicator** under ablation; the baseline arm cannot fire a plugin skill, so trigger cases always show delta 1. The informative comparisons are the two policy cases.
- **`claude plugin validate --strict`** warns on a missing plugin author and a missing marketplace description; the runtime tolerates both.
- **`CLAUDE_CONFIG_DIR` also keys the macOS Keychain credential** (docs), so it cannot isolate a headless test that needs the user's login.
- System Python is 3.9 (no `tomllib`); P6's TOML output uses `build/mini_toml.py`.

## Differs from spec

- `dist/claude-code/` now holds one plugin per profile plus a marketplace, not a single plugin (06 §12 table). Proposed for 7-review with decision ②.
- The Claude Code plugin ships no MCP server yet (`.mcp.json` in 06 §12): P7 decides whether a tool-less server is shipped at all.
- No build stamp yet (06 §12): P7 settles its format.

## Subagent runs

Exploration cap: 1 of 4 used.

| # | Tier | Purpose | Tokens | Result |
|---|---|---|---|---|
| 1 | claude-code-guide (docs lookup) | `claude plugin eval` case format, local marketplace, `CLAUDE_CONFIG_DIR` isolation, forced styles, plugin agent fields | 86.3k | Case/grader format and marketplace format confirmed; `CLAUDE_CONFIG_DIR` also keys the Keychain credential, so a throwaway config dir has no login; two forced styles: first loaded wins |
| V | mid (Sonnet 5) | Verification of the done-condition (outside the cap) | 111.3k | All four clauses **met**. Reproduced `korean-reviewer` → `ko-diagnose` on the unmodified agent-reply plugin; re-diffed hand vs build (every difference explained); confirmed checks 2–3 "within Claude Code only" is honest scope before P6. Caveat: the marketplace install/uninstall cycle ran for `ko-quality` only; `ko-quality-formal` rests on `validate --strict` and `--plugin-dir` runs |

## Build process note

One step (saving this log and editing this record) used an unquoted shell heredoc; the shell ran the backticked names in the text as commands, and the step hung until it was stopped. Nothing was written. The step was redone from a script file. A shell left over from P4's schema-writing step (hung the same way after its files were written) was stopped at the same time.

## Release-blocked

None. Every done-condition clause was verified met. Open for 7-review, not blocking: install `ko-quality-formal` through the marketplace once (only `ko-quality` went through the full install cycle).
