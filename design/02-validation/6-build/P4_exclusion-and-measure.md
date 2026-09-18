# P4 — Exclusion pass and `measure/`

## Summary

`measure/` now exists as an offline runner. It enforces retention first, reads `logs/`, joins `annotations/` on `session_id` (and `turn_key` when an annotation names one), applies exclusion pass `ex-1`, and writes timestamp-free `derived/` records with `instruction_lang`, `artifact_lang` and `usable`. A labelled zone set of 11 synthetic replies is committed under `tests/exclusion-cases/`, and the false-negative count is reported for every zone. Proper nouns are reported as Tier 1, pending P6.
Done-condition: **met on all three clauses** (independent `mid` verification). Release-blocked: **0**. The verifier found four defects that do not break a clause; P5 carries the fixes (see Verification, builder's notes).

## Built

| Item | Path | State |
|---|---|---|
| Runner, CLI, derived fields | `measure/runner.py`, `measure/__main__.py`, `measure/derived_fields.py` | done |
| Exclusion pass `ex-1` (nine zone rows) | `measure/exclusion.py` | done |
| Zone evaluation | `measure/exclusion_cases.py` | done |
| Retention (09 §20) | `measure/retention.py` | done |
| Measurement registry (empty until P5) | `measure/measurements/__init__.py` | done |
| README (Korean), pinned `requirements.txt` (empty until P6), `measure/.venv/` ignored | `measure/` | done |
| Labelled zone set (F5) | `tests/exclusion-cases/x01…x11.json` | done |
| Retention and re-run test | `tests/measure_runner_test.py` | done, 0 failures |
| Reports | `tests/runs/02-P4/exclusion-cases-ex-1.json`, `tests/runs/02-P4/runner-test.txt` | done |

### False negatives per zone, `ex-1`

| Zone (09 §15.2 row) | Tier | Positives | False negatives | Excluded under another zone | Near-miss negatives | False positives |
|---|---|---|---|---|---|---|
| code | 0 | 9 | 1 | 0 | 4 | 2 |
| url_path_id | 0 | 12 | 0 | 0 | 4 | 0 |
| quotation | 0 | 8 | 0 | 1 | 4 | 0 |
| number | 0 | 14 | 0 | 1 | 4 | 0 |
| structure | 0 | 11 | 0 | 0 | 5 | 0 |
| math | 0 | 7 | 0 | 0 | 5 | 0 |
| legal | 0 | 6 | 0 | 0 | 5 | 0 |
| abbreviation | 0 | 9 | 0 | 0 | 4 | 0 |
| proper_noun | 1 (pending P6) | 9 | 4 | 2 | 3 | 0 |

**How much to trust this table.** The builder wrote cases x01–x10 after the first version of the pass and then fixed the pass against them. The fixes were real bugs: `\b` treated Hangul as a word character, so `320ms에서` did not match, and `NUMBER` ran before `ABBREV` and split `S3`. The counts on x01–x10 are therefore optimistic. x11 was written before it was run and was not tuned against. Its code false negative and two code false positives (a lone backtick pairs with the next one) are left as found. P8 measures the pass again on generated replies.

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | Case format for zone labels: JSON with substring spans / YAML via `build/mini_yaml.py` | JSON. Labels are lists of maps, which the stdlib YAML subset cannot read, and §17.3's format does not fit zone labels (10_plan.md verification #5) | high | 10_plan.md P4 |
| 2 | major | False-negative definition: not excluded under its own zone / not excluded at all | Both are reported: `false_negatives` (not excluded at all, or not labelled for structure) and `other_zone` (excluded under a different zone). The verifier showed that `other_zone` can hide a real miss behind an unrelated false positive (V4, note 3) | medium | exclusion_cases.py |
| 3 | minor | Proper nouns in Tier 0: Latin capitalised tokens now, NNP in P6 / nothing until P6 | Latin tokens now, reported as Tier 1 pending | medium-high | flow.md §3 P4 checks |
| 4 | minor | Attributed quotation markers | A speech verb must follow 라고/고 (`X라고 부르다` names; it does not quote), plus 라며, 라는 말, and upstream's `따르면`. Tightened before commit, after a P5 draft case exposed `'혁신'이라고 부르기`; the labelled set's counts did not change | medium | upstream Do-NOT line |
| 5 | minor | Text-copy directories for retention | `logs/`, `judge/`, `grader/`, `exports/`, so that every copy of §20's text is covered. `derived/` and `annotations/` are never touched | medium-high | 09 §20 |
| 6 | minor | Derived file layout on re-run | Rewrite each month's file: derived records whose log has expired are kept first, then fresh records in log order. `sort_keys`, no timestamp | high | runner test |
| 7 | minor | `instruction_lang` with no letters at all | `mixed`, as era 01's logger did (09 names only `ko \| en \| mixed`) | medium | 09 §12.3 |

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V4 | mid (Sonnet 5) | Verification of the P4 done-condition (outside the cap), isolated worktree at `a6cd821` | 114,190 | All three clauses **met**; four findings: `code_version` provenance, honorific speech marker, `other_zone` masking, retention docstring |

Exploration runs: 0 of 4.

## Cost

No model calls. **$0.**

## Differs from spec

- **Zone cases are JSON, not §17.3 YAML** (decision 1). 10_plan.md already separated them from §17.3 cases.
- **Two extra report columns** (`other_zone`, false positives on near misses) beside the false-negative count that §15.2 asks for.

## Spec did not know

- **`\b` and `\w` in Python treat Hangul as word characters.** Every ASCII token that a particle attaches to directly (`max_retries를`, `H2SO4입니다`) needs `re.ASCII` boundaries. This was the largest single source of misses on the first pass.
- **Hashing `measure/**/*.py` for `code_version` also hashes the virtualenv.** `measure/.venv/` lives inside `measure/`, so the committed `runner-test.txt` carries `7def1cd15df13bb3` (with the venv's files) while a clean checkout computes `30fff4f9e9b504b2`. The results match; only the version string differs. P5 excludes `.venv`.
- **A lone backtick breaks inline-code pairing for the rest of the line** (x11). `INLINE_CODE` pairs it with the next backtick.

## Verification

Run V4, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned:

> Verified at commit a6cd821 (detached HEAD, worktree left clean, symlink to upstream/.cache removed after use).
>
> **Done-condition (10_plan.md §4 P4)**
>
> **1. False-negative count per zone, with exclusion_version — MET**
> Evidence: `python3 -m measure exclusion-cases` output (identical byte-for-byte to `tests/runs/02-P4/exclusion-cases-ex-1.json`) reports `"exclusion_version": "ex-1"` at top level and a `false_negatives` integer for all 9 zones in `measure/exclusion.py`'s `ZONES` tuple (code, url_path_id, quotation, number, structure, math, legal, abbreviation, proper_noun). `proper_noun` carries `"status": "Tier 1: NNP needs the analyser (P6). Only Latin capitalised tokens are found in Tier 0"` (`measure/exclusion_cases.py:16`), matching flow.md §3 P4's "proper-noun row is reported as Tier 1 and pending P6."
> How it could still be wrong: the reported counts are less trustworthy than they look. `exclusion_cases.py`'s `evaluate()` (lines 52–59) counts a missed positive as `other_zone` (not a false negative) whenever it falls inside *any* removed zone's span, even when that other zone's match is itself a false positive. I demonstrated this concretely: in `tests/exclusion-cases/x11-near-misses.json`, a stray backtick produces a huge false-positive `code` span (chars 6–98) that happens to swallow three unrelated positives — `3분기` (number), `박서연` (proper_noun), and `"확인했다"` (quotation) — all three are bucketed as `other_zone`, so they never count against `false_negatives`. Testing the `quotation` zone in isolation (stripping the stray backtick) shows a real, independent defect: `SPEECH_MARKER` in `measure/exclusion.py:44` matches `고 했습니다`/`라고 했다` but not the honorific `고 하셨습니다`/`고 하셨다` (verified directly against the regex — `SPEECH_MARKER.match("고 하셨습니다.")` → `False`, vs `SPEECH_MARKER.match("고 했습니다.")` → `True`). No other case file in `tests/exclusion-cases/` exercises this honorific form directly, so this gap in the `quotation` zone is currently invisible in the reported `false_negatives: 0` for that zone. This doesn't make the letter of clause 1 "not met" (a count is reported for every zone), but it means the reported counts understate real defects — worth flagging for whoever reads the P4 record.
>
> **2. Retention on a fixture home (expired/current, every directory; leaves derived/ and annotations/ in place) — MET**
> Evidence: `tests/measure_runner_test.py` builds a fixture under all six `KO_QUALITY_HOME` subdirectories (`logs`, `judge`, `grader`, `exports`, `derived`, `annotations`) with dates spanning the 90-day boundary, runs `measure.runner.run`, and asserts `retention_deleted == ["logs/2026-05.jsonl", "judge/2026-04.jsonl", "grader/2026-05.jsonl", "exports/2025-12.csv"]` while every `derived/*.jsonl` and `annotations/*.jsonl` file (even ones dated 2026-01/2026-05, older than 90 days) survives (`tests/measure_runner_test.py:61-68`). I reran the script fresh (`python3 tests/measure_runner_test.py` → `0 failures`), and independently probed `measure/retention.py`'s `expired()`: at exactly 90 days past a month's last day it returns `False`, at 91 days `True` (strict `>`, matching 09 §20's "more than 90 days"); non-monthly filenames (`readme.txt`) and invalid months (`2026-13.jsonl`) are never touched.
> How it could still be wrong: `retention.py`'s own docstring says "A monthly file is `<yyyy-mm>.<ext>` directly under a text directory," but `enforce()` (line 41) uses `base.rglob("*")`, which recurses into subdirectories. I confirmed this: a file at `logs/sub/2026-05.jsonl` gets deleted too, contradicting the "directly under" claim in the same file. Harmless today since nothing nests text files, but the code's behavior doesn't match its own stated invariant. Also, the fixture's `derived/` and `annotations/` files are only ever old-dated (never a "current" file in those two directories specifically), so "expired and current... in every directory" is satisfied loosely (across the fixture as a whole and strictly for `logs`/text-copy dirs) but not literally per-directory for `derived`/`annotations` — a minor wording gap, not a functional one, since those two dirs are exempt from expiry regardless of date.
>
> **3. Re-running on unchanged input yields identical derived records — MET**
> Evidence: same test, lines 76–80: snapshots the bytes of every `derived/*.jsonl` file, runs `runner.run` a second time, and asserts byte-for-byte equality; also asserts the second run's `retention_deleted == []`. Reran independently and got `0 failures`. Confirmed mechanism: `runner.derive_record` never writes a timestamp, and `run()` writes with `sort_keys=True` over inputs read in deterministic sorted-file/line order.
> How it could still be wrong: only tested on a small, static fixture; large-scale ordering edge cases (e.g., ties in file globbing across many months) aren't exercised, though the sorting is well-defined.
>
> **Checks (flow.md §3 P4)**
>
> **10_plan.md P4.1–P4.3 — MET** (see above, same evidence).
>
> **Release-blocked condition ("a zone's false negatives are not reported") — NOT TRIGGERED.** Every zone has a reported count; see the caveat above about `other_zone` masking a real defect in `quotation`.
>
> **Contradictions found (not asked to fix)**
>
> 1. **Run-log provenance mismatch.** `tests/runs/02-P4/runner-test.txt` (the committed evidence for clauses 2–3) does not match a fresh run of the exact code committed at a6cd821. Diffing my reproduction against the committed file shows only `code_version` differs: committed log says `"code_version": "7def1cd15df13bb3"`, but hashing every `.py` file under `measure/` at this exact commit (working tree is clean, `git status` empty) deterministically gives `"30fff4f9e9b504b2"` — confirmed by computing the hash independently with the same algorithm as `measure/runner.py:19-24`. Every other field (`retention_deleted`, `log_records`, `derived_records`, the per-record `instruction_lang`/`artifact_lang`/`usable` checks, `snapshot == again`) matches exactly. This means the committed `runner-test.txt` log was captured from a slightly different (non-functional, since results match) version of some `measure/*.py` file than what ended up in the final commit — a genuine provenance gap for that one artifact, though the by `tests/runs/02-P4/exclusion-cases-ex-1.json` log I checked separately is byte-identical to a fresh run (that one has no discrepancy).
> 2. **`retention.py` behavior vs. its own docstring**, as detailed above (uses `rglob` where the docstring implies non-recursive "directly under" semantics). Not exercised by any spec/plan requirement either way, but worth a maintainer's attention.
> 3. **`exclusion_cases.py`'s `other_zone` accounting can hide a real false negative** behind an unrelated false positive, as demonstrated with the honorific speech-marker gap in `quotation` (§15.2's done-condition asks that false negatives be measured; this scripted evaluation's bucketing can under-measure them in this specific interaction pattern).
>
> No other contradictions of 09_toolkit_spec.md §11.4/§12.3/§15.1–§15.3/§20, 10_plan.md §4 P4, or flow.md §1 F5/§3 P4 were found. `build/checks.py` (all 6 checks, including check 6's dependency boundary which correctly excludes `measure/` from the stdlib-only scan) passes cleanly at this commit.

**Builder's notes, handled in P5** (recorded there when done):
1. `code_version` difference: confirmed. The venv-inclusive hash is `7def1cd15df13bb3` and the clean hash is `30fff4f9e9b504b2`. P5 excludes `.venv` from the hash.
2. The recursion in retention is intended: judge and grader copies may nest per run, and every copy must expire. P5 fixes the docstring, not the code.
3. `other_zone` masking: P5 adds an isolation check that re-evaluates each `other_zone` positive with the offending span removed, and reports what it finds.
4. Honorific markers (`고 하셨습니다`): P5 adds them and bumps the pass to `ex-2`, with a new case written before running it.

## Release-blocked

None.
