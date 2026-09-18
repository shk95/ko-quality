# 04. Plan

> Stage document, era 98. Builds [`../3-spec/03_spec.md`](../3-spec/03_spec.md). Verification of every step is deferred to `7-review` (user, 2026-09-18).

| Step | Builds | Spec | Done when |
|---|---|---|---|
| Q1 | `hostguard/` rules, scan, redact, CLI, tests; `allow.tsv`, `conditions.txt` | §2.1, §2.2, §2.5 | tests pass; a scan of the current history lists only false positives, each exempted with a reason (done 1, 2) |
| Q2 | Check 7 in `build/checks.py`; check 6 boundary includes `hostguard/`; hooks | §2.5 | `build/checks.py` passes; the three hooks refuse planted values (done 3, 6) |
| Q3 | Local root: `deny.local`, `status`, `clean`, `notice`, `mark-reviewed`; SessionStart hook in `.claude/settings.json`; move this host's existing local data into the root | §2.3, §2.4 | done 4. The move is recorded in `LOCAL-NOTES.md` only |
| Q4 | `corpus summary`, canary report through `redact`; `measure/prices.json`, `measure/cost.py` | §3 | done 5 |
| Q5 | `AGENTS.md`, root `README.md`, `corpus/README.md`, forward pointers in 09 | §1, §5 | the documents say what §1 and §5 say |

Each step ends with a commit and a record in `6-build/`. Order: Q1 and Q2 first, so every later commit is scanned.
