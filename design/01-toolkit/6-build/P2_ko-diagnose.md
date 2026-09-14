# P2 — yoonmoon → `ko-diagnose`

2026-09-14. Branch `dev`. Upstream yoonmoon at `c8885310` (lock). Flow: `5-preflight/flow.md` §3 P2.

## Result

`ko-diagnose` is hand-built for Claude Code with P1's temporary YAML shape, unchanged. All four runs fired the skill and produced the upstream report shape without modifying the text. The short SNS comment was the only input that loaded `xdac-research.md`. When one request asked for both diagnosis and fixing, `ko-diagnose` and `ko-rewrite` both fired and each read only its own reference files. 320 upstream spans recompute; 0 `adapted`.

| Artifact | Path |
|---|---|
| Normalized procedure | `upstream/normalized/procedure/diagnose.yaml` — 71 fragments, from `skills/detect/SKILL.md` |
| Normalized taxonomy | `upstream/normalized/taxonomy/diagnose.yaml` — 151 fragments (55 table rows: 52 patterns + 3 severity), from `skills/humanize/references/ai-tell-taxonomy.md` |
| Normalized references | `upstream/normalized/reference/diagnose/{lread-rubric,katfishnet-research,xdac-research}.yaml` — 41, 25, 32 fragments; `kind`: rubric, research, research |
| Our skill template | `assemble/skills/ko-diagnose.md` |
| Skill | `dist/claude-code/skills/ko-diagnose/SKILL.md` (97 lines, body 91), `references/{scoring-and-report,taxonomy-diagnose,lread-rubric,katfishnet-research,xdac-research}.md`, `SKILL.provenance.yaml` |
| Test cases, run summary | `tests/cases/ko-diagnose.yaml`, `tests/runs/P2/ko-diagnose.json` |
| Provenance check | `tests/check_provenance.py dist/claude-code/skills/ko-diagnose` → `320 upstream spans checked, 0 errors`; ko-rewrite still `111 …, 0 errors` |

Fidelity: the three reference files render byte-identical to upstream. `taxonomy-diagnose.md` is identical to upstream apart from the title and the `## 목차` section, whose trailing `---` rule goes with the excluded section.

## What went where

- **SKILL.md:** `<role>`, `<resources>`, `<workflow>` (phases 0, 1, 1S, 2), `<cautions>`, `<outOfScope>`, all verbatim, tag lines kept as structure.
- **`references/scoring-and-report.md`:** `<fluencyTrap>`, `<scoringRubric>`, `<outputFormat>`. Moved to bring the body from 118 to 91 lines (flow P1 criterion: move non-step material first, never cut). The ours notes tell the model to read it before Phase 2; every run did.
- **Excluded:** detect frontmatter (ours `description`), detect H1, taxonomy H1, taxonomy `## 목차`.
- **Not supplied, left verbatim:** 3 links in the taxonomy to `../../translate-polish/references/translationese-research.md`; `polish-all` routing sentence in `<outputFormat>` 1; `humanize` skill mentions. The notes map `humanize` → `ko-rewrite`, `../humanize/references/*` → our file names, and say `polish-all` is not part of the toolkit.

## Runs

Claude Code 2.1.270, `claude-opus-5[1m]`, headless, user settings excluded, empty cwd. Four runs, $1.60.

| Case | Owner | Skills fired | Files read | Verdict (AI 가능성 / 신뢰도 / 번역문 / 장르) | Text modified by ko-diagnose |
|---|---|---|---|---|---|
| ai-column (yoonmoon 칼럼 `<before>`) | upstream | ko-diagnose | scoring-and-report, taxonomy-diagnose, lread-rubric | 높음 / 중간 / 낮음 / 논술·에세이 결론 | no |
| human-academic (im-not-ai golden 02) | upstream | ko-diagnose | scoring-and-report, taxonomy-diagnose, lread-rubric | 중간 / 낮음 / 낮음 / 학술 논문 | no |
| short-sns | ours | ko-diagnose | scoring-and-report, **xdac-research**, taxonomy-diagnose, lread-rubric | 낮음 / 중간 / 낮음 / SNS 댓글 | no |
| diagnose-and-fix (yoonmoon 리포트 `<before>`) | upstream | ko-diagnose, then ko-rewrite | ko-diagnose: scoring-and-report, taxonomy-diagnose; ko-rewrite: taxonomy-rewrite | 중간 / 낮음 / 중간 / 프로젝트 성과 보고 | no — the rewrite came from ko-rewrite in a separate section (변경률 ≈30%, 등급 B) |

## Checks (flow.md §3 P2)

| Check | Result |
|---|---|
| Output follows `<outputFormat>` (one-line verdict, evidence summary, signal table, suspect spans) | 4/4. Short mode noted its own signal rows |
| No text modified | 4/4 for ko-diagnose's report |
| ko-rewrite and ko-diagnose never read each other's references | Tool logs: yes, including the run where both fired. Grep: neither skill directory names the other's taxonomy file |
| xdac read only on the short text | Yes (1/4) |

## Differs from spec

- `<outputFormat>` lives in a reference file, not SKILL.md. 06 §7 does not say where the output contract goes; the line limit decided.
- 06 §7 lists "`taxonomy/diagnose` + 역할이 정해지지 않은 참조 3종" as ko-diagnose's references. The three now sit in role `reference` with `kind` (flow D5), and a fourth reference file (`scoring-and-report.md`) carries procedure fragments.

## Spec did not know

- **Taxonomy isolation holds per skill, not per context.** 06 §7 says the two taxonomies are never loaded into one context. Skills run in the main conversation, so a request that invokes both (diagnose-and-fix) loads `taxonomy-diagnose.md` and `taxonomy-rewrite.md` into the same context. Each skill still reads only its own files. Keeping them apart would need routing through separate agents (`korean-reviewer`, `korean-editor`, P5). Proposed for 7-review: restate §7's rule as "each skill reads only its own references; the context separation is an agent-level property (P5)". Not release-blocked: it holds without changing upstream sentences (flow §3 P2).
- **The diagnosis went beyond its scope once.** On human-academic, the report added a "문체 판정과 별개로 확인할 점" section suggesting the footnote sources be checked, and asserted from model memory that the 88만 3천 명 figure comes from another agency's survey. The fixture is synthetic (upstream README: 서지사항·인명·수치는 전부 허구), so that claim is unfounded. `<outOfScope>` lists 사실 검증; the model labeled it separate from the verdict but still made it. Upstream behavior under our rendering; recorded, not fixed.
- `katfishnet-research.md` was not read in any run, though Phase 1 says to look at its quantitative signals; the model applied them from SKILL.md's own list. Upstream's `<resources>` says "필요할 때 … 읽는다", so this is within the text.

## Temporary format friction (P4 material)

P1's shape was used unchanged. Where it did not fit:

- **Tables.** Row fragments need a table header and separator fragment each (`table-header`, `table-sep`: 24 fragments of pure structure). Anchors by heading + first cell worked; a table's identity is implicit (position under a heading).
- **Tags.** The YAML has no place for tag structure; tag lines are rendered from the parser's context, and the sidecar marks them `owner: ours` with a note. Nesting (`workflow/phase[n=1]`) exists only in the anchor string.
- **Reference role needs fields P1 lacked.** `name` and `kind` were added at file level; the slot alone does not identify a reference.
- **List markers.** P1 stripped `1. ` markers (it renumbered merged sources); P2 keeps them in the fragment text (single source, order preserved). Same shape, two conventions.
- **Horizontal rules.** `---` lines became `paragraph` fragments (6 in the taxonomy); they carry no text but need a fragment to render.
- **Anchor ordinals.** Most anchors are `paragraph N` / `item N` within a context. Stable only while upstream does not insert blocks; E2 saw yoonmoon rewrite `detect/SKILL.md` wholesale once.
- **Whole-file extraction.** For references (and effectively the taxonomy), fragmenting a file only to render it back byte-identical adds 98 fragments of bookkeeping; a file-level fragment with one hash would carry the same guarantee.

## Decisions

| # | Grade | Options (best / cheapest to reverse) | Chosen | Confidence | Basis |
|---|---|---|---|---|---|
| 1 | major | Move `<fluencyTrap>`, `<scoringRubric>`, `<outputFormat>` to one reference file / move only the first two and cut blank lines (still ~106) | All three, one file | medium-high (4/4 runs read it) | flow P1 criterion; line limit |
| 2 | major | Keep upstream paths and skill names verbatim + ours mapping notes / rename files to upstream names | Notes (same as P1 decision 1) | high (no failed read in 4 runs) | 06 §7 file names; 0 adapted |
| 3 | minor | Keep `polish-all` sentence verbatim + note / `selected` it out (loses "항상 채운다") | Keep + note | medium | instruction still useful; no sentence change |
| 4 | minor | Render tag lines as structure without upstream's indentation / reproduce indentation | No indentation | high | structure is ours; indentation carries nothing |
| 5 | minor | Whole-file references rendered by fragments / copy file with one hash | Fragments | medium | P1 shape unchanged per flow P2 step 1; the alternative recorded as friction |
| 6 | minor | Diagnose-and-fix prompt run with both skills installed / ko-diagnose alone | Both installed | high | realistic install; tests isolation |

## Subagent runs

Exploration cap: 0 of 4 used.

| # | Tier | Purpose | Tokens | Result |
|---|---|---|---|---|
| V | mid (Sonnet 5) | Verification of the done-condition (outside the cap) | _pending_ | _pending_ |

## Release-blocked

_(Updated after the verification run.)_
