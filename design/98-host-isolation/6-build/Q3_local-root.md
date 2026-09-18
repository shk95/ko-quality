# Q3: local root, deletion candidates, SessionStart notice

Spec §2.3, §2.4. Builder's own evidence only.

## Built

- `hostguard/local.py` (in Q1's commit): `deny.local`, candidates, `status`, `clean`, `mark-reviewed`, `notice`.
- `.claude/settings.json`: a SessionStart hook running `python3 -m hostguard notice` from `$CLAUDE_PROJECT_DIR`.
- This host's local data moved into the local root (preflight F4: moved, nothing deleted). What moved from where is in the root's `LOCAL-NOTES.md` only; the earlier build's local note is kept unchanged inside the moved build material and copied into the root note.
- `deny.local` received the host values the configuration no longer holds (the ones the second rewrite removed), so scans keep refusing them. The public branches hold none of them (checked before adding).

## Ran

- `python3 -m hostguard status`: era 02's build material pending (its review has not closed); the rewrite mirror and five local backup refs ready.
- A headless session at the repository root (Claude Code, `claude-haiku-4-5-20251001`, $0.031): the hook ran, exit 0, and printed both channels with the count of ready candidates. The prompt asked for a one-word reply, and the model did not add the notice; the instruction asks for "a natural point", so this is not a failure, but whether the model mentions it in an ordinary session is unmeasured.

## Differs from spec

- `deny.local` also holds two rules the spec does not name, `host:clone-name` and `host:local-dir`, for past values that are neither plugins nor models. They match on word boundaries like any unknown rule.

## Spec did not know

- **Corpus homes named in committed era 02 records** are the old ad hoc home directories. They are records of that time and stay (the user does not want pushed content rewritten again); new batches use the local root. Their names are not added to `deny.local`, because they are in the pushed history and check 7 would fail on them.
- Deleting a backup ref with `clean` removes the ref; its objects stay in the clone until git's garbage collection.
