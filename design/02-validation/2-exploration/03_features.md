# 03. E2 — what can be counted, what needs a reader

> Stage document. `2-exploration`, agenda item E2 (see [`02_scope.md`](02_scope.md)).
> The question: of the rules this toolkit ships, which ones can a program score, which need an LLM, and which need a person. The answer is the `features` list.
>
> A feature is a **measurement, not a verdict** (05a). A row marked `mechanical` means a number can be produced, not that a threshold is justified. Thresholds are E3's and `watch:`'s problem.

## Sources and how they were read

The rendered `dist/` text is the source, not the normalized YAML: it is what an agent actually reads, and it is what an output is judged against.

| Source | Lines | Read by |
|---|---|---|
| `output-styles/agent-reply.md`, `formal-report.md` (the policy) | 2 × ~45 | me |
| `skills/ko-rewrite/references/taxonomy-rewrite.md` | 100 | me |
| `skills/ko-diagnose/references/` — taxonomy, rubric, scoring | 395 | `mid` subagent |
| `skills/ko-grammar/references/` — rules, common-errors, guidelines | 771 | `mid` subagent |

Classification used throughout:

- **`mechanical`** — a violation is decidable by regex, counting, or morphological analysis (`kiwipiepy`: morphemes, POS tags including 조사/어미, sentence splits). The recipe has to fit in a sentence or two.
- **`llm`** — deciding needs meaning, but the verdict is well enough defined that two careful readers would usually agree.
- **`human`** — reading judgment with no stable reference.

Two further columns, because they turned out to matter more than expected:

- **`needs`** — `output-only`, or `input+output` when you must also see the text the output came from.
- **mechanical core** — several `llm` rules have a countable part that catches most cases. It is written down, but it is *not* promoted to `mechanical`. A proxy that is scored as if it were the rule is exactly how a measurement turns into a wrong verdict.

## The policy (fluent-korean)

This is the always-on layer, and therefore the one whose effect the era is measuring.

**First, a finding that narrows the work.** The two variants are nearly the same text. Diffing the rendered bodies, the substantive differences are exactly two:

- `agent-reply` has `## 추가 사항` — the subagent clause. `formal-report` does not.
- `formal-report` has the honorific block appended. `agent-reply` does not.

Everything else differs only in spacing and two words (`작업 중`/`작업중`, `문맥과 형식에 따라`/`문맥에 따라`). So **every measurable rule except the honorific one is shared by both profiles.** Measuring both profiles buys one extra feature group, not two feature sets.

| id | What it requires | Class | Procedure | Emits | Needs |
|---|---|---|---|---|---|
| coding.06 | The policy is about writing clear Korean, not about translating foreign text into Korean | — | A scope statement. Nothing to measure | n/a | — |
| coding.07 | Code-adjacent text (identifiers, comments, commit messages, log strings) follows the project's convention, not this policy | `llm` | Needs the project's convention. A proxy could only flag Hangul inside identifiers | n/a | input+output |
| coding.08 | Proper nouns and technical terms: use the settled Korean rendering, else keep the original | `llm` | Needs a glossary of what counts as settled. None exists | n/a | output-only |
| coding.09 | Do not mimic the user's tone; hold the policy's register | `mechanical` | Classify the sentence-ender class (해라체/해체/해요체/합쇼체) of the prompt and of the output from `EF` tags; emit both, and whether they match | label ×2, bool | input+output |
| coding.11a | Do not omit meaningful sentence constituents | `llm` | Semantic completeness. No surface cue | n/a | output-only |
| coding.11b | Do not overuse the genitive 조사 `~의` | `mechanical` | `JKG` count ÷ 어절 count | ratio | output-only |
| coding.12 | Do not end a sentence on a 명사구/부사구/연결어미; end on 서술어 + 종결어미. Headings and list items exempt | `mechanical` | Split sentences; drop heading lines and list items; check whether the final morpheme is `EF` | ratio | output-only |
| coding.14 | Do not drop 조사/어미; use 부사, 보조사, 선어말어미, 보조용언 | `mechanical` (proxy) | Share of 체언 not followed by any `J*` tag | ratio | output-only |
| coding.15 | Use 한자어 with 조사/어미 so that relations between words are explicit | `mechanical` (proxy) | Run length of consecutive `NN*` with no `J*` between; emit mean and max | ratio, count | output-only |
| coding.16 | Do not put a metaphorical word where an ordinary one belongs | `llm` | Needs to know which word is metaphorical *here*. A fixed list catches only the three examples given | n/a | output-only |
| coding.17 | Avoid the em dash; use a colon or a conjunction | `mechanical` | Count `U+2014` outside fenced code and quote blocks | count | output-only |
| coding.19 | Before calling a subagent with a Korean prompt, check the guidelines against it; they also apply to the relayed result | `mechanical` **if captured** | The prompt the model writes for a subagent arrives in the `Agent` tool's `PostToolUse` payload. The logger does not capture it today (see below) | ratio | — |
| honorific | Address the user as `사용자님`; use honorific endings; never 반말 | `mechanical` | (a) `사용자님` present; (b) share of sentence enders in the 합쇼체/해요체 classes | bool, ratio | output-only |

### False-positive risks worth writing down now

| Feature | Fires on correct text when |
|---|---|
| `genitive_ui_ratio` (coding.11b) | Fixed expressions and titles use `의` legitimately. The rule says "more than necessary", which a flat ratio cannot see |
| `non_ef_ending_ratio` (coding.12) | Table cells and fragments that are not markdown list items; a sentence that ends in a closing quotation mark |
| `josa_drop_ratio` (coding.14) | Compound nouns, headings, enumerations, and code identifiers quoted in prose |
| `noun_run_length` (coding.15) | Technical compounds are legitimate noun runs — the policy's own example is `토큰 카운트 함수` |
| `em_dash_count` (coding.17) | An em dash inside a quoted upstream sentence, or inside a table |
| `honorific_*` | A one-line answer has no natural place to address the user at all |

### One capture gap, worth its own line

`coding.19` is the only policy rule whose subject is not the reply. It governs **the prompt the model writes for a subagent**. That text exists in the `Agent` tool's `PostToolUse` payload, which the logger already receives — it currently reads that event only to set `edit_tools` and to count tool errors. Capturing the delegation prompt would make `coding.19` measurable and would also give the `sub-to-orchestrator` records a matching input. It is a logger change, not a research question, and it belongs in this era's spec.

## The rewrite taxonomy (im-not-ai)

61 entries, A through J. Three things stand out, and they change how much work E2's successor has.

**1. Upstream already wrote the thresholds.** 24 of the 61 carry an explicit count — `한 문단 3회+`, `문서 2회+`, `5회+`, `4문장+ 연속`. Several cite measurements: C-8 says the 대구 pattern appears in 31 of 532 human-written pieces, C-11 cites a 4.84× separation from KatFish, A-21 says the 범위 상승 pattern was found 0 times in human writing. 05a's worry was that opening `watch:` means "직감으로 숫자를 박는다" — inventing thresholds by feel. For this battery we are not inventing them; we are inheriting numbers someone derived from a corpus.

**2. Nearly all of it is countable.** Most entries are a fixed phrase or a small regex plus a density threshold.

| Shape | Count | Class |
|---|---|---|
| Fixed phrase or small regex + density threshold | ~47 | `mechanical` |
| Needs a parse or document structure — 관형구 length (A-18), consecutive bullet blocks (C-2), paragraph-initial triads (C-7), sentence-length distribution (E-1), 종결어미 runs (E-2), 경어법 mixing (E-7), 당위 at paragraph end (I-4), final-30 % position (D-11) | ~8 | `mechanical`, with sentence/paragraph segmentation |
| Countable core plus a judgment the count cannot make — 은유 beyond the fixed list (D-14), buzzword vs. standard term (B-2), abstract-subject personification (D-5), pronoun antecedent candidates (A-16), have/make/take calques (A-7) | ~6 | `llm` with a mechanical core |

**3. It is genre-bound, and the genre is not ours.** C-2 and C-5 name 칼럼-리포트 explicitly; D-13 restricts itself to 에세이; E-7 to 대화-구어. The counts were derived on published columns, not on an agent's replies in a terminal. Carrying a `문단 3회+` threshold across that gap is a transfer, not a measurement, and it has to be re-checked against our own corpus before any of it becomes a `watch:` value.

**What makes it valuable anyway:** these features are computable on *any* Korean output, whether or not `ko-rewrite` ran. They are not a measure of the skill; they are a measure of the text. That makes them a general battery for "does this read like AI Korean", which is closer to the era's actual question than the policy's own rules are.

**The `Do-NOT` zones are the real engineering.** The taxonomy excludes proper nouns, numbers and units, attributed direct quotations, legal text, mathematical notation, and industry abbreviations — and it distinguishes an attributed quotation from a rhetorical one by whether a speech marker is present. Every count above is wrong by the size of those zones unless they are excluded first. The logger's current `korean_prose()` strips fenced code and quote-prefixed lines, which is a fraction of that list.

**The missing entry.** J starts at J-2. This is the P1 finding — upstream ships 85 patterns and the generator loaded 61 — visible here as gaps at A-12/13/14/17/23, C-1/3/4/6, E-3/4/5/6, F-1/2/3/6, H-2, I-5/6, and J-1. Whether the missing 24 change the battery is an open item for the spec.

## The diagnose taxonomy, the LREAD rubric and the scoring rules

A `mid` subagent classified all three ko-diagnose references against the same scheme. 85 rows: **46 `mechanical`, 35 `llm`, 4 `human`.**

The shape of the split is more useful than the totals.

**The 11 defect categories are mostly countable, for the same reason the rewrite taxonomy is:** they name fixed phrases (번역투 `~에 대해`/`~을 통해`, 이중 피동, 결론 도입구, hype 어휘, 문두 접속사, `것이다` 종결, `-적` 연쇄, 볼드·이모지·엠대시 남용) or a distribution a tagger can compute (문장 길이 균일성, 종결어미 단조, POS n-gram diversity). Category 11 (과소 서술) is the exception and is mostly `llm` — omitted constituents, vague substitution and figurative replacement have no surface signal. The one category-11 item that *is* mechanical, 명사구·연결어미 종결, is the same measurement as the policy's `coding.12`.

**The 보존 원칙 are the most valuable rows in the whole exercise.** Eight preservation rules — proper nouns, numbers/units/dates/currency, quotations, code/identifiers/URLs/paths, register level — are `mechanical` and `input+output`: extract the tokens from both texts and compare the multisets. These are not style measurements. They are **exactly the code judgment 06 §13.1 said this era owes**: `ko.change_rate` and its companions, replacing the model's self-reported 변경률. That item can be closed here rather than deferred.

Two of the eight are not mechanical: "meaning of technical terms must not shift" is `human`, and "direction, strength, causality and quantity of claims must not flip" is `llm` with a polarity-list proxy that misses negation and modality changes.

**The LREAD rubric is almost entirely unmeasurable by code.** Of 13 items, exactly one is `mechanical` — 어문 규범, which states its own ratio (errors ÷ words) and needs an external spelling/spacing checker. Everything else (논지 명확성, 근거 적절성, 어휘 사용, 문장 구성, 글쓰기 관습) is `llm`, and 창의성 and 표현 창의성 are `human` with no stable reference. The scoring rules that aggregate these are `llm` by construction, since they take a creativity signal as an input.

**One contradiction found inside the sources.** The 보존 원칙 require register consistency between input and output. The LREAD rubric treats *unnaturally excessive* register consistency as an AI signal. The two point in opposite directions and neither states the boundary. A feature can still emit register variance; what it cannot do is carry a direction. Recorded for the spec, not resolved here.

## The grammar rules (korean-skills)

A `mid` subagent classified all three ko-grammar references. 50 rows: **22 `mechanical`, 26 `llm`, 2 `human`** — the least mechanical of the three skills, which is the opposite of what the subject matter suggests.

**Orthography looks decidable and mostly is not.** 사이시옷 and 두음법칙 are general rules over morpheme origin (고유어 / 한자어 / 외래어), and POS tags do not carry origin. Both reduce to a closed dictionary of the pairs the document happens to list, which is a proxy, not the rule. 합성어 spacing has the same shape: it needs a lexicon of what is lexicalized, and deciding "one word or two" is a meaning question.

**What is genuinely mechanical is narrow and very reliable.** 되요/됬 as banned strings; 왠 anywhere but in 왠지; 않 not preceded by -지; 조사 attached with no space; 의존명사 spaced; repeated `!!!`; quotation marks balanced by a stack parse; code spans excluded.

**One group needs no analyzer at all.** The allomorph rules — 을/를, 이/가, 은/는, 와/과, -ㅂ니다/습니다, -ㄹ까요/을까요 — are decided by whether the preceding syllable has a 받침. That is jamo arithmetic on a Hangul code point: stdlib, no dependency. The known exceptions are ㄹ-irregular stems and numerals or acronyms whose 받침 follows pronunciation rather than the glyph.

**One upstream rule has no stable target.** 주어와 서술어 호응 was classified `human` because its own worked example marks a sentence wrong and then says it is contextually fine. Korean verbs do not inflect for number or person, so the rule as written has nothing to check. Recorded as a source-quality finding, not as a feature.

**One row is infrastructure, not a rule.** `guidelines.md`'s code-block exclusion is `mechanical` and is the same machinery the rewrite taxonomy's `Do-NOT` zones need. It belongs in the shared exclusion pass, below, rather than in the feature list.

## A constraint that outranks the classification: no third-party dependency exists

Every `mechanical` row above assumes `kiwipiepy` — morphemes, POS tags, sentence splits.

`kiwipiepy` is not installed, and **era 01 took no third-party dependency at all.** There are zero non-stdlib imports across `build/`, `logger/` and `tests/`; era 01 hand-wrote `build/mini_yaml.py` rather than take PyYAML, and `build/mini_toml.py` rather than wait for `tomllib`. That was a deliberate property of the build, not an accident.

So the real question E2 hands to the spec is not which rules are countable. It is **where the counting runs.**

| | Features in the hook | Features offline |
|---|---|---|
| What the logger needs | `kiwipiepy` on the user's machine, on every turn | nothing new; it already stores the raw text |
| If the import fails | The logger swallows it and exits 0 — features silently absent | not applicable |
| `watch:` / `gate:` at runtime | possible | not possible |
| Era 01's stdlib-only property | broken | kept |
| This era's corpus | — | the corpus is generated offline anyway, so this *is* the workflow |

The offline split also matches 05a's line. The logger's job is to leave a record; deciding anything from that record is a separate program. Nothing in era 02 needs a feature value at runtime, because `gate:` is explicitly out of scope and `watch:` produces candidate values, not live ones.

This is a spec decision, not an exploration one, but E2 cannot produce a `features` list without naming it: a list written for an in-hook computation and a list written for an offline pass are different lists.

## What this means for the feature list

209 rule rows were classified across four sources. That number is misleading: **the same measurement appears under different ids in three or four places.** The em dash is `coding.17`, rewrite `J-3` and diagnose 8.3. "명사구로 문장을 끝낸다" is `coding.12`, diagnose 11.3 and part of rewrite `E-2`. `~에 대해` is rewrite `A-1` and diagnose 1.1.

So the list is organised by **measurement**, not by rule id. Each measurement cites the rules it serves; a rule can appear under several measurements.

### Tier 0 — stdlib only, output-only

Regular expressions, counting, Hangul jamo arithmetic. No analyzer, no third-party package, runs anywhere.

| Measurement | Serves | Emits |
|---|---|---|
| `em_dash_count` | coding.17, rewrite J-3, diagnose 8.3 | count |
| `emoji_count` | rewrite C-5, diagnose 8.2 | count |
| `bold_density`, `bullet_density`, `header_formula` | diagnose 8.1 / 5.2 / 5.3, rewrite C-2 / C-9 / C-10 | ratio |
| `quote_emphasis_count` | rewrite J-2, diagnose 8.4 | count |
| `phrase_battery` — one table of fixed phrases with per-entry scope (paragraph / document) and threshold | ~47 rewrite entries, diagnose categories 1–4, 6, 7, 10 | count per entry |
| `english_gloss_repeat` | rewrite B-1, diagnose 10.1 / 10.3 | count |
| `sentence_length_stats` — mean, stdev, coefficient of variation, longest | rewrite E-1, diagnose 5.4 / 9.2 | ratio |
| `paragraph_initial_repeat` — triads and repeated openers | rewrite C-7, diagnose 4.2 / 9.3 | ratio |
| `connective_comma_count` | rewrite C-11, diagnose 4.1 | count |
| `spelling_denylist` — 되요, 됬, 왠 outside 왠지, `!!!` | grammar 되/돼, 웬/왠, 느낌표 | count |
| `quote_balance` — stack parse | grammar 따옴표 혼용 | bool |
| `allomorph_errors` — 을/를, 이/가, 은/는, 와/과, -ㅂ니다/습니다, -ㄹ까요 by 받침 | grammar 조사·어미 사용 오류 | count |

### Tier 1 — needs a morphological analyzer, output-only

| Measurement | Serves | Emits |
|---|---|---|
| `non_ef_ending_ratio` — final morpheme is not `EF` | coding.12, diagnose 11.3 | ratio |
| `speech_level` — 해라체 / 해체 / 해요체 / 합쇼체 distribution | coding.09, honorific, rewrite E-7, grammar 높임법 | label, ratio |
| `josa_drop_ratio` — 체언 with no following `J*` | coding.14, diagnose 11.2 | ratio |
| `noun_run_length` — consecutive `NN*` with no `J*` between | coding.15 | count |
| `genitive_ui_ratio` — `JKG` density | coding.11b, diagnose 11.6 | ratio |
| `ending_monotony` — `EF` distribution and run length | rewrite E-2, diagnose 9.1 | ratio |
| `pos_ngram_diversity` | diagnose 9.4 (KatFishNet) | ratio |
| `adnominal_chain_depth` — `ETM` chains | rewrite A-18, diagnose 1.8 | count |
| `suffix_jeok_density` — `XSN` 적 | diagnose 7.2, rewrite F-4 / F-5 | ratio |
| `spacing_errors` — 조사 spacing, 의존명사 spacing, 부사 spacing | grammar 띄어쓰기 | count |

### Tier 2 — input and output together (the `change_rate` family)

These are the 보존 원칙 from the diagnose taxonomy. They are not style measurements: they are **the code judgment 06 §13.1 assigned to this era**, replacing the model's self-reported 변경률.

| Measurement | Needs an analyzer | Emits |
|---|---|---|
| `number_unit_date_preservation` | no — regex | bool, diff |
| `quote_preservation` | no | bool |
| `code_url_path_preservation` | no | bool |
| `proper_noun_preservation` — `NNP` multiset diff | yes | bool, diff |
| `register_preservation` — speech level of input vs output | yes | bool |
| `change_rate` — edit distance over comparable spans | no | ratio |

Two preservation rules are **not** in this tier because they are not mechanical: "the meaning of a technical term must not shift" is `human`, and "the direction, strength, causality or quantity of a claim must not flip" is `llm` with a polarity-list proxy that misses inserted negation and modality shifts.

### The prerequisite nobody can skip: the exclusion pass

Every count above is wrong by the size of the zones it failed to exclude. The sources between them name: fenced and inline code, attributed direct quotations (distinguished from rhetorical quotation by the presence of a speech marker), proper nouns, product and model names, numbers, dates, units and currency, legal text, mathematical and chemical notation, industry abbreviations, and markdown headings and list items.

The logger's `korean_prose()` today strips fenced code and quote-prefixed lines. That is two items from a list of twelve, and the rest are not decorative — the `phrase_battery` fires on quoted upstream text, `proper_noun_preservation` needs the proper-noun list it is supposed to produce, and `non_ef_ending_ratio` is meaningless without heading and list exclusion.

**The exclusion pass is the first thing to build and the first thing to validate.** It is shared by all three tiers and it is where the false positives listed throughout this document actually come from.

### What is left to `llm` and to `human`

Roughly 65 rows across the four sources need meaning: whether a constituent was omitted but recoverable, whether a word is metaphorical here, whether a term has a settled Korean rendering, whether an honorific is socially required, whether a hedge is warranted. The LREAD rubric is almost entirely in this group — of its 13 items exactly one is mechanical.

Six rows need a person: 창의성 and 표현 창의성 (no stable reference), "the meaning of a technical term must not shift", "was this text already edited by a human", 과도한 교정 피하기 (whether a colloquialism was intentional), and 주어와 서술어 호응 (whose own example contradicts itself).

E3 inherits this group. The question it has to answer is not whether an LLM can judge these — it is what agreement rate, against what reference, on how many samples, licenses using one.

### One thing this document did not do

**Nothing here was run against real text.** Every false-positive risk listed is predicted from the recipe, not measured. The first job after E2 is to implement the exclusion pass plus a handful of Tier 0 measurements and run them over the corpus — including deliberately correct Korean — to find out which of these predictions were right. A feature whose false-positive rate has never been observed is not ready to carry a `watch:` value, however well upstream documented its threshold.

## What this means for the feature list

*(pending the two reports)*

## Subagent runs

| # | Tier | Purpose | Verdict |
|---|---|---|---|
| E2-a | `mid` (Sonnet 5) | Classify the ko-diagnose references (taxonomy, rubric, scoring) | 85 rows: 46 `mechanical`, 35 `llm`, 4 `human`. Found the 보존 원칙 group, which closes 06 §13.1's change-rate item. 81.7k tokens |
| E2-b | `mid` (Sonnet 5) | Classify the ko-grammar references (rules, common-errors, guidelines) | 50 rows: 22 `mechanical`, 26 `llm`, 2 `human`. Found one upstream rule with no stable target (주어와 서술어 호응). 83.4k tokens |

Both were given the question, the sources and the classification scheme, never a leaning. Exploration runs used in this stage: 2. Total ≈165k tokens.
