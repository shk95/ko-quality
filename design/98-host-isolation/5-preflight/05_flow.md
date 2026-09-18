# 05. Preflight

> Stage document, era 98. Flow of the build for [`../4-plan/04_plan.md`](../4-plan/04_plan.md).

## Decided before the build

| # | Decision | Answer |
|---|---|---|
| F1 | Verification | None during the build; all of it in `7-review` (user, 2026-09-18). Each step records what it ran itself, marked as the builder's own evidence |
| F2 | Test fixtures carrying host values | Built at run time from the host (`Path.home()`, `getpass`), never written into a committed file |
| F3 | Pushing | Each step's commit is pushed to `origin/dev` after its own checks pass; the hooks are enabled in this clone in Q2 |
| F4 | Moving this host's local data (Q3) | Move, never delete. Old locations are recorded in `LOCAL-NOTES.md`; nothing about them is committed |
| F5 | Price table | Only values read from the official pricing page. If the page cannot be read, the table ships empty for that provider and the step is marked **release-blocked** |
| F6 | Existing backup refs in this clone | Listed by `status`; not deleted by the build |

## Release-blocked if

- Check 7 cannot pass on the current history without exempting a real host value.
- A hook cannot refuse a planted value.
