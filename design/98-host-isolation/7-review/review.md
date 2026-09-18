# 7-review (era 98)

> Review of [`../6-build/README.md`](../6-build/README.md) against [`../3-spec/03_spec.md`](../3-spec/03_spec.md) §6. The build ran without verification (user, 2026-09-18); this review is where everything was verified. Branch `review/98-host-isolation`, merged back to `dev`.

## A. Verification

| Run | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V | mid (Sonnet 5) | Independent check of done conditions 1–6, a bypass hunt, and `AGENTS.md` coherence; given the spec, the exploration and the code, not the build records | 198,347 | 1 met with a caveat, 2 partly met, 3 met with two bypasses found, 4–6 met; `AGENTS.md` coherent |

| # | Done condition | Verification found | After the review |
|---|---|---|---|
| 1 | Check 7 passes; every exemption has a reason | Met. All 13 allowlisted lines only name a rule or a category; none hides a value. Caveat: "0 hits" could not see merge commits (below) | Met |
| 2 | A catch and a false positive per rule; no host value in fixtures | Partly. Three literal rules (`host:hostname`, `host:user-in-path`, `host:project-slug`) had no test; three more had no false-positive case. Fixtures carry no host value | Met: all added |
| 3 | The three hooks refuse planted values | Met, reproduced. **Bypass 1 (high):** `git diff-tree` without `-m` shows nothing for a merge commit, so a value introduced only by a merge resolution passed check 7 and `pre-push`; reproduced end to end. **Bypass 2 (medium):** scanning is per line, so a path wrapped over a line break passed every rule. Tag pushes and renames did not bypass | Fixed: merges are diffed against each parent (`-m`); a `pre-merge-commit` hook covers merges without conflicts, which never run `pre-commit` (found while fixing); substring rules also run on the text with line breaks removed. Tests reproduce both bypasses and fail without the fix (checked by removing `-m`) |
| 4 | `status`, `clean`, `notice`, `mark-reviewed` | Met, over a temporary root | Met |
| 5 | `corpus summary`, `api_equivalent` | Met; the summary is also redacted, which the condition did not ask | Met |
| 6 | `build/checks.py`, check 6 covers `hostguard/` | Met | Met: 0 failures, check 7 0 hits, after the fixes |

## B. The two items the build left unmeasured

Record: [`tests/runs/98-review/unmeasured-items.json`](../../../tests/runs/98-review/unmeasured-items.json).

- **Does the model pass the cleanup notice on?** In 1 of 2 ordinary sessions. The hook fires every time; the model channel alone is not reliable. Whether the interactive UI shows `systemMessage` is still unmeasured: the owner sees it, or does not, at the next session start. Handed to era 03.
- **The changed `corpus canary`:** works as specified. The full report stays in the work directory with its session id; the report and stdout carry `<local>` and pass the scan.

## C. Differences from the spec, accepted

Found by V; each reduces false positives in the direction exploration §2 measured, and none was shown to hide a value.

- A path token that begins with the scratch segment itself, or with the Unicode ellipsis, is a placeholder.
- `host:user-in-path` needs a user name of 3+ characters; `host:hostname` skips `localhost`.
- `claude-plugins-official` is treated like this project's own marketplace: it is the same for every Claude Code user.
- `host:model-setting` skips plain lowercase aliases and names under 4 characters.
- `deny.local` carries two rule names the spec does not list (`host:clone-name`, `host:local-dir`).

## D. Limits, accepted and named

- Binary files and `upstream/` are not scanned (spec §2.1).
- Deliberate obfuscation (zero-width characters, homoglyphs, encodings) defeats literal matching. The threat is an accidental leak, not an adversary.
- The plain-word heuristic for plugin and model names is coarse.
- `status` and `clean` depend on the process points in `AGENTS.md` and the notice; nothing forces them.

## E. Incidents during the review

- **The verification subagent deleted outside its scope.** Cleaning its own temporary directories, it removed about 330 empty directories under the system temporary folder, beyond the ones it made. It reported this itself. The repository, the local root and this session's working files were checked afterwards and are intact. The prompt limited it to directories it created; the next verification prompt should also forbid glob deletion.
- **The builder lost uncommitted work for a moment.** Restoring a file after the check-the-test-fails experiment with `git checkout` also discarded the uncommitted fix in that file; it was restored from a copy taken just before. The lesson is ordinary: commit, or copy, before an experiment that reverts.

## F. Decisions

| # | Decision | Why |
|---|---|---|
| R1 | Era 98 is closed. Its work is in `dev` | All six done conditions met after the review's fixes; no release-blocked mark |
| R2 | **`master` does not move now.** Era 98 reaches `master` together with era 02, after era 02's review | `dev` also holds era 02's unreviewed build and its release-blocked P9 mark; `master` takes only reviewed, stable changes (user, 2026-09-18). Cheapest to reverse |
| R3 | Era 02 resumes at `7-review`, reviewing the build at tag `era02-6build-end`, under `AGENTS.md`'s new public-repository rule | The pause condition (era 98 in `dev`) is met |
| R4 | The process points run now: `mark-reviewed 98-host-isolation`, then `status`, and the owner chooses what to delete | `AGENTS.md` "Public repository" |

## G. Handed to era 03

- **`project`:** if era 03 pools records from more than one machine, revisit it; a committed random id is the candidate (P-5).
- **Stale `state/` files in a product user's `~/.ko-quality`:** the shipped logger never sweeps them. A product decision.
- **The cleanup notice:** the model relays it about half the time; whether the UI shows `systemMessage` is unmeasured. If it does not, the notice needs another channel.
- **The first corpus batch** uses `corpus summary` and the redacted canary report, and runs under check 7 and the hooks.
