# Q1: hostguard rules, scan, redact, CLI, tests

Spec §2.1, §2.2, §2.5. Builder's own evidence only (no verification run in this build).

## Built

`hostguard/` (`rules.py`, `scan.py`, `local.py`, `redact.py`, `__main__.py`, `hooks/`, `allow.tsv`, `conditions.txt`) and `tests/hostguard_test.py`. Standard library only.

## Ran

- `python3 tests/hostguard_test.py`: 0 failures. Covers every literal and fixed rule with one catch and one false positive from exploration §2, the allowlist, `redact`, the local root, and the three hooks in a temporary repository (a planted home path refused by `pre-commit`, a planted session id by `commit-msg`, a commit made past the local hooks refused by `pre-push`, nothing reaching the remote).
- `python3 -m hostguard scan --history HEAD` on this repository: 11 lines hit, all in era 98's own documents and records that name the rules or the removed categories. Each is in `allow.tsv` with that reason. After that, 0 hits.

## Differs from spec

- **Relative scratch mentions.** A path token that starts with the scratch segment itself (no prefix) is treated as a placeholder, like `...` and `<`. It carries no host prefix; one committed record uses that form. Spec §2.1 names only `...` and `<`.
- **Rule sources avoid matching themselves.** Fixed patterns are written with a bracketed character (`fold[e]rs`), and the test file joins example strings at run time, so neither needs an allowlist entry.
- **CLI scans the repository it runs in** (`git rev-parse --show-toplevel`), so the hooks guard whichever clone they are enabled in.

## Spec did not know

- The prototype's `plus Tier` false positive disappears with case-sensitive vocabulary, and word boundaries keep the plan vocabulary from matching inside `quotation`.
- `notice` cannot be tested silent in this clone while rewrite backup refs exist: they are ready candidates. The test asserts silence only when no ready candidate exists.
