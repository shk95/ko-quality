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

**2. Nearly all of it is countable.** Row by row, all 61 entries:

| id | Pattern | Upstream threshold | Class | Maps to | Note |
|---|---|---|---|---|---|
| A-1 | `~에 대해(서)` | 문단 3회+ | `mechanical` | `phrase_battery` | upstream says humans use it 3× more; the default is to keep it |
| A-2 | `~를 통해/통하여` | 문단 3회+ | `mechanical` | `phrase_battery` | standard means-marker; only density is a signal |
| A-3 | `~에 있어(서)` | — (S1, any) | `mechanical` | `phrase_battery` |  |
| A-4 | `~라는 점에서` | 3회+ | `mechanical` | `phrase_battery` |  |
| A-5 | `~와 관련하여/관련된` | — | `mechanical` | `phrase_battery` |  |
| A-6 | `~에 기반하여/바탕으로` | 남발 | `mechanical` | `phrase_battery` | no number given; needs one from our corpus |
| A-7 | `가지고 있다`; have/make/take/give calques | — | `llm` | `phrase_battery` (fixed part only) | the fixed string is countable; the calque judgment is not |
| A-8 | 이중 피동 `~되어진다/~지게 된다` | — (S1, any) | `mechanical` | `phrase_battery` | also diagnose 2.1 — same measurement |
| A-9 | `~에 의해` passive | — | `mechanical` | `phrase_battery` | legitimate agentless passive in formal register |
| A-10 | `~할 수 있다` repeated | 4회+ | `mechanical` | `phrase_battery` | rule forbids converting to assertion; count only |
| A-11 | `~을 위해` purpose clause | 남발 | `mechanical` | `phrase_battery` | no number given |
| A-15 | abstract subject + 만능 동사 (보여준다/제공한다/가져온다) | — | `llm` | `phrase_battery` (verb list only) | needs to know the subject is abstract |
| A-16 | pronoun with 0 / 1 / 2+ antecedent candidates in the previous 2 sentences | — | `llm` | — | needs candidate resolution; rule says keep when unsure |
| A-18 | 관형구/관계절 of 3+ 어절 before a noun | 3어절+ | `mechanical` | `adnominal_chain_depth` | needs `ETM` chain length |
| A-19 | 이중 조사 `~에서의/~으로의/~에의/~으로부터의` | — | `mechanical` | `phrase_battery` | plain `~의` explicitly excluded |
| A-20 | `~되고 있다/~지고 있다` | 문단 3회+ | `mechanical` | `phrase_battery` | isolated use preserved |
| A-21 | `단순한 X를 넘어 Y` | — (0 in human corpus) | `mechanical` | `phrase_battery` | upstream measured 0 occurrences in human writing |
| A-22 | `~은/는 명확하다·분명하다` | — | `mechanical` | `phrase_battery` | excludes the adverb 분명히 and the verb phrase 명확히 하다 |
| A-24 | `더 이상 ~ 않다/아니다` | 문서 2회+ | `mechanical` | `phrase_battery` | injection also forbidden — needs input+output to check that half |
| B-1 | 한글 + (English) gloss repeated after first use | 매번 | `mechanical` | `english_gloss_repeat` | long documents may legitimately re-gloss |
| B-2 | ad-copy buzzwords (seamless, robust, leverage) | — | `llm` | `phrase_battery` (seed list) | distinguishing ad-copy from a standard technical term needs judgment |
| C-2 | 3+ consecutive bullet blocks | 3블록+ | `mechanical` | `bullet_density` | genre-bound: 칼럼-리포트 only |
| C-5 | emoji in list heads, headings, emphasis | 남발 | `mechanical` | `emoji_count` | genre-bound: 칼럼-리포트 only |
| C-7 | paragraph-initial 먼저–반면–결국 triad | 3단 | `mechanical` | `paragraph_initial_repeat` |  |
| C-8 | `A인가, B인가` / `A가 아니라 B` 대구 | 2회+ | `mechanical` | `phrase_battery` | 31 of 532 human pieces use it; preserve unless clustered |
| C-9 | numbered inline indexing `1) 2) 3)` | — | `mechanical` | `header_formula` |  |
| C-10 | colon-subtitle headings `X: Y` repeated | 반복 | `mechanical` | `header_formula` | real section titles in academic reports preserved |
| C-11 | comma right after a 연결어미 (-고/-며/-지만/-면서/-아서/-어서) | 6회+ = strong | `mechanical` | `comma_rate` | KatFish 4.84× separation; also diagnose 4.1 |
| D-1 | 결산 lexicon 결론적으로/따라서/이를 통해/그러므로/요약하면/정리하자면 | 3회 초과 | `mechanical` | `phrase_battery` | also diagnose 3.1 |
| D-2 | `시사하는 바가 크다/주목할 만하다/매우 중요하다` | — | `mechanical` | `phrase_battery` | also diagnose 3.2 |
| D-3 | enumeration openers `크게 세 가지로 나눌 수 있다/다음과 같은` | — | `mechanical` | `phrase_battery` |  |
| D-4 | hype 혁신적/획기적/압도적/파격적/폭발적/전례 없는 | 3회+ | `mechanical` | `phrase_battery` | also diagnose 3.4 |
| D-5 | personified abstract subject (기술이 묻는다, 시대가 부른다) | — | `llm` | — | needs to know the subject is abstract and the verb animate |
| D-6 | closing formula `~할 때입니다/~시점입니다/~할 순간입니다` | 문서 1회 이하 | `mechanical` | `phrase_battery` |  |
| D-7 | transformation formula `X에서 Y로/X을 넘어 Y로` | 문서 1회 이하 | `mechanical` | `phrase_battery` | overlaps ordinary literal from/to — diagnose flags the same ambiguity |
| D-8 | cleft `필요한/중요한 것은 ~이다`, `문제는/핵심은/관건은/답은 ~다` | — | `mechanical` | `phrase_battery` |  |
| D-9 | `(으)로 이어진다`/`~에 직결된다` + 결산용 `결국` | 문서 2회+ | `mechanical` | `phrase_battery` | injection forbidden — that half needs input+output |
| D-10 | `~하는 이유다` inverted close | 문서 1회 이하 | `mechanical` | `phrase_battery` | injection forbidden |
| D-11 | `향후/앞으로/중장기적으로` at paragraph start in the final 30 % | 위치 조건 | `mechanical` | `phrase_battery` + document position | needs document segmentation |
| D-12 | `과제도 남아 있다/한계도 분명하다/아쉬운 점도 있다` as a standalone sentence | — | `mechanical` | `phrase_battery` |  |
| D-13 | essay close `어쩌면 ~일 것이다/비로소/천천히 ~이 됐다` | — | `mechanical` | `phrase_battery` | genre-bound: 에세이 only |
| D-14 | sensory evaluation predicates 1회+; fixed dead-metaphor list (잠식·청사진·적신호…) 1회+; other conceptual metaphor 3회+; same metaphor root 3회+ | 1회+ / 3회+ | `llm` | `phrase_battery` (fixed list only) | the fixed list is countable; 'other conceptual metaphor' is not |
| E-1 | uniform sentence length, no 100+ character sentence | 100자 | `mechanical` | `sentence_len_var` | also diagnose 5.4 / 9.2 |
| E-2 | same 종결어미 4 sentences in a row; `~고 있다` auto-mapping | 4문장+ 연속 | `mechanical` | `ending_monotony` | also diagnose 9.1 |
| E-7 | mixed 경어법 levels (해라/하게/하오/해요/합쇼) in one document | 혼재 | `mechanical` | `speech_level` | dialogue/spoken genre only; collides with the register-preservation rule |
| F-4 | 한자어 -성/-적/-화 plus English -tion/-ment/-ness/-ity calques | 문서 12회+ | `mechanical` | `suffix_jeok_density` | also diagnose 7.2 |
| F-5 | `~적 N` abstract chains (전략적 함의, 실천적 기반) | 3회+ | `mechanical` | `suffix_jeok_density` |  |
| F-7 | generic policy verbs 확대·강화·개선·확보·마련·구축 + abstract-object 설계 | 밀집 | `mechanical` | `phrase_battery` | no number given |
| G-1 | repeated speculative endings `~로 보인다/~로 판단된다/~라고 여겨진다` | 반복 | `mechanical` | `phrase_battery` | also diagnose 3.3; conversion to assertion forbidden |
| G-2 | stacked hedges `~할 가능성이 있을 수 있다/~로 보여질 수 있다` | 이중~삼중 | `mechanical` | `phrase_battery` | polarity must be preserved — that check is input+output |
| G-3 | balance lexicon 양쪽 모두/두 가지 모두/장점도 있지만/신중하게/균형 | 4회+ (**실증 부족 — hold**) | `mechanical` | `phrase_battery` | upstream marks this one as insufficiently evidenced and on hold |
| H-1 | paragraph-initial conjunctions 또한/따라서/즉/나아가/아울러/게다가/더욱이 | 문단 3회+ | `mechanical` | `paragraph_initial_repeat` | also diagnose 4.2 |
| H-3 | meta openers `이는 ~/이 점에서/이 관점에서/이 말은` | 문단 3회+ | `mechanical` | `paragraph_initial_repeat` |  |
| H-4 | `즉` overuse | 문서 2회 이하 | `mechanical` | `phrase_battery` | also diagnose 4.3 |
| I-1 | `~한 것이다/~일 것이다` | 연속 3회+ | `mechanical` | `phrase_battery` | also diagnose 6.1 |
| I-2 | `주목할 점은/X은 ~라는 점에 있다` | — | `mechanical` | `phrase_battery` | also diagnose 6.3 |
| I-3 | `~다는 것이다/~다는 뜻이다` | 합산 2회 이하 | `mechanical` | `phrase_battery` |  |
| I-4 | paragraphs ending on an obligation (첫 번째 제외) | 2개+ | `mechanical` | `phrase_battery` + paragraph position | total obligation markers must stay equal — input+output |
| I-7 | `~다는 분석이다/평가다` with no cited source | — | `llm` | `phrase_battery` (ending only) | whether a source appears nearby needs reading |
| J-2 | quotation marks used for emphasis | 5회+ | `mechanical` | `quote_emphasis_count` | also diagnose 8.4 |
| J-3 | em dash used for parenthetical asides | 문장마다 | `mechanical` | `em_dash_count` | dashes already in the source are preserved — input+output for that half |

**Counts:** `mechanical` 54, `llm` 7. 44 of the 61 carry an explicit numeric threshold. 5 have a clause the count cannot check on its own, because it forbids the rewrite from *introducing* the pattern — that half is `input+output`.

Six entries are `llm`, and each has a countable core that is written down but not promoted: A-7 (the fixed string `가지고 있다`, not the calque), A-15 and D-5 (the verb list, not the abstractness of the subject), A-16 (pronoun occurrences, not antecedent candidates), B-2 (a seed buzzword list), D-14 (the fixed dead-metaphor list, not "other conceptual metaphor"), I-7 (the ending, not whether a source is nearby).

**Two entries carry upstream's own warnings.** G-3 is marked `실증 부족 — hold` in the source itself and must not be given a threshold here. E-7 (mixed 경어법) points the opposite way from the diagnose taxonomy's register-preservation rule, which is the same contradiction recorded below.

**3. It is genre-bound, and the genre is not ours.** C-2 and C-5 name 칼럼-리포트 explicitly; D-13 restricts itself to 에세이; E-7 to 대화-구어. The counts were derived on published columns, not on an agent's replies in a terminal. Carrying a `문단 3회+` threshold across that gap is a transfer, not a measurement, and it has to be re-checked against our own corpus before any of it becomes a `watch:` value.

**What makes it valuable — and the line it must not cross.** These features are computable on any Korean output, whether or not `ko-rewrite` ran. That is useful, and it is also the trap 05a named:

> `policy_on`이 `noun_ending_ratio`를 안 움직이면 … 그건 한국어 품질 엔진이 아니라 일반 문체 린터이고, 다른 프로젝트다.

The rewrite taxonomy describes patterns the **policy never undertook to change**. Running its battery against ordinary replies and finding no on/off difference would not be a finding about the policy; it would be a category error. The battery belongs to the skill layer and is compared within it.

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

**Names are inherited, not invented.** 04 §6 already named six: `comma_rate`, `pos_ngram_diversity`, `noun_ending_ratio`, `particle_absence_ratio`, `english_ratio`, `sentence_len_var`. Those names are kept for the same measurements rather than forked. `english_ratio` returns here in the form 06 §13.1 allowed — defined on the **output**, not on the context, since the system prompt is invisible to a hook and the old `context_en_ratio` was removed for that reason.

### First: which layer does a measurement belong to?

The four sources are not one layer, and the era's question is about one of them.

| Layer | Always on? | Sources | What an on/off comparison means |
|---|---|---|---|
| **policy** | yes — injected at build time into the output style and the agent definitions | `output-styles/*.md` | This is the era's question. A difference here is the policy's effect |
| **skill** | no — only when `ko-rewrite`, `ko-diagnose` or `ko-grammar` is invoked | the three `references/` sets | A difference means the skill did its job, and only in records where the skill ran |
| **agent** | only when a subagent is spawned | `agents/*.md` (the policy text again) | Same as policy, on the `sub-to-orchestrator` records |

**A measurement is compared only within the layer that was toggled.** Applying the skill layer's battery to ordinary replies and reporting "no on/off difference" would say nothing about the policy, because the policy never promised to move those patterns.

The tiers below are about *how a number is produced*. The layer is a separate attribute, and every measurement carries both.

### Second: what the control arm actually toggles

> **The logger cannot tell the arms apart yet.** It sets `policy_on` and `injection_point` from the presence of the build stamp rather than from what applied, so a run with the plugin installed and its style unselected records `policy_on: true` (E7's run). Arm B below is indistinguishable from arm C until that is fixed.

An ablation run with the plugin uninstalled removes the policy, the skills and the agents together. A difference between that and a full install cannot be attributed to any one of them.

B9's measurement supplies the missing arm at no cost. With unforced styles, the plugin can be installed while its style is simply not selected:

| Arm | Policy | Skills and agents |
|---|---|---|
| A | — | — |
| B — **only possible under B9** | — | present |
| C | present | present |

**B minus C is the policy's own effect.** A minus B is the skills'. Under the build as it stands only A and C exist, so era 02 would measure the toolkit, not the policy — which is not the question the concept asked.

This makes B9 a prerequisite for E1's corpus design, not just a packaging preference. It is recorded in [`02_scope.md`](02_scope.md) as a spec decision; this is the reason it cannot be deferred past `4-plan`.

**All three arms run with the gate off**, because `gate:` is not opened this era. E6 adds a second dimension — `policy {on, off} × gate {on, off}` — and the era that opens `gate:` inherits arms A–C as its gate-off column ([`07_gate.md`](07_gate.md)).

### Third: the `usable` flag sits on top of the defect

The logger marks a record `usable: false` when the reply has fewer than 20 Korean 어절 after stripping code and quoted lines. It does not drop the record.

That flag sits directly on the defect being measured. 전보체 — dropped 조사 and 어미, noun-phrase endings — is what `coding.12` and `coding.14` target, and a reply written that way is short. 05a's second leak gate is exactly this shape:

> `filter.py`가 features를 읽는다 … 재려는 변수로 표본을 거른다.

**Observed, not predicted** (E7's run, five records): `usable` was `false` on three of five, and all three were short, correct Korean answers to a short question. The floor excludes ordinary replies, not only defective ones.

Nothing filters on `usable` today, so the gate is closed. **The rule this era adds: the analysis must not drop `usable: false` records for any measurement whose defect makes text shorter.** If a length floor is needed at all, it is applied per measurement with a stated reason, never as a blanket filter, and the count of excluded records is reported alongside the result.

### Fourth: reply length versus document thresholds

Upstream's thresholds assume a document: `한 문단 3회+`, `문서 2회+`, `5회+`, `4문장+ 연속`. An agent's reply is often two or three sentences, and a threshold of three per paragraph cannot fire in it at all.

The consequence is not that the counts are wrong. It is that **most of them will be zero on most records, and a feature with no variance cannot show an on/off difference** however real the underlying effect is. The same five records bear this out: replies of one or two sentences, on which a `문단 3회+` threshold cannot fire at all. This is more fundamental than the genre-transfer problem noted above, and it applies to the whole `phrase_battery`.

Two ways out, both for the spec: emit raw counts and rates per 100 어절 rather than threshold verdicts, and aggregate across records within a stratum instead of deciding per record. Neither is chosen here.

### Tier 0 — stdlib only, output-only

Regular expressions, counting, Hangul jamo arithmetic. No analyzer, no third-party package, runs anywhere.

| Measurement | Serves | Emits |
|---|---|---|
| `em_dash_count` | coding.17, rewrite J-3, diagnose 8.3 | count |
| `emoji_count` | rewrite C-5, diagnose 8.2 | count |
| `bold_density`, `bullet_density`, `header_formula` | diagnose 8.1 / 5.2 / 5.3, rewrite C-2 / C-9 / C-10 | ratio |
| `quote_emphasis_count` | rewrite J-2, diagnose 8.4 | count |
| `phrase_battery` — one table of fixed phrases with per-entry scope (paragraph / document) and threshold | ~47 rewrite entries, diagnose categories 1–4, 6, 7, 10 | count per entry |
| `english_ratio` (04 §6) — Latin characters as a share of the prose, **defined on the output**, not on the context | coding.08, diagnose 10.2 | ratio |
| `english_gloss_repeat` | rewrite B-1, diagnose 10.1 / 10.3 | count |
| `sentence_len_var` (04 §6) — mean, stdev, coefficient of variation, longest | rewrite E-1, diagnose 5.4 / 9.2 | ratio |
| `paragraph_initial_repeat` — triads and repeated openers | rewrite C-7, diagnose 4.2 / 9.3 | ratio |
| `comma_rate` (04 §6) — overall, plus the connective-ending case | rewrite C-11, diagnose 4.1, grammar 과도한 쉼표 | ratio, count |
| `spelling_denylist` — 되요, 됬, 왠 outside 왠지, `!!!` | grammar 되/돼, 웬/왠, 느낌표 | count |
| `quote_balance` — stack parse | grammar 따옴표 혼용 | bool |
| `allomorph_errors` — 을/를, 이/가, 은/는, 와/과, -ㅂ니다/습니다, -ㄹ까요 by 받침 | grammar 조사·어미 사용 오류 | count |

### Tier 1 — needs a morphological analyzer, output-only

> **Verified** (kiwipiepy 0.23.2 on Python 3.9.6, [`tests/runs/02-E2/kiwipiepy-recipes.json`](../../../tests/runs/02-E2/kiwipiepy-recipes.json)). All twenty tags this document names exist and mean what it assumed. One caution nothing here said: irregular stems carry subtype tags (`VV-I`, `VV-R`), so `tag == "VV"` silently misses them and prefix matching is required.
>
> **The tagset was fine. Two of the recipes were not.** They were run against correct Korean, telegraphic Korean and markdown, and the results are below. Both bugs are fixable and both fixes are specified.

### `noun_ending_ratio` — as written it fires on everything

kiwipiepy emits sentence-final punctuation as a trailing `SF` morpheme **after** the `EF` token: `이 기능은 값을 검증합니다.` ends `['XSV', 'EF', 'SF']`. A literal "is the final morpheme `EF`" test is therefore false for every period-terminated sentence in the language.

| | Correct prose | Telegraphic | Separation |
|---|---|---|---|
| As written | 1.00 | 1.00 | **0.00** |
| Popping trailing `SF`/`SP`/`SS`/`SE`/`SO`/`SW` first | **0.00** | **1.00** | **1.00** |

Unfixed it separates nothing. Fixed it separates perfectly on this corpus, which makes it the strongest measurement in the battery — and it was one line from being useless.

### `particle_absence_ratio` — the recipe counts the wrong nouns

`N + XSV` — the 하다 verbalizing suffix — puts a non-`J*` tag directly after the noun, and that is *the* dominant verb-formation pattern in formal Korean. Correct prose scored **0.50**; correct honorific prose scored **0.80**, because `XSN` (님) also sits between a noun and its particle: `사용자님께서` is `사용자/NNG 님/XSN 께서/JKS`.

Every noun flagged in the correct sample — 입력, 검증, 저장, 실패, 표시, 중단 — was a verb stem, not a dropped 조사.

| Variant | Correct (mean) | Defective (mean) | Gap |
|---|---|---|---|
| As written | 0.66 | 0.94 | +0.28 |
| Skip `XSN`/`XSM` when looking ahead | 0.59 | 0.94 | +0.35 |
| **Also drop verbalized 체언 from the denominator** | **0.17** | **0.96** | **+0.79** |

The third variant is the right one and the reason is not a tuning choice: **a 체언 followed by `XSV`/`XSA` is a verb stem, not a noun awaiting a particle**, so it does not belong in the denominator at all. With it, the two classes stop overlapping — correct 0.00–0.40, defective 0.88–1.00.

The residual is the false positive this document predicted: the technical-compound sample sits at 0.40, the closest of the correct cases to the defective range. Predicted, and now measured.

### Three more things the recipes did not say

- **The exclusion pass runs on raw text lines *before* the sentence splitter, not after.** kiwipiepy's splitter is paragraph-aware and knows nothing of markdown: consecutive bullets merge into one "sentence" and a three-line table into another, after which individual lines cannot be attributed back. This document's phrasing implied the reverse order and was wrong.
- **`noun_run_length`'s "no `J*` between" is ambiguous** — strict consecutive `NN*` versus bridging over intervening non-noun, non-particle tags give very different numbers. Undecided; the spec has to pick one.
- **`genitive_ui_ratio`'s predicted false positive is still untested.** No test case contained 의 at all, so the prediction is neither confirmed nor refuted.

| Measurement | Serves | Emits |
|---|---|---|
| `noun_ending_ratio` (04 §6) — final morpheme is not `EF` | coding.12, diagnose 11.3 | ratio |
| `speech_level` — 해라체 / 해체 / 해요체 / 합쇼체 distribution | coding.09, honorific, rewrite E-7, grammar 높임법 | label, ratio |
| `particle_absence_ratio` (04 §6) — 체언 with no following `J*` | coding.14, diagnose 11.2 | ratio |
| `noun_run_length` — consecutive `NN*` with no `J*` between | coding.15 | count |
| `genitive_ui_ratio` — `JKG` density | coding.11b, diagnose 11.6 | ratio |
| `ending_monotony` — `EF` distribution and run length | rewrite E-2, diagnose 9.1 | ratio |
| `pos_ngram_diversity` (04 §6) | diagnose 9.4 (KatFishNet) | ratio |
| `adnominal_chain_depth` — `ETM` chains | rewrite A-18, diagnose 1.8 | count |
| `suffix_jeok_density` — `XSN` 적 | diagnose 7.2, rewrite F-4 / F-5 | ratio |
| `spacing_errors` — 조사 spacing, 의존명사 spacing, 부사 spacing | grammar 띄어쓰기 | count |

### Tier 2 — input and output together (the `change_rate` family)

These are the 보존 원칙 from the diagnose taxonomy, plus one row that is not.

**The 보존 원칙 give `ko.preserve`** (04 §6): extract the protected kinds from both texts and compare the sets. Mechanical, and ready.

**`ko.change_rate` is a different capability and is not specified here.** 04 §6 lists it separately — `before, after, preserve_spans → ratio`, 형태소 단위, with preserved spans excluded from the denominator — and `gate` takes both as separate conjuncts. A quantity of change is not a set of invariants; the preservation extraction is an *input* to the ratio, not a replacement for it. An earlier draft of this table listed `change_rate` as needing no analyser and treated the two as one obligation. Both were wrong. See [`05_approximations.md`](05_approximations.md) item 8.

| Measurement | Needs an analyzer | Emits |
|---|---|---|
| `number_unit_date_preservation` | no — regex | bool, diff |
| `quote_preservation` | no | bool |
| `code_url_path_preservation` | no | bool |
| `proper_noun_preservation` — `NNP` multiset diff | yes | bool, diff |
| `register_preservation` — speech level of input vs output | yes | bool |
| `change_rate` — see below; **not specified** | **yes** — 04 §6 says 형태소 단위 | ratio |

**These measurements need a pair, and the record usually does not have one.** The logger stores `task` (the user's prompt) and `output` (the reply). When the user pastes the text to be rewritten into the prompt, the original is in `task` and the pair exists. When the model read the text from a file, the original never enters the record, and every measurement in this tier is unavailable. So Tier 2 is measurable on **paste-in-prompt cases only** unless the logger starts capturing the read. That is a corpus-design constraint — the prompt set has to include paste-in cases deliberately — and it is also why `ko.change_rate` can be built here but cannot be evaluated on arbitrary records.

Two preservation rules are **not** in this tier because they are not mechanical: "the meaning of a technical term must not shift" is `human`, and "the direction, strength, causality or quantity of a claim must not flip" is `llm` with a polarity-list proxy that misses inserted negation and modality shifts.

### The prerequisite nobody can skip: the exclusion pass

Every count above is wrong by the size of the zones it failed to exclude. The sources between them name: fenced and inline code, attributed direct quotations (distinguished from rhetorical quotation by the presence of a speech marker), proper nouns, product and model names, numbers, dates, units and currency, legal text, mathematical and chemical notation, industry abbreviations, and markdown headings and list items.

The logger's `korean_prose()` today strips fenced code and quote-prefixed lines. That is two items from a list of twelve, and the rest are not decorative — the `phrase_battery` fires on quoted upstream text, `proper_noun_preservation` needs the proper-noun list it is supposed to produce, and `non_ef_ending_ratio` is meaningless without heading and list exclusion.

**The exclusion pass is the first thing to build and the first thing to validate.** It is shared by all three tiers and it is where the false positives listed throughout this document actually come from.

### What is left to `llm` and to `human`

Roughly 65 rows across the four sources need meaning: whether a constituent was omitted but recoverable, whether a word is metaphorical here, whether a term has a settled Korean rendering, whether an honorific is socially required, whether a hedge is warranted. The LREAD rubric is almost entirely in this group — of its 13 items exactly one is mechanical.

Six rows need a person: 창의성 and 표현 창의성 (no stable reference), "the meaning of a technical term must not shift", "was this text already edited by a human", 과도한 교정 피하기 (whether a colloquialism was intentional), and 주어와 서술어 호응 (whose own example contradicts itself).

E3 inherits this group. The question it has to answer is not whether an LLM can judge these — it is what agreement rate, against what reference, on how many samples, licenses using one.

**E2 owes E3 the reference.** A judge is scored against something. The candidates are the measurements whose recipe leaves no room for interpretation, so that a disagreement is the judge's fault and not the metric's:

| Candidate reference | Why it qualifies |
|---|---|
| `em_dash_count` | A character count. C3 already used it and it separated the arms |
| honorific: `사용자님` present | A string test. C3 used it and it separated the arms |
| `speech_level` | A closed classification over sentence enders, once the tagset is verified |
| `allomorph_errors` | Jamo arithmetic with two named exception classes |
| `spelling_denylist` (되요, 됬, 왠 outside 왠지) | Closed banned-string list |
| `quote_balance` | A stack parse with one answer |

The rest are not reference material: a ratio with a false-positive class attached cannot adjudicate a judge, because a disagreement is then ambiguous between the two.

### One thing this document did not do

**Most of this was never run against real text.** Two Tier 1 measurements have now been (above), and the result argues for doing the rest: the tagset assumption held, and the recipes built on it were broken in ways no amount of reading would have found. Every remaining false-positive risk listed is predicted from the recipe, not measured. The first job after E2 is to implement the exclusion pass plus a handful of Tier 0 measurements and run them over the corpus — including deliberately correct Korean — to find out which of these predictions were right. A feature whose false-positive rate has never been observed is not ready to carry a `watch:` value, however well upstream documented its threshold.

## What this means for the feature list

*(pending the two reports)*

## Subagent runs

| # | Tier | Purpose | Verdict |
|---|---|---|---|
| E2-a | `mid` (Sonnet 5) | Classify the ko-diagnose references (taxonomy, rubric, scoring) | 85 rows: 46 `mechanical`, 35 `llm`, 4 `human`. Found the 보존 원칙 group, which closes 06 §13.1's change-rate item. 81.7k tokens |
| E2-b | `mid` (Sonnet 5) | Classify the ko-grammar references (rules, common-errors, guidelines) | 50 rows: 22 `mechanical`, 26 `llm`, 2 `human`. Found one upstream rule with no stable target (주어와 서술어 호응). 83.4k tokens |
| E2-c | `docs` (`claude-code-guide`) | Where Claude Code reads agent definitions from, and what `--scope` scopes (its undocumented answers were then measured, `tests/runs/02-E7/`) | Five locations, project `.claude/agents/` documented and meant for version control. Plugin agent namespacing and whether `--scope` limits visibility are **undocumented**. 39.7k tokens |

E2-a and E2-b were given the question, the sources and the classification scheme, never a leaning. **This document used four runs** (E2-a, E2-b, E2-c, E2-v); the stage's running total is in [`README.md`](README.md).
