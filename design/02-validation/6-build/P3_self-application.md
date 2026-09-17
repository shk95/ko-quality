# P3 — Self-application

## Summary

This repository now runs ko-quality on itself (09 §21). The committed `.claude/settings.json` sets `KO_QUALITY_HOME: "~/.ko-quality-dev"`, enables `ko-quality@ko-quality` and selects `ko-quality:agent-reply`. The Korean `README.md` carries the per-machine steps. On this machine the local marketplace is registered, and the plugin loads straight from `dist/claude-code/ko-quality`. Sessions at the root write to `~/.ko-quality-dev` with `project` and `build_id`; `~/.ko-quality` never appeared.
Done-condition: **met on all three clauses** (independent `mid` verification). Release-blocked: **0**.

## Built

| Item | Path | State |
|---|---|---|
| Committed settings: home, plugin, style | `.claude/settings.json` | done |
| Per-machine steps and caveats (Korean) | `README.md`, section "이 저장소에서 개발할 때: 자기 적용" | done |
| Local `outputStyle` absent on this machine | `.claude/settings.local.json` (untracked) | confirmed absent before P3 (F12, removed by the user) |
| Marketplace `ko-quality` → `dist/claude-code` in user settings | this machine only | done |
| Run summary | `tests/runs/02-P3/self-application.json` | done |

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | minor | Canary for clause 3: register a marked copy of `dist/claude-code` as the marketplace, then swap in the real one / `--plugin-dir` a marked copy | The marked marketplace. The clause is about the committed-settings path, and `--plugin-dir` would bypass `enabledPlugins` | high | F3; X1 |
| 2 | minor | Clause 2's plugin in a subdirectory: a user-scope install writing to `~/.ko-quality` / `--plugin-dir` with `KO_QUALITY_HOME` at a scratch home in the shell | The scratch home. The check "`~/.ko-quality` gains no file" rules out the real leak path. `project` does not depend on the home | medium-high | flow.md §3 P3 checks |
| 3 | minor | After finding that `marketplace remove` strips `enabledPlugins` from the committed file: restore the file and document it / avoid the command | Restore and document in the README | high | runs `root-real`, `root-canary2`, `root-canary3`, `root-real3` |

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V3 | mid (Sonnet 5) | Verification of the P3 done-condition (outside the cap), isolated worktree at `cb924eb` | 104,190 | All three clauses and the home-listing check **met**; noted that no "after" listing had been saved |

Exploration runs: 0 of 4.

## Cost

| Run | Model | USD |
|---|---|---|
| Eight headless sessions (root, design/, swaps and retries; see the summary) | claude-sonnet-5 | 0.36 |
| **Total** | | **0.36** (no ceiling set for P3) |

## Differs from spec

- **The marketplace step alone is enough on a fresh machine, with no `claude plugin install`.** 09 §21.2 lists only the marketplace step, and that held. The plugin loads from the marketplace directory in place: nothing is added to `installed_plugins.json` and nothing is copied into the cache.
- **Clause 2 was shown with a stand-in** (decision 2). No real user-scope install wrote to the default home.

## Spec did not know

- **`claude plugin marketplace remove ko-quality` rewrites the committed project settings.** Run at the repository root, it removed `ko-quality@ko-quality` from `.claude/settings.json` `enabledPlugins`. Later sessions still echoed `outputStyle: ko-quality:agent-reply` in `init` but loaded no plugin and wrote no record. That failure was silent and safe: no policy and no record, not records in the wrong home. The README now says to `git checkout .claude/settings.json` after re-registering. The same command in P1's scratch project left `enabledPlugins: {}` in `settings.local.json`, which is the same behaviour.
- **In-place loading means a rebuild applies to the next session.** The dev plugin always matches `dist/`, and `build_id` in records tells builds apart (09 §21.1).
- **`init.output_style` is a settings echo, not proof that the style applied.** It named `ko-quality:agent-reply` in sessions where the plugin had not loaded. This matches review §D's reason for canaries.
- **The build session itself is unaffected, as F12 expected.** `~/.ko-quality-dev/logs` still holds only the three records from this step's sessions.

## Verification

Run V3, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned (the user's home directory is written `~`):

> Verified at commit `cb924eb` (detached, in an isolated worktree). Checked out cleanly, working tree clean throughout — no changes made anywhere.
>
> **Done-condition clauses (10_plan.md §4 P3)**
>
> **1. "A session launched at the repository root writes records to ~/.ko-quality-dev carrying `project` and `build_id`, and none to ~/.ko-quality."**
> verdict: **met**
> evidence: `~/.ko-quality-dev/logs/2026-09.jsonl` currently holds exactly 3 records, all with `"project": "<project hash>"` and `"build_id": "51112680979b60c3"`, `"plugin_present": true`, `"harness_position": "main-to-user"`, `"policy_on": null`. Their `session_id`s (`<session>`, `<session>`, `<session>`) match exactly the init events of the raw stream logs for sessions `root`, `root-canary3`, `root-real3` in the scratchpad. I independently recomputed `hashlib.sha256("<repository>".encode())[:16]` → `<project hash>`, matching. I independently read `dist/claude-code/ko-quality/ko-quality.stamp.json` → `"build_id": "51112680979b60c3"`, matching the committed dist artifact, not just the claim in `tests/runs/02-P3/self-application.json`. `ls ~/.ko-quality` → "No such file or directory" (checked live). `snap/homes-before.txt` (scratchpad) shows the same absence before the step: `"~/.ko-quality": No such file or directory (os error 2)`.
> how it could still be wrong: the 3 records are all from headless `claude -p` reproduction runs the tester built specifically for this check (using a canary-marked or restored plugin copy), not an ordinary interactive session. Nothing here rules out a different code path (e.g. `--resume`, an interactive session started before the harness re-reads `env`) still reaching `~/.ko-quality`. Sessions `root-real`/`root-real2`/`root-canary2` also ran at the root and *echoed* `outputStyle: ko-quality:agent-reply` in `init`, but `enabledPlugins` had been stripped by an unrelated `marketplace remove` bug, so no plugin loaded and no record was written at all — a near-miss that happened to fail safe (writes nothing) rather than fail into the wrong home; a different bug shape might not.
>
> **2. "A session launched in a subdirectory is identifiable from its record's `project` (§21.1)."**
> verdict: **met**
> evidence: session `sub-plugin` (stream log `sub-plugin.jsonl`) has `init.cwd = "<repository>/design"` and `init.output_style = "default"` (confirming committed project settings were *not* read from that directory, per spec §2.1). It loaded the plugin via `--plugin-dir` (simulating a user-scope install) with `KO_QUALITY_HOME` pointed at a scratch home. The resulting record in `sub-home/logs/2026-09.jsonl` — `session_id: <session>` (matches `sub-plugin.jsonl`'s init) — carries `"project": "<project hash>"`, identical to the repository's hash. Plain session `sub-plain` (no `--plugin-dir`) loaded no plugin and produced no record at all, matching §21.1's "gets no isolation and no plugin."
> how it could still be wrong: this exercises identifiability by *proxy* — `--plugin-dir` plus a scratch `KO_QUALITY_HOME`, not a real user-scope marketplace install writing to the real default `~/.ko-quality`. That real leak path was deliberately not exercised, precisely so the "`~/.ko-quality` gains no file" check would hold. `project` is computed purely from `git_root(cwd)` (logger/ko_quality_log.py:82-86), so it is close to tautologically correct for any cwd inside the repo — the test confirms the mechanism but not the untested real-leak trigger it exists to catch.
>
> **3. "The main thread's reply shows the agent-reply policy (canary)."**
> verdict: **met**
> evidence: `canary-market/ko-quality/output-styles/agent-reply.md` (scratchpad) has the line `Begin every reply with the line KQ-CANARY-P3-style-agent-reply-1` appended after the body's `## 추가 사항` section (outside the policy text, per F3). Assistant replies in `root.jsonl` and `root-canary3.jsonl` (both with `ko-quality` plugin present per `init.plugins`) begin literally with `KQ-CANARY-P3-style-agent-reply-1`, e.g. root.jsonl: `"text": "KQ-CANARY-P3-style-agent-reply-1\n\n\`gate\` 디렉터리는 게이트 실행 파일을 위해 예약된 자리이며..."`.
> how it could still be wrong: the canary was only fired against the canary-marked copy. The real (unmarked) plugin's load was confirmed separately (`root-real3.jsonl`: `init.plugins` shows `ko-quality` loaded from `<repository>/dist/claude-code/ko-quality`) but that reply carries no marker by design, so clause 3's affirmative evidence rests entirely on the canary copy, not on the shipped `agent-reply.md` body itself — consistent with F3's own stated limitation ("adding a line changes the thing tested... the unmodified plugin is what the corpus runs; the canary proves routing only").
>
> **Checks (flow.md §3 P3)**
>
> **`10_plan.md` P3.1–P3.3**: same three clauses above — met, same evidence.
>
> **"`~/.ko-quality` gains no file during the step (listing before and after)"**
> verdict: **met**, with a gap in the audit trail
> evidence: `snap/homes-before.txt` (scratchpad, timestamped 17 Sep 17:53, same minute as the first root session) shows `~/.ko-quality` absent before. `ls ~/.ko-quality` now (this verification) still shows absent. `self-application.json`'s own field: `"default_home_after": "~/.ko-quality absent before and after the step"`.
> how it could still be wrong: no `homes-after.txt` (or equivalent) file exists in the scratchpad alongside `homes-before.txt` — only a "before" snapshot was preserved as a raw artifact. The "after" state I confirmed was checked live, after the fact, in a separate session, not captured by the build session itself immediately following its last reproduction run. A transient creation-and-cleanup of `~/.ko-quality` between the build's last write and my check would not be caught by either snapshot.
>
> **Anything contradicting spec 09 / 10_plan.md / flow.md**
>
> None found. Specific things checked and found consistent, not contradictory:
> - Committed `.claude/settings.json` has exactly `env.KO_QUALITY_HOME`, `enabledPlugins`, `outputStyle` — no marketplace entry, matching F13/L4 (github marketplace source stays untested/not adopted, per-machine `marketplace add` step stays and is present in README.md).
> - Main checkout's `.claude/settings.local.json` (untracked, read only) has no `outputStyle` key — matches F12 (user removed it, consent U3 recorded as "Answered: yes" in flow.md §4).
> - `outputStyle: "ko-quality:agent-reply"` matches the required `<plugin.json name>:<style>` form (§2.1); plugin/marketplace name `ko-quality` confirmed from `dist/claude-code/.claude-plugin/marketplace.json` and the stamp file.
> - The "`marketplace remove` strips committed `enabledPlugins`" finding (from debugging `root-real`/`root-real2`/`root-canary2`) is already folded into README.md's "알아둘 것" section as a documented caveat, not left as a silent contradiction.
> - All records in `~/.ko-quality-dev/logs/2026-09.jsonl` correspond to known session_ids from the provided stream logs; no unexplained extra records.
>
> One process note, not a content contradiction: `design/02-validation/6-build/README.md`'s progress table still shows P3 as all `—` (no record, no verdict, no cost), and there is only one commit for P3 (`cb924eb`, the "step" commit) versus the two-commit pattern (step + "record... verified, N release-blocked") used for P1 and P2. This is expected under flow.md §2: the independent `mid` verification (this report) is meant to be pasted into the P3 record verbatim, and that record apparently has not been written yet as of `cb924eb` — not a deviation from process, just work still pending on the builder's side.

**Builder's note on the audit gap:** an "after" listing was saved after verification (2026-09-17T09:05Z): `~/.ko-quality` absent, and `~/.ko-quality-dev/logs/2026-09.jsonl` last modified at the step's final session. It closes the gap only from that time on, not for the interval the verifier names.

## Release-blocked

None.
