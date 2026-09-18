# Q5: documents

Spec §1, §5. Builder's own evidence only.

## Built

- `AGENTS.md`: "Public repository" replaced by the rule (the test, the table of host state and allowed values, ways of writing, enforcement, the local root, the two process points); `hostguard/` in the layout table; raw run logs now "in the local root".
- Root `README.md`: per-machine steps 4 (hooks) and 5 (local root); a note that nothing local is deleted automatically.
- `corpus/README.md`: corpus homes and work directories under the local root; committed files come only from `--report` and `summary`.
- `09_toolkit_spec.md`: forward pointers at §12.1, §13 and §18. Nothing else in 09 changed.

## Ran

- `hostguard scan` on the four documents: one hit, the rule table's own row naming the banned category; exempted in `allow.tsv` with that reason.
- `python3 -m build.checks`: 0 failures (check 7: 0 hits). `tests/hostguard_test.py`, `tests/logger_test.py`: 0 failures.

## Differs from spec

- None.
