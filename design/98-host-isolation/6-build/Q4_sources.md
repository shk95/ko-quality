# Q4: sources — corpus summary, redacted canary report, price table

Spec §3. Builder's own evidence only.

## Built

- `python3 -m corpus summary --progress <file> --out <path>`: every progress row without `session_id`, passed through `redact`.
- `python3 -m corpus canary`: the full report goes to `<work>/<batch>.canary[-mislabel].json` (local); `--report` and stdout get a copy with `session_id` set to `<local>` and passed through `redact`.
- `measure/prices.json`: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`, read from the official OpenAI pricing page on 2026-09-18. `gpt-5.6` is not on the page and has no entry.
- `measure/cost.py` `api_equivalent(model, input, cached_input, output)`, and `tests/cost_test.py`.

## Ran

- `corpus summary` on era 02's real batch progress file (in the local root): 1,458 rows, no `session_id`; the output passes `hostguard scan`.
- `python3 tests/cost_test.py`: 0 failures. At the official price, era 02's P2 Codex run (83,703 input, 318 output tokens) is $0.171. The P2 record is not changed.
- **Not run:** `corpus canary` (it starts paid headless sessions). Its new lines only move the full report to the work directory and redact the printed copy; the first batch of era 03 exercises it.

## Spec did not know

- **The official price differs from third-party pages.** Exploration §4 quoted third-party pages; the official page gives `gpt-5.6-sol` input at $4.00, not $5.00. The official page is the source (preflight F5).
- `gpt-5.5`'s official price is for short context (under 272K input tokens); the entry says so.
