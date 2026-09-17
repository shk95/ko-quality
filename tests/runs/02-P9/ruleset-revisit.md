# `ruleset` revisit (09 §17.4, 10_plan.md P9.3)

Exploration run R9-1, `mid` (Sonnet 5), 157,544 tokens, 2026-09-17. The candidate was cloned outside the tree at `05ce76d` and read there; nothing from it is in this repository. The answer is recorded as returned. The builder's reading is at the end.

---

## 1. Repository, licence, and rule count

Cloned `JangHyun-bin/korean-report-skills` at `05ce76d` (tag: Release v1.18.1, 2026-09-05; `package.json` version `1.18.1`).

**Licence confirmed exactly as §17.4 states**: root `LICENSE` is Apache License 2.0. Root `NOTICE` carries copyright (2026, 장현빈) and, under a Korean-language section, three third-party build-time dependencies (KaTeX/MIT, Pretendard/OFL-1.1, Playwright/Apache-2.0) that are *not* bundled in the skill payload itself. `package.json` declares `"license": "Apache-2.0"`. Nothing here contradicts §17.4.

**Where the rules live**: `plugins/korean-report/skills/korean-report-style/`
- `references/substitutions.md` — a Markdown table, single source of truth, parsed by `assets/lint.py`'s `load_rules()`. Each row is `찾기/쓰지 않는다` → `바꾸기/쓴다`, optionally with `검사 범위` (scope: all/prose/heading/table/html) and `검출 방식` (literal or regex).
- `assets/lint.py` (876 lines) — the checker: parses the table, applies literal/regex matching per scope, plus **code-only** (non-table) checks: heading-must-be-noun-phrase, emoji, bold-label-echo lists, heading-echoed-by-next-sentence, and paragraph-level density (bold overuse, hedge-word overuse, from `references/density.md`).
- `assets/morph.py` (324 lines) — a **second, morphological** layer, active only if `kiwipiepy` is installed: closed-class stem/unit-noun/ending rules from `references/morphology.md`, applied via POS tags rather than string matching (verb-stem precision, personification-by-subject, unit-noun/counted-object mismatch, formality-register majority/minority, adjective-conjugation errors).

**Rule count — the "115" figure is stale.** I ran `load_rules()` against the table at the pinned commit: **136 rules** (no `--heuristic`), **143** with the separate `software-handoff.md` heuristic table folded in. `CHANGELOG.md` shows exactly where "115" comes from: `v1.2.0` (2026-08-10) says "치환표 78 → 115건" and `v1.11.0` (2026-08-11, when `lint.py` first shipped) still says "치환표 115행." Two later PRs — `#13` ("서식 갈래와 1단계 규칙 네 건") and `#14` ("Add the filler substitutions and the two density rules") — added the §10 (대화 잔재, 7 rules) and §11 (군더더기 구문, 9 rules) sections plus two density checks, after the point ko-quality's own `01a_findings_survey.md` recorded "115." So **115 was correct once, but is roughly 20% under the pinned commit's actual count (136).** Any adoption-cost arithmetic in the next stage should re-run `load_rules()` against the pinned commit rather than reuse "115."

Section breakdown at HEAD (table-driven only):

| Section | Rows | Match | Tier |
|---|---|---|---|
| §1 어미 (contraction expansion, 됐다/했다→되었다/하였다) | 13 | literal/regex | 고침 (auto-fixable) |
| §2 제목 (heading rewrites) | 18 | literal | 검토 |
| §3 구어체 환언 (colloquial paraphrase) | 14 | literal | 검토 |
| §4 의인화·물리 은유 (personification) | 14 | literal | 검토 |
| §5 번역투 (calque) | 7 | literal | 검토 |
| §6 과장·위협 (hype/threat framing) | 7 | literal | 검토 |
| §7.1 광의→협의 어휘 (vague verb → precise Sino-Korean) | 27 | literal | 검토 |
| §7.2 외래어 표기 (keep English for spec terms) | 4 | literal | 검토 |
| §7.3 격식체·외래어 (bureaucratic Sino-Korean) | 6 | literal | 검토 |
| §8 결함→역량 프레이밍 (defect→capability reframing) | 10 | literal | 검토 |
| §10 대화 잔재 (chat-residue phrases) | 7 | literal | 고침-adjacent/검토 |
| §11 군더더기 구문 (wordy filler) | 9 | literal | 고침 (auto-fixable) |

Plus code-only, non-table checks in `lint.py` (heading-is-noun-phrase, emoji, bold-label-echo, heading-echo, bold/hedge density) and `morph.py`'s POS-tag rules (9 core + 9 "주의" verb stems, 13 animate-verb stems, ~9 unit-noun corrections, formality-majority check, adjective-conjugation check).

## 2. Characterisation

Two important facts cut across the whole comparison:

**(a) Roughly half the 136 table rows are fictional-example sentences, not portable rules.** The table's own header says so explicitly: "이 표는 예시이지 목록이 아니다" (this table is an example, not a list). §2 (18), §3 (14), §6 (7), §8 (10), and most of §4's table half (14) are literal phrases lifted from one invented case study ("A사 — 인라인 계측 체계 확립과 수율 개선," a semiconductor-yield report). They will only ever fire on text that reproduces that exact fictional example — they are teaching material for a judgment principle (e.g. "a heading should be a noun phrase," "don't personify equipment"), not reusable detectors. That's **~63 of 136 rows with zero direct transfer value**; the other **~73** (§1, §5, §7.*, §10, §11, plus the code-only checks) are genuinely reusable patterns or mechanisms.

**(b) There are two detection mechanisms, matching this repo's own Tier 0/Tier 1 split.** Literal/regex table rows are Tier-0-equivalent (surface, standard-library regex). `morph.py`'s stem/tag rules are Tier-1-equivalent (need a morphological analyser) — and the project's own commit history proves the necessity: `morphology.md` states that of 14 sentences violating one rule only by inflection, "literal-string matching let 7 of 14 through," which is exactly why this repo's Tier 1 exists.

By kind of text change:
- **Register/formality**: §1 (contraction expansion), §4.1 morph (평서체/합니다체 majority check), §5 morph (형용사 활용 오류) — correctness/house-style, not AI-tell detection.
- **Word choice precision**: §7.1/7.3 — a vague-native-verb-to-precise-Sino-Korean-verb axis this repo's taxonomy does not have at all.
- **Calque/번역투**: §5 — same *category* this repo already targets heavily, but different literal instances.
- **Chat/assistant residue**: §10 — direct AI-tell category, phrase-level.
- **Wordy filler**: §11 — classic redundant-phrase reduction, some categorical overlap with existing entries.
- **Personification**: §4 table (fictional, non-transferable) + `morph.py`'s generalised subject-check version (transferable, needs analyser).
- **Structural/format**: emoji, bold density, bold-label-echo, heading-echo, heading-shape — code, not table rows.
- **Grammar correctness**: `morph.py`'s unit-noun and adjective-conjugation checks — fits this repo's existing "grammar" measurement family (allomorph_errors, spacing_errors) but isn't in it yet.

## 3. Coverage against this repository

I checked every class against `measure/data/phrase_battery.json`, `measure/measurements/tier0.py`, `tier1.py`, and the upstream taxonomies (`rewrite.yaml`, `diagnose.yaml`), plus `upstream/normalized/policy/fluent-korean.yaml` for the policy-layer items.

**Covered (same defect, already measured):**
- §4.1 formality-register mixing (morph.py) ↔ **`speech_level`** (Tier 1) — exact match; `phrase_battery.json`'s own `omitted_rewrite_patterns` already lists `"E-7": "speech_level (Tier 1)"` for this.
- Bold-overuse density (§10.4/density.md) ↔ **`bold_density`** (Tier 0) — same defect, different threshold granularity (per-paragraph count vs per-100-eojeol ratio).
- Emoji (§10.1, code) ↔ **`emoji_count`** (Tier 0) — exact match.
- §5's "갖는다/가지다" calque instance ↔ **`diagnose.031`** (가지다/갖다 직역) — the specific instance matches.

**Partly covered (same category, different instance/mechanism):**
- §5 번역투 (the other 6 items) ↔ this repo's `rewrite.A-*`/`diagnose.02x-04x` 번역투 family — same category, but each is a different literal calque, so no row-for-row match.
- §10.5 완충어 과잉 (hedge-word density, 14-word open list, per-sentence) ↔ **`diagnose.055`** (hedging 중첩, 3-pattern regex alternation, per-document) — same theme (hedging pile-up), different word list and counting unit.
- §11 군더더기 구문 — 2 of 9 (`경우에 있어서는`, `수행하는 역할을 한다`-type) are near-misses of existing `rewrite.A-3` (에 있어서) and `diagnose.057` (역할을 하다), but the exact strings/regex don't fire on these particular inflections.
- §6 과장·위협 ↔ `rewrite.D-4`/`diagnose.056` (혁전적/획기적 hype vocabulary) — same theme (exaggeration), disjoint lexicon.

**Not covered:**
- §1 어미 contraction expansion (13) — no equivalent; also arguably out of mission (register house-style, not an AI-tell).
- §2 제목 rewrites (18) — N/A, non-transferable fictional examples; but the underlying **code check** (heading must be a noun phrase, not declarative/interrogative/clausal) has **no equivalent** in `header_formula`, which only checks colon-subtitles and a formulaic-heading denylist, not sentence shape.
- §3 구어체 환언 (14) — N/A, non-transferable.
- §4 personification, generalised form (morph.py, 13 verb stems + subject detection) — **no equivalent**; directly relevant to this repo's own `phrase_battery.json` note that **D-5** ("personified abstract subject needs meaning") was excluded as "no surface form."
- §7.1/7.3 word-choice precision (33 rows, 18 generalised stems) — **no equivalent anywhere in the taxonomy**; this axis (vague-verb precision) isn't part of `rewrite.yaml`/`diagnose.yaml` at all.
- §7.2 외래어 표기 (4) — opposite intent to `diagnose.130` (미번역 용어), not applicable.
- §8 결함→역량 프레이밍 (10) — N/A, non-transferable narrative reframing, not a linguistic pattern.
- §10 대화 잔재 (7) — **no equivalent**; checked `rewrite.yaml`, `diagnose.yaml`, and `policy/fluent-korean.yaml` for "도움이/궁금/말씀/좋은 질문" — nothing. This is the single clearest AI-tell gap: assistant-reply filler ("도움이 되었기를 바랍니다," "좋은 질문입니다," "더 필요하시면 말씀해 주세요") sits in the same policy/agent-reply layer as `em_dash_count` and `honorific_address`, which this repo already measures.
- §10.2/§10.3 bold-label-echo and heading-echo (code) — no equivalent; `bullet_density`/`header_formula`/`paragraph_initial_repeat` are adjacent but don't detect either pattern.
- `morph.py`'s unit-noun mismatch and adjective-conjugation error (형용사+동사어미) — no equivalent; both are grammar-correctness classes that would sit naturally beside `allomorph_errors`/`spacing_errors` (this repo's existing "grammar" family, sourced from `korean-skills`), but aren't implemented.

## 4. Implementation cost for the not-covered items

| Class | Cost in this repo's terms | Note |
|---|---|---|
| §1 어미 contraction (13) | cheap — literal/regex `phrase_battery.json` entries | low relevance to AI-tell mission |
| §7.3 격식체 (6) | cheap — literal entries | low-moderate relevance (formal-document register, not AI-tell) |
| §10 대화 잔재 (7) | cheap — literal entries, fits the existing "policy"/agent-reply layer directly | **highest relevance, lowest cost** of everything found |
| §11 군더더기 구문 (9, minus ~2 near-duplicates) | cheap — literal/regex entries | some already fixable 1:1 like their own `--fix` |
| Heading-is-noun-phrase (code) | cheap-moderate — new Tier 0 function, pure regex, reuses the existing heading extraction that `header_formula` already does; **no exclusion-pass change needed** | new AI-tell-relevant structural check |
| Heading-echoed-by-next-sentence (code) | cheap-moderate — new Tier 0 function, regex + adjacency over lines already split into paragraph/heading kinds; **no exclusion-pass change** | |
| Bold-label-echo list (code) | moderate — new Tier 0 function needs list-item-run detection with label-vs-body comparison; **no exclusion-pass change** | |
| Personification via subject-check (morph.py, 13 stems) | **needs the analyser** (Tier 1) — subject-detection off a closed animate-noun exception list, would live beside `noun_ending_ratio` etc.; would also need a new exclusion decision for the animate-noun allowlist (their `animate_nouns` set) | fills the currently-excluded D-5 gap |
| Word-choice precision, §7.1 (18 generalised stems) | **needs the analyser** — their own testing shows literal matching misses half of all violations by inflection; a fresh closed-stem table plus Tier-1-style stem lookup | new taxonomy axis, questionable mission fit |
| Unit-noun mismatch (morph.py) | **needs the analyser** — NNB/NNG tag after a numeral | fits existing "grammar" family |
| Adjective-conjugation error (morph.py, 필요한다 등) | **needs the analyser** — XSA vs XSV tag distinction | fits existing "grammar" family |
| Hedge-word density refinement (§10.5) | cheap-moderate — could extend `diagnose.055`'s word list, but changing unit from per-document count to per-sentence density is a small measurement-code change, not just a data entry | |

None of the cheap/data-only items need an exclusion-pass change (they're literal or simple regex over already-excluded prose). The three analyser-dependent items (personification, §7.1 precision, unit-noun, adjective-conjugation) would need **new Tier 1 code**, not just data, and the personification item specifically would need a new exclusion-pass decision for its animate-noun allowlist, mirroring what `LEXICAL_EXCEPTIONS` already does for allomorphs.

## 5. Legal/provenance requirements for adoption

Per `AGENTS.md`'s "Upstream text" section and the pattern already in `upstream/lock.yaml` / `upstream/normalized/taxonomy/rewrite.yaml`:

- **`lock.yaml` entry**: a fifth entry (`name: korean-report-skills`, `url`, `commit: 05ce76d...`, `license: Apache-2.0`, `license_checked`, `roles: [ruleset]`) — same shape as the four existing MIT entries, mechanically easy.
- **Per-fragment provenance**: every extracted rule/pattern needs `{upstream, commit, path, anchor, content_hash, transform}` fields exactly like the existing `rewrite.yaml`/`diagnose.yaml` fragments (e.g. `severity.S1` with `transform: verbatim`). This is the same P1-era mechanical work already done four times.
- **New obligation this repo hasn't had yet: carrying the NOTICE.** All four current upstreams are MIT (attribution-only, satisfied by the per-fragment provenance already kept). Apache-2.0 §4(d) requires that a work containing an Apache-licensed NOTICE carry a readable copy of its attribution notices in *some* form (a NOTICE file, source comments, or documentation) in derivative distributions. **`ko-quality` has no root `NOTICE` file today** (confirmed: `find . -iname "NOTICE*"` returns nothing outside `upstream/.cache/`, which is gitignored anyway). Adopting `korean-report-skills` would be the first upstream to trigger this, meaning either a new root `NOTICE` file or an equivalent attribution surface would need to be added and kept in sync — a small but genuinely new piece of process, not just a data-entry cost.
- **Marking changes**: Apache-2.0 §4(b) requires marking modified files with notice of changes. Since this repo's practice is to *extract into `normalized/` as data*, not redistribute their code files, the existing `transform: adapted` convention (06 §5.4, mentioned in `AGENTS.md`) should satisfy this for any fragment whose wording is changed — same mechanism already used for MIT upstreams, just now load-bearing rather than a nicety.

## Case for adopting now, and where it breaks

Adopting now would buy: a working, currently-running checker for §10 (chat residue — genuinely missing and squarely AI-tell), the code-only heading/echo/bold-label checks (also missing), and validated evidence for how morphological generalisation should work for personification (D-5, currently excluded). It breaks on the spec's own logic: **the "115 vs. remaining battery" comparison the spec set up as the re-entry criterion is itself now wrong** — the actual number is 136 (and even that overstates transferable content roughly 2×, since ~63 rows are fictional-example dead weight). Doing the comparison "now," with stale numbers, means re-doing it anyway once the real count is used. E5's other blocker also still applies undiminished: no `ruleset.schema.yaml`, no interface slot, no normalizer, no build check — the full P0–P4 apparatus for a fifth vendor, which is exactly what E5 said isn't this era's job.

## Case for deferring, and where it breaks

Deferring is consistent with E5/§17.4's own stated entry criterion once corrected for the real count: the exclusion pass and Tier 0 (16 measurements) and Tier 1 (10 measurements) already exist per the background documents, so the "revisit" trigger condition is arguably already met *now*, just with different numbers than the spec assumed (136 rules, not 115; and only ~10 of those rules/mechanisms are genuinely not-covered-and-worth-having, not "the whole remaining battery"). Deferring further risks the same drift repeating: the pinned commit will keep moving (the source repo shipped 5+ releases between "115" being recorded and today), so each re-check costs a re-clone and a re-count, and the licence/NOTICE gap (item 5 above) doesn't get smaller by waiting.

## Summary table

| | Count |
|---|---|
| Rules at HEAD `05ce76d` (table-driven, `load_rules()`) | 136 (was cited as 115 — stale since PRs #13/#14) |
| Rules with heuristic table included | 143 |
| Table rows tied to one fictional example, non-transferable | ~63 |
| Genuinely transferable table rows/mechanisms | ~73 (+ 5 code-only checks + 4 morph.py mechanisms) |
| Covered by this repo already (same defect) | 4 (speech_level/§4.1, bold_density/§10.4, emoji_count/§10.1, diagnose.031 instance) |
| Partly covered (same category, different instance/mechanism) | ~4 classes (§5 remainder, §10.5 hedging, §11 near-dupes, §6) |
| Not covered, cheap (data entry only) | ~4 classes (§1, §7.3, §10 대화 잔재, §11 remainder) |
| Not covered, moderate (new Tier 0 code, no exclusion-pass change) | 3 (heading-is-noun-phrase, heading-echo, bold-label-echo) |
| Not covered, needs the analyser (new Tier 1 code, possibly exclusion-pass change) | 4 (personification/D-5, §7.1 word-choice precision, unit-noun mismatch, adjective-conjugation) |

---

## Builder's reading (for review, not a decision)

- **Adoption stays deferred in era 02**, as 09 §17.4 says; 6-build does not open a fifth upstream (schema slot, normalizer, lock entry, NOTICE). The comparison §17.4 asked for is now recorded, with the corrected count.
- **The spec's number is stale:** 136 rules at the locked-for-licence commit, not 115. About 63 are examples tied to one fictional report.
- **The gap worth the most for this toolkit is §10 대화 잔재** (assistant-reply filler): 7 literal phrases, a data entry in `phrase_battery.json`, in the policy layer where B − C is measured. It is not in any locked upstream, so adding it would be our text or theirs, and either choice is a review decision.
- **Adoption would be the first Apache-2.0 upstream**, which brings a NOTICE obligation this repository has not had.
