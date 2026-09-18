# P6 — Tier 1 and Tier 2

## Summary

`kiwipiepy` 0.23.2 is pinned in `measure/requirements.txt` (with its three dependencies) and imported lazily, so Tier 0 still runs on the standard library; without the analyser Tier 1 is not computed, the report says why, and the exclusion version carries `-t0`. The ten Tier 1 measurements of 09 §15.4 and `ko.preserve` with five kinds are built, and the proper-noun zone gains its NNP half (`ex-3`). On the committed F7 set (17 correct and 14 telegraphic sentences), `noun_ending_ratio` separates fully (0.00 vs 1.00, as E2) and `particle_absence_ratio` separates fully in E2's direction (means 0.26 vs 0.95; E2: 0.17 vs 0.96). P5's three carried notes are fixed first.
Done-condition: **met on all three clauses** (independent `mid` verification), F7 and F15 met. Release-blocked: **0**.

## Built

| Item | Path | State |
|---|---|---|
| P5 carried notes: `english_gloss_repeat` counts repeats per term; `delegation_prompt_*` fixture; `sentence_len_var` boundary 0.25 on both sides | `measure/measurements/tier0.py`, `tests/measure-cases/t0-*.yaml` (+ `t0-correct-07-first-glosses`), `tests/measure_runner_test.py` | done (`92832da`) |
| Analyser wrapper: lazy import, version, sentences with offsets, spacing | `measure/analyser.py` | done |
| Pin | `measure/requirements.txt`: `kiwipiepy==0.23.2`, `kiwipiepy_model==0.23.0`, `numpy==2.0.2`, `tqdm==4.70.1` | done; installs into a fresh virtualenv (`tests/runs/02-P6/requirements-install.txt`) |
| Proper-noun zone, Tier 1 half (NNP), `ex-3` / `ex-3-t0` | `measure/exclusion.py` | done |
| Tier 1 measurements (10) | `measure/measurements/tier1.py` | done |
| `ko.preserve` (5 kinds), paste-in original extraction | `measure/measurements/tier2.py` | done |
| Registry: tiers available, paste-in records, analyser status in the report | `measure/measurements/__init__.py` | done |
| Case runner: paste-in pairs (`output`), `preserve: [kinds]`, skipped checks | `measure/cases.py` | done |
| Separation report beside E2 (P6.1) | `measure/separation.py`, `python3 -m measure separation` | done |
| Cases: F7 set (5 correct, 4 telegraphic, 1 memo `-음`), other Tier 1 (1 correct, 7 defective), Tier 2 (1 correct, 5 defective) | `tests/measure-cases/t1-*.yaml` (18), `t2-*.yaml` (6) | done: 174 checks, 0 failures (venv); 118 checks, 56 skipped, 0 failures (system Python) |
| Exclusion case: Korean proper nouns and loanword near misses | `tests/exclusion-cases/x13-korean-proper-nouns.json` | done |
| `sentence_len_var` keeps excluded characters as placeholders | `measure/measurements/tier0.py`, `measure/exclusion.py` (`prose(fill=)`) | done |
| Runner test: analyser version or reason, exclusion version, Tier 1 features, paste-in record | `tests/measure_runner_test.py` | done, 0 failures under both interpreters |
| README | `measure/README.md` | done |
| Reports | `tests/runs/02-P6/` (cases, separation, exclusion cases under `ex-3` and `ex-3-t0`, runner test, build checks, install) | done |

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | NNP tagging of transliterated common nouns (`캐시`, `로더`, `스레드`, `쿼리`, `커밋`, `스키마` always; `디렉터리`, `프레임워크`, `플러그인`, `프롬프트` in some contexts): exclude every NNP as 09 §15.2 says / add a loanword denylist / keep NNP out of Tier 0 | **Every NNP, as specified**, with the false positives measured (x13) and handed to review. Best and cheapest coincide: arms share the prompt distribution, so a zone false positive falls on both arms of B − C; a denylist is a new list nobody has validated; splitting the zone by tier breaks "one implementation, shared by every tier" | medium | probe of 50 nouns in two contexts; x13 |
| 2 | minor | `sentence_len_var` after `ex-3` moved `t0-defect-05` from cv 0.2465 to 0.3406, because a masked word at a sentence's start was stripped with the spaces: fix the measurement / loosen the case | **Fix:** excluded characters become a placeholder (`□`) for sentence length, so a sentence keeps its length. Both P5 values return (0.0379, 0.2465) under both versions | medium-high | case diff under `ex-3` vs `ex-3-t0` |
| 3 | minor | Exclusion version without the analyser: same version / suffixed | `ex-3` with the analyser, `ex-3-t0` without; derived records and reports carry the run's value, so the two are never pooled | high | 09 §15.2, §18.4 item 3 |
| 4 | major | `particle_absence_ratio`: 체언 + `VCP` (이다). The recipe names J* only / count VCP as a particle | **VCP is a particle** (서술격 조사 in school grammar). The recipe is silent, not contrary; E2's text does not say how it scored VCP | medium | 09 §15.4 recipe; 학교 문법 |
| 5 | minor | Which lines Tier 1 reads | **Paragraph lines only.** coding.12 exempts headings and lists, and a list item's telegraphic form is a format choice `bullet_density` already counts | medium | 09 §15.4 recipe note |
| 6 | minor | Tokens inside excluded zones | Analyse the raw line (Latin and numbers are `SL`/`SN` anyway); an excluded token is never a subject; a 체언 whose next token is excluded leaves the denominator as `undetermined_dropped`; a sentence ending in an excluded token is `excluded`, not counted | medium | E2 (raw lines first) |
| 7 | minor | Emitted shape of the Tier 1 measurements whose "Emits" column is one word | `speech_level`: labels `hapsyo`/`haeyo`/`haera`/`hae`/`nominal`/`connective`/`other`, `dominant` and `levels_present` over the four verbal levels. `noun_run_length`: runs, mean over all runs, max, `multi_noun_runs`. `ending_monotony`: key = trailing EP/EF/EC/ETN/VX/VCP (up to 4), `ratio` = top ending's share, `longest_run`. `adnominal_chain_depth`: `count` = heads with ≥ 2 stacked ETM/MM, `max`, histogram (upstream's "3중" not applied). `suffix_jeok_density`: 적 count and per 100 어절, `followed_by_noun`, 성/화 beside. `spacing_errors`: Hangul–Hangul gaps where `Kiwi.space(reset_whitespace=True)` differs | medium (low for `ending_monotony` key and `adnominal_chain_depth`) | 09 §15.1 (numbers, not verdicts); rule texts |
| 8 | major | §17.3 case format for a paste-in pair: the rewrite has no field | **`output` added**: `input` stays the original (as §17.3 says), `output` is the rewrite, and the measurements then read `output`. A `preserve` failure is written as a dotted path | medium-high | 09 §17.3; P5 decision 3 |
| 9 | minor | `ko.preserve` kind `quote`: every quote / attributed quotations and block quotes | Attributed and block quotes only: a rhetorical quote is the writer's own sentence, and J-2 removes it | medium | upstream Do-NOT line; J-2 |
| 10 | minor | Paste-in log records: which text is the original | Stratum prefix `paste-in` (annotation `stratum` or `corpus_prompt_id`); the original is the task after its first blank line. **P8's prompt set must write paste-in prompts as instruction, blank line, text** | medium | 09 §18.3 |
| 11 | minor | Pin only `kiwipiepy` / pin the whole resolved set | Whole set (4 lines), verified by a fresh install | high | 09 S3 "pinned" |
| 12 | minor | A Tier 1 check without the analyser | Reported as skipped with the reason, never as a pass | high | 09 §15.6 |

Exploration runs: 0 of 4. For decisions 1 and 4 the specified reading was also the cheapest to reverse, so no cost needed weighing; both are measured and listed for review.

## Subagent runs

| # | Tier | Purpose | Tokens | Verdict |
|---|---|---|---|---|
| V6 | mid (Sonnet 5) | Verification of the P6 done-condition (outside the cap), isolated worktree at `21845c7` | 163,393 | All three clauses **met**; F7, F15 met; noted a trimmed system-Python summary, the unrecorded `sentence_len_var` change (record not yet written), and check 1's crash without the upstream cache |

## Cost

No model calls. **$0.**

## Differs from spec

- **`particle_absence_ratio` counts `VCP` as a particle** (decision 4). The §15.4 recipe says only which tokens to skip and which to drop.
- **§17.3 cases gain `output`** for paste-in pairs (decision 8).
- **`sentence_len_var`, a P5 measurement, changed** how it treats excluded characters (decision 2).
- **The exclusion version has a `-t0` form** for a run without the analyser (decision 3).

## Spec did not know

- **The analyser tags common transliterated technical nouns as NNP**, so the proper-noun zone removes them. On `ex-3`: proper-noun positives 15, false negatives 1 (`김민준` is split `김민/NNP 준/NNG`); negatives 9, false positives 5 (`로더`, `캐시`, `스레드`, `쿼리`, and `클라우드에서도` inside the single NNP token `네이버 클라우드`). Without the analyser the same row has 10 false negatives and 0 false positives (`tests/runs/02-P6/exclusion-cases-ex-3{,-t0}.json`).
- **An NNP token can span a space** (`네이버 클라우드`), and a Korean personal name can be split across tags.
- **Masking to spaces had shortened sentences** whenever an excluded span opened one. It was latent in P5 (numbers, paths) and became visible with NNP.
- **`의존명사 + 용언` (`할 수 있다`) is an absence under the recipe.** It occurs once in the correct set (`absent_by_next.predicate_after_NNB`), and is reported apart so review can size it.
- **Noun compounds drive the correct set's particle absence:** 11 of the 14 absences in the correct set are a 체언 followed by a 체언; `t1-correct-05-technical` is the closest correct case (0.47), as E2's technical case was (0.40).
- **`Kiwi.space` splits some loanwords** (`디렉터리` → `디렉터 리`), a false-positive source for `spacing_errors`.
- **`GitHub` is an identifier to the Tier 0 pass** (camel case), so a rewrite dropping it violates `code_url_path`, not `proper_noun`.

## Verification

Run V6, `mid` (Sonnet 5), prompt per `flow.md` §2, answer as returned:

> Verified at commit 21845c7 (confirmed via `git checkout --detach 21845c7`; `git log -1 --oneline` showed 21845c76). No tracked files were modified during verification (final `git status --porcelain` clean). All reproduce commands were run against `<repository>/measure/.venv/bin/python` (kiwipiepy 0.23.2, confirmed via `pip freeze`) and system `/usr/bin/python3` (no kiwipiepy) as instructed.
>
> ## Done-condition clauses (10_plan.md §4 P6)
>
> **Clause 1 — noun_ending_ratio/particle_absence_ratio separate correct from telegraphic in E2's direction, size reported beside E2**
> verdict: met
> evidence: Reran `VPY -m measure separation`; output byte-identical to `tests/runs/02-P6/separation.json` (diff empty). That file: `noun_ending_ratio`: correct mean/pooled 0.0 (n=17 sentences, 5 cases), telegraphic mean/pooled 1.0 (n=14 sentences, 4 cases), `"direction": "telegraphic higher"`, `"fully_separable": true`. `particle_absence_ratio`: correct mean 0.2584/pooled 0.2857, telegraphic mean 0.9474/pooled 0.9273, `"direction": "telegraphic higher"`, `"fully_separable": true` (min telegraphic 0.7895 > max correct 0.4706). E2's values are read verbatim into the same report under `"e2"` (noun_ending: correct 0.0/telegraphic 1.0/gap 1.0; particle_absence: correct_mean 0.17/defective_mean 0.96/gap 0.79) — reported beside, not restated as identical (measure/separation.py correctly treats E2's uncommitted sentences and this build's committed sentences as different texts, comparing direction/size only, matching spec 09 §15.4's note and the plan's finding-1 resolution).
> how it could still be wrong: this is a single committed case set the builder also wrote, so "separates" is only as strong as the 5+4 case texts chosen; the set does not include an adversarial correct case as close to the telegraphic boundary as E2's own 0.40 "technical-compound" near-miss (t1-correct-05 is "technical" but scores 0.4706 particle_absence, actually the closest — so this concern is addressed by that case, at pooled 0.2857/mean 0.2584 still well under telegraphic's 0.7895 floor).
>
> **Clause 2 — each ko.preserve kind passes and fails its paste-in cases as expected**
> verdict: met
> evidence: `tests/measure-cases/t2-correct-01-preserve-all.yaml` (all 5 kinds pass) plus one dedicated defect case per kind (t2-defect-01..05), each failing exactly its named kind and passing the other four. Reran full cases via venv; `tests/runs/02-P6/cases-tier0-1-2.json` reproduces byte-identical (diff empty). Extracted t2-* rows: all 35 checks pass (`"pass": true`), including e.g. `t2-defect-01-number-unit-date: ko.preserve.number_unit_date.pass equals False → value False → pass True` alongside the other four kinds' `.pass equals True → value True`. Overall report: `"failures": []`.
> how it could still be wrong: all five defect cases share one base text with a single substitution, so "kind X fails, others pass" is demonstrated but not stress-tested against compound failures (two kinds failing at once) or against real corpus paste-ins.
>
> **Clause 3 — Check 6 passes, and the analyser version appears in the run report**
> verdict: met
> evidence: `python3 -m build.checks` initially crashed (`IndexError` in `build/checks.py:132`, check 1's re-extraction subprocess) because this worktree lacks `upstream/.cache/` (gitignored per AGENTS.md, machine-local, never committed — confirmed via `.gitignore`). This is unrelated to P6 (check 1/upstream extraction predates P6; `git log --oneline -- measure/` shows no touch to upstream/build in this commit). I symlinked the main checkout's `upstream/.cache/` into the worktree (read-only use of a gitignored, non-tracked path — no tracked file touched) to unblock the script, reran, got exit 0, and removed the symlink afterward. Output then matched `tests/runs/02-P6/build-checks.txt` exactly: `"check 6 dependency boundary: 23 files under logger, build, upstream, dist, 0 third-party imports"`, `"checks: 0 failures"`. Independently `grep -rn "kiwipiepy" logger/ build/ upstream/ dist/ --include="*.py"` found zero hits, confirming check 6's own AST-based scan. Analyser version: `measure/measurements/__init__.py:report()` includes `"analyser": {"version": "kiwipiepy 0.23.2 (kiwipiepy_model 0.23.0, cong)"}` in the runner's report; reproduced via `VPY tests/measure_runner_test.py`, output byte-identical to `tests/runs/02-P6/runner-test-and-report.txt` (diff empty, including matching `code_version: 7bf5b395db1bc51c`, confirming code is unchanged since that log was written).
> how it could still be wrong: `build/checks.py`'s check-1 crash on an empty subprocess stdout (unhandled `IndexError` rather than a graceful failure message) is a real fragility in committed code, exposed by any environment lacking the upstream cache — worth knowing even though it's outside P6's scope and the recorded log shows check 1 passing in the builder's own environment.
>
> ## flow.md §3 P6 checks (10_plan.md P6.1–P6.3)
> Same three clauses as above — met, same evidence.
>
> **Criteria-only (kiwipiepy install / release-blocked):** not triggered. kiwipiepy 0.23.2 installs and runs (`pip freeze` in `measure/.venv` matches `measure/requirements.txt` and `tests/runs/02-P6/requirements-install.txt` exactly). No release-blocked marker exists anywhere for P6 (`grep -rn "release-blocked" tests/runs/02-P6/ measure/` empty).
>
> **F7 (flow.md §1):** met. The committed separation set (measure/separation.py's CORRECT/TELEGRAPHIC lists) totals 17 correct sentences and 14 telegraphic sentences (≥10/10), confirmed by the reproduced separation.json's `"sentences": {"correct": 17, "telegraphic": 14}`. Pitfalls covered: trailing punctuation (t1-correct-03: `?`, `)` before `.`; t1-defect-04: `!`, `)`, `?`), VV-I/VV-R (t1-correct-02: 듣/돕/걷 irregular stems), 체언+XSV/XSA (t1-correct-01: 고쳤/통과했; t1-correct-04: 필요하). All within the actual cases used for separation, not just decorative comments.
>
> **F15 (flow.md §1):** met. `t1-defect-02-telegraphic-ham` (개조식 -함/-됨/-음) sits inside the TELEGRAPHIC comparison set; `t1-defect-05-memo-eum` (문서체 -음) is deliberately kept in a separate `BESIDE` set and reported apart (`"beside": {"t1-defect-05-memo-eum": {...}}` in separation.json, with `by_final.ef_nominal: 2` matching the case's own expectation) — exactly flow.md's resolution "the case set (F7) includes both kinds and reports them." `measure/measurements/tier1.py`'s `EF_NOMINAL = ("ᆷ", "음")` implements the F15 rule directly, matching the X3 preflight probe's finding (`파일 읽기 실패함` → tagged `EF` with form `함`/ᆷ, counted as noun ending).
>
> ## Contradictions / notable findings
>
> 1. **No `design/02-validation/6-build/P6_*.md` record exists at this commit**, and `6-build/README.md`'s progress table still shows `—` in every column for the P6 row (record, done-condition verdict, release-blocked, cost, last commit), even though `21845c7` (and the preceding `92832da`) are titled as P6 work and contain the complete P6 deliverable (`git show --stat 21845c7` adds all Tier 1/2 code, the case set, and all five `tests/runs/02-P6/*` logs). This is not a contradiction of spec 09/10_plan.md/flow.md content, but it is a gap against AGENTS.md's build process ("Each build step ends with a commit and a record in `6-build/`"; "A stage's done-condition is confirmed by an independent verification subagent... every run is recorded in the stage's build record"). No independent verification run is recorded for P6 prior to this one. This looks like this verification is meant to feed that still-unwritten record, but as of this commit the record-keeping requirement is unmet.
>
> 2. **`tests/runs/02-P6/cases-system-python-tier0-only.json` does not match what the code at this commit actually produces.** Rerunning `python3 -m measure cases` (system Python) reproduces identical aggregate counts (`checks`, `skipped`, `coverage_cases_per_measurement`, `tiers`, `analyser`, `exclusion_version` all equal) but the live run additionally emits `"results"` (118 rows) and `"skipped_checks"` (56 rows) that the committed log lacks entirely — not truncated, just absent as top-level keys. `measure/cases.py`'s `run()` (as committed in this same commit, diffed against P5's `3ce8941`) always returns both keys, and `measure/__main__.py`'s `cases` subcommand never filters them (only `cases.py`'s own standalone `__main__` block filters `"results"`, and even that keeps `"skipped_checks"`). So this one committed log could not have been produced by any invocation path of the code as committed at 21845c7 — it appears stale (e.g., captured against an earlier version of `cases.py` before this commit's `skipped_checks` field was added, or hand-trimmed, and never regenerated before commit). The task instructions anticipated only `code_version`-style value drift ("will match only at this commit"); this is a structural mismatch instead. It does not affect the done-condition itself, which I verified directly via a fresh run (Tier 1 checks correctly reported as skipped with reason `"tier 1 not computed"`, 0 failures on the 118 Tier-0/Tier-2 checks that did run).
>
> 3. Minor, undocumented-anywhere-except-the-commit-message deviation: `sentence_len_var` (a Tier 0 / P5-era measurement) was changed in this P6 commit to keep excluded characters as a placeholder (`□`) rather than a space, "so a masked word no longer shortens a sentence" (commit message: "P6: NNP made the loss visible"). This is a real behavior change to already-shipped P5 code, made in the P6 commit, and — absent a P6 build record — is currently recorded nowhere but the commit message (not in a "Differs from spec" / "Spec did not know" section as AGENTS.md's record format prescribes). By contrast, the other two code changes bundled into this commit against P5 code (`english_gloss_repeat` counting repeats not raw occurrences, and the `delegation_prompt_*` test) were pre-planned: they exactly match the three "carried notes" at the end of `design/02-validation/6-build/P5_tier0.md`, so those are not undocumented, only this placeholder change is.
>
> ## Key files
> - `<worktree>/measure/separation.py`
> - `<worktree>/measure/measurements/tier1.py`
> - `<worktree>/measure/measurements/tier2.py`
> - `<worktree>/measure/measurements/__init__.py`
> - `<worktree>/measure/cases.py`
> - `<worktree>/measure/exclusion.py`
> - `<worktree>/build/checks.py`
> - `<worktree>/tests/measure_runner_test.py`
> - `<worktree>/tests/runs/02-P6/` (separation.json, cases-tier0-1-2.json, cases-system-python-tier0-only.json, exclusion-cases-ex-3.json, exclusion-cases-ex-3-t0.json, build-checks.txt, runner-test-and-report.txt, requirements-install.txt)
> - `<worktree>/design/02-validation/6-build/README.md` (P6 row blank)
> - `<worktree>/design/02-validation/6-build/P5_tier0.md` (carried notes)
>
> I did not fix or modify anything; no tracked files changed.

**Builder's notes on the findings:**
1. The record did not exist at the verified commit by design: the record is written after verification (this file).
2. `cases-system-python-tier0-only.json` was trimmed on purpose when it was written: the `results` and `skipped_checks` lists were dropped to keep a summary beside the full venv report; the counts are the run's. The file name says what it is, but the trimming was not stated. It is stated here.
3. The `sentence_len_var` change is decision 2 and is listed under Differs from spec.
4. Check 1 raises `IndexError` without `upstream/.cache/` instead of failing with a message. Outside P6's scope; carried to review.

## Release-blocked

None.
