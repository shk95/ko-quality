# Q2: check 7, check 6 boundary, hooks enabled

Spec §2.5. Builder's own evidence only.

## Built

- `build/checks.py`: check 7 scans the tip tree and every commit reachable from `HEAD` with `hostguard.scan`; check 6's boundary includes `hostguard/`.
- This clone: `git config core.hooksPath hostguard/hooks` (preflight F3).

## Ran

- `python3 -m build.checks`: 0 failures after the fix below; check 6 covers 29 files, 0 third-party imports; check 7 reports 0 hits.
- The hooks were exercised in a temporary repository by Q1's tests. In this clone they ran on the amended Q1 commit, on this commit, and on its push.

## Spec did not know

- **Check 7 caught the builder on its first run.** The Q1 record, committed before the hooks were enabled, quoted a plan-vocabulary word while explaining a false positive. The commit was local, so it was amended with the line reworded. This is the failure mode exploration §2 measured: a writer who knows the rule still writes the word.
