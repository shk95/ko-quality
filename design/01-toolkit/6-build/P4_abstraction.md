# P4 — abstraction

2026-09-14. Branch `dev`. Flow: `5-preflight/flow.md` §3 P4.

## Result

The P1–P3 temporary format now has written schemas (`upstream/interface/`) and code extractors (`upstream/extractors/`). The code reproduces the hand outputs byte for byte, except 25 anchor lines in the policy file, where the change fixes two duplicate anchors. 06 §12 check 1 runs: `check: 8 files, 474 fragments, 0 failures`. The update test moved im-not-ai back 10 commits: the report named every changed fragment and matched the upstream commit log. Moving forward again (the lock commit) gave 0 failures. **Abstraction test passed:** korean-skills went in from the schema and conventions alone without a schema field or enum change. It found two defects in the shared parser, now fixed, and five places where the schema documentation was silent, now clarified. With four upstreams, check 1 reports `11 files, 988 fragments, 0 failures`.

| Artifact | Path |
|---|---|
| Schemas | `upstream/interface/{common,procedure,taxonomy,reference,policy}.schema.yaml` |
| Extractors | `upstream/extractors/` — `source.py` (lock, `git show <commit>:<path>` from the cached clones), `markdown.py` (block parser, anchor forms), `normalized.py` (YAML write/read, hash), `validate.py`, `im_not_ai.py`, `yoonmoon.py`, `fluent_korean.py`, `__main__.py` (`extract`, `check`, `diff`, `validate`), `README.md` (conventions for a new upstream) |
| Update test log | `tests/runs/P4/update-test.txt` |
| Fourth upstream | `upstream/extractors/korean_skills.py`; `upstream/normalized/procedure/grammar.yaml` (93 fragments, 39 excluded), `reference/grammar/rules.yaml` (190, `kind: rubric`), `reference/grammar/common-errors.yaml` (231, `kind: recipes`) |

## Hand vs code

`python3 -m upstream.extractors extract` over the committed P1–P3 files:

| File | Diff |
|---|---|
| `procedure/rewrite.yaml`, `taxonomy/rewrite.yaml`, `procedure/diagnose.yaml`, `taxonomy/diagnose.yaml`, `reference/diagnose/*.yaml` (3) | **0** |
| `policy/fluent-korean.yaml` | 25 lines changed, all `anchor:` lines (0 non-anchor lines). P3 anchored list items by marker (`item -`, `item 1.`), so the two bullets under `## 상황과 목표` shared one anchor in each variant, against 06 §5.5 rule 2. The code uses P2's ordinal form (`item 1`, `item 2`). Fixed on the normalized side; the dist sidecar references ids, not anchors, so `dist/` is unaffected (provenance checks still 111/320/56 spans, 0 errors) |

`validate`: 0 errors, which includes anchor uniqueness in every file.

## Update test

Upstreams had not moved since the lock (`git ls-remote`, all four HEADs equal to the lock), so flow's fallback applied: im-not-ai back 10 commits (`0df19680`, 2026-08-29) and forward again.

| Report | Fragment | Upstream change in the window |
|---|---|---|
| ANCHOR NOT FOUND | `pattern.A-22`, `pattern.A-24` | added in `3bb1457` and `bf48b12` |
| HASH DIFFERS | `pattern.A-16` | heading and rule replaced ("조준 교체", `3bb1457`) |
| HASH DIFFERS | `pattern.C-8` | quick_pattern changed (`d2d1188`, `0899cc8`) |
| HASH DIFFERS | `pattern.C-11`, `pattern.D-14`, `check.5` | no-injection rule and lexicon tiers (`fea0e34`) |

Each HASH DIFFERS line shows the first differing character and the text around it for both sides. **D1 re-diff:** C's 철칙 1–9, the header's 서법 보존 and B's steps produced no failures across the window, so the invariants B's skeleton relies on did not drift in these 10 commits. (B itself was last changed before the window, on 2026-08-09.) Forward at the lock: `check` 0 failures.

## Abstraction test

A fresh `mid` run (exploration run 1) got the schemas, `upstream/extractors/README.md`, the shared modules (`source`, `normalized`, `markdown`, `validate`, `__main__`), the lock, spec 06 §5 and §7, and the korean-skills files. It was not given the other extractor modules, `upstream/normalized/`, `dist/` or the design records. It could write only `korean_skills.py` and its outputs.

**Outcome (06 §14 P4: "스키마를 고치지 않고 들어가면 성공").** Passed. No schema field, enum or shared module was changed by the run. 514 fragments, all `verbatim`; `validate` 0 errors, `check` 0 failures.

**Contamination, disclosed by the run.** While listing directory depth it printed `upstream/normalized/procedure/rewrite.yaml`, which it was not given. The run reports the file's structure matched what `normalized.py` and `common.schema.yaml` already state. The test is weaker than clean-room by that one file; the choices it made (kinds per heading, reference kinds) are not visible in rewrite.yaml.

**Shared-code defects it found (worked around in its module, then moved into `markdown.py`).**

| Defect | Input | Fix |
|---|---|---|
| `split_frontmatter` crashed on a bare `key:` with indented children | SKILL.md `metadata:` / `  author:` / `  version:` | Bare keys keep their indented child lines as the value |
| `table separator` anchors collided when one heading holds two tables | common-errors.md `### 5. 가운뎃점(·) 오남용` | Any repeated anchor in a file gets ` > N` (06 §5.5 rule 2); schema form `repeated` |

After the move, the module's workarounds were removed and all 11 normalized files were regenerated byte-identical to the run's output.

**Where the schema was silent (clarified in the schema text; no field or enum added).**

| Gap | What the run did | Clarification |
|---|---|---|
| `reference.kind` values had no meanings | Inferred from 06 §7's examples: rules → rubric, common-errors → recipes | Meanings with examples in `reference.schema.yaml` |
| No anchor form for frontmatter in `excluded` | Used `frontmatter > <key>` | Form `frontmatter` in `common.schema.yaml` |
| Bold-label-only paragraphs that group items | Excluded as structure, by analogy with headings | Listed under `excluded.typical` |
| No kind for "scope of what is checked" (grammar has no taxonomy slot) | Filed under `invariant` | `invariant` meaning covers it in `procedure.schema.yaml` `kind_meanings` |
| Confidence tiers | Filed under `grade` | `grade` meaning in `kind_meanings` |

**For P5.** `procedure/grammar.yaml` has 37 `invariant` and 36 `step` fragments; ko-grammar's SKILL.md body will not fit 100 lines without moving material to `references/` (the P2 criterion). One kept sentence names the Claude Code `Read` tool (`### 1단계` item 2, noted in the fragment); P5 decides whether it is `selected` out.

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | structural | Redesign the on-disk format now (file-level provenance defaults, readable text, whole-file fragments) / write schemas for the format as built | As built, frictions recorded with a disposition | medium | The diff-0 comparison only means something against the committed files; P5 is the first consumer and has not asked for a different shape; a redesign would rewrite 474 fragments. Revisit in 7-review with P5's experience |
| 2 | major | Check 1 compares fresh and committed fragments by (path, anchor) / by id | (path, anchor) | high | whole-file ids are block positions and shift on insertion; anchors are what 06 §5.5 names |
| 3 | minor | Read upstream files with `git show <commit>:<path>` from the cached clone / check out each commit | `git show` | high | any commit, no working-tree changes, enables `diff` |
| 4 | minor | Fix P3's duplicate anchors by adopting P2's ordinal form / add a disambiguating suffix to P3's form | P2's form | high | one form for items across whole-file extractions |
| 5 | minor | Validator in stdlib reading our own format / add PyYAML and a JSON Schema validator | stdlib | medium | PyYAML is not installed; the format is ours and narrow |
| 6 | minor | Parser keeps a fenced block whole as one paragraph (new) / unchanged P2 parser | Fence-aware | high | 06 §5.5 rule 1; P1–P3 files had no fences in extracted parts, so the change did not alter their output (diff 0). korean-skills SKILL.md's fenced output template (headings inside) came out as one paragraph, as intended |
| 7 | major | **D5 final shape:** one `reference` role with `kind` / split into roles per kind / fold into procedure | One role with `kind` | medium-high | 5 reference files from 2 upstreams used 3 of 4 kinds with no role-level difference in handling; a split adds roles without a consumer that treats them differently |
| 8 | major | **06 §7 ko-grammar references:** `rules.md` → reference `rubric`, `common-errors.md` → reference `recipes` / leave unsupplied | Supplied as references | medium | SKILL.md step 3 tells the model to load both when unsure; leaving them out strands that step (abstraction run's argument, checked against the text) |
| 9 | minor | Move the run's workarounds into shared code / leave them in the module | Shared code | high | both are general (any nested frontmatter, any repeated anchor); outputs unchanged |

## Temporary format friction — disposition

| Friction (P1–P3 records) | Disposition in P4 |
|---|---|
| Positional sub-item anchors (`bullet N`, `sentence 1`) | Kept; all forms listed in `common.schema.yaml` `anchor.forms`. The update test shows positional anchors held over 10 commits for these files |
| Provenance repeated per fragment | Kept (06 §5.5 says every fragment carries it); deferred to 7-review |
| Text as JSON strings | Kept; deferred (no YAML library in the toolchain) |
| Non-contiguous fragments (pattern = heading + meta line) | Kept as `kind: pattern`; render rule stays in the renderer (P5) |
| Tables need header and separator fragments | Formalized as kinds `table-header`, `table-sep` |
| Tag structure has no place in YAML | Formalized: tag context lives in the anchor (`tag/tag[n=…]`); renderers supply tag lines |
| Reference role needs `name`, `kind` | Formalized in `reference.schema.yaml` |
| List markers stripped (P1) vs kept (P2, P3) | Kept as built; the two conventions are tied to selection vs whole-file extraction |
| Frontmatter as data | Formalized: `data:` section in `policy.schema.yaml` |
| Two variants stored twice | Kept (06b decision a) |
| Blank-line counts | Parser records them; not stored (rendering concern) |
| Whole-file references fragmented only to render back | Kept; deferred to 7-review with decision 1 |
| Composition has no home | Unchanged; `assemble/profiles/` in P5 |
| Two kind vocabularies (structural vs semantic) | Formalized as two enum groups in `common.schema.yaml` |

## Subagent runs

Exploration cap: 1 of 4 used.

| # | Tier | Purpose | Tokens | Result |
|---|---|---|---|---|
| 1 | mid (Sonnet 5) | Abstraction test: korean-skills grammar from the schema and conventions only | 134.5k | Passed without a schema change; 2 parser defects, 5 documentation gaps; one out-of-scope file read (disclosed) |
| V | mid (Sonnet 5) | Verification of the done-condition (outside the cap) | _pending_ | _pending_ |

## Release-blocked

_(Updated after the verification run.)_
