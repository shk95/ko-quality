---
name: ko-diagnose
description: Diagnoses whether a Korean text shows signs of AI writing and reports AI 가능성, 신뢰도, 번역문 가능성, genre and evidence, without changing the text. Use when the user asks whether Korean text was written by AI or GPT, asks for AI detection, or asks "사람이 쓴 글 맞아?" — short SNS posts and comments included. Do not use to rewrite text (that is ko-rewrite), for spelling, translation or fact-checking, or as sole evidence of plagiarism or misconduct.
metadata:
  provenance: SKILL.provenance.yaml
---

# ko-diagnose

## Notes

- Korean sentences inside the tags are upstream (yoonmoon) and unchanged. The title, tag lines and English lines are ours.
- Paths in upstream sentences: `../humanize/references/ai-tell-taxonomy.md` and `ai-tell-taxonomy.md` mean `references/taxonomy-diagnose.md`; `../humanize/references/katfishnet-research.md` means `references/katfishnet-research.md`. `references/lread-rubric.md` and `references/xdac-research.md` are as named. Links to `translationese-research.md` point to a file not included here.
- `<fluencyTrap>`, `<scoringRubric>` and `<outputFormat>` are in `references/scoring-and-report.md`. Read it before Phase 2.
- The `humanize` skill means `ko-rewrite`. `polish-all` is not part of this toolkit; still fill 번역문 가능성 and 장르.
- Do not read `ko-rewrite`'s reference files.

<role>
한글 텍스트가 LLM이 쓴 것인지 **진단**한다. 윤문(humanize) 스킬이 *고쳐 쓰는* 도구라면, 이 스킬은
*판별·설명*하는 도구다. 같은 AI 티 분류를 쓰되, 고치지 않고 **AI 가능성·신뢰도·근거**만 보고한다.
</role>

<resources>
필요할 때 아래 파일을 읽어 기준으로 삼는다.

- `references/lread-rubric.md` — 사람의 한국어 AI 글 판별 루브릭(LREAD, ACL 2025 후속). **Phase 1~2**의 판정 틀. fluency trap 경고 포함.
- `../humanize/references/ai-tell-taxonomy.md` — 11대 카테고리 AI 티 분류(탐지할 신호 목록). **Phase 1**에서 읽는다(같은 플러그인의 humanize 스킬 공유).
- `../humanize/references/katfishnet-research.md` — 정량 특징의 학술 근거(KatFishNet, ACL 2025). 가중치 판단 근거.
- `references/xdac-research.md` — **단문/SNS·댓글** AI 탐지 신호(XDAC, ACL 2025). 입력이 단문·구어체일 때만 **Phase 1-S**에서 읽는다.
</resources>

<workflow>

<phase n="0" name="입력·장르">
1. 판별할 한글 텍스트를 확보한다(붙여넣기 또는 파일).
2. 첫 ~300자로 장르를 추정한다(칼럼/리포트/블로그/공식문서/시 등). 장르는 신뢰도 보정에 쓴다.
3. **단문/SNS 게이트** — 입력이 짧고 구어체(댓글·SNS·채팅·리뷰 등 비격식 단문)면 **단문 모드**를 켠다.
   켜지면 Phase 1-S(단문 신호축)를 추가 적용한다. 문어체(칼럼·리포트·공식문서)면 켜지 않는다 — 적용 시 위양성.
</phase>

<phase n="1" name="신호 스캔">
`ai-tell-taxonomy.md`의 11대 카테고리 패턴을 스캔하고, 각 탐지의 심각도(강/중/약)와 빈도를 센다.
더해 `katfishnet-research.md` 기반 **정량 신호**를 살핀다.

- **쉼표 과용** — 연결어미·접속부사 뒤 쉼표 빈도(한국어는 본래 쉼표가 드묾). _가장 강한 신호._
- **POS·구조 다양성 저하** — 종결어미·문장 구조·문두의 단조로운 반복.
- **의존명사·보조용언 정형 반복** — "할 수 있다 / 하는 것 / 것이다"의 기계적 반복.
- **균일한 리듬** — 비슷한 길이·구조의 문장 연속.
- **과소 서술·개조식**(_약한 보조 신호_) — 성분·조사·어미 생략, 명사구·연결어미 종결, 일반 어휘를 밀어낸 비유(카테고리 11).
  요약·보고 맥락의 LLM 출력에 잦지만 사람이 쓴 메모·실무 문서에도 흔하므로 **단독 판단 금지**, 다른 신호와 겹칠 때만 가산.
- **경동사·대동사 군더더기**(_약한 보조 신호_) — '명사+을 실시/수행/진행하다'(→'명사+하다') 같은 한자어 대동사 분리(카테고리 6 번역투). 격식·공문서체 사람 글에도 흔하므로 **단독 판단 금지**, 다른 신호와 겹칠 때만 가산(`<cautions>` 참조).

이어 `references/lread-rubric.md`의 **LREAD 루브릭 3대 차원**으로 다시 본다(`<fluencyTrap>` 적용).

- **내용(Content)** — **창의성·발달적 비정형성**이 있는가. *부재*가 AI 단서, 존재가 사람 단서.
- **조직(Organization)** — 서–본–결 구조 완결성·템플릿 충실. **높을수록 오히려 AI 의심**(역설 신호).
- **표현(Expression)** — 자연스러운 우리말(번역투 단서), 어색함·중의성, 띄어쓰기·구두점 정형성,
  register 안정성이 _부자연스럽게 과도하게_ 일정한가, 페르소나(주장된 작성자 수준)와의 정합성.
</phase>

<phase n="1S" name="단문/SNS 신호 (조건부)">
**Phase 0에서 단문 모드일 때만 수행.** `references/xdac-research.md`를 읽어 단문/구어체 신호를 본다.
문어체 입력에는 적용하지 않는다.

- **반복문자 부재** — 구어 맥락인데 ㅋㅋ/ㅎㅎ/ㅠㅠ가 전무 → AI 단서(가장 강함).
- **포맷팅 부재** — 줄바꿈·이중공백이 거의 없음 → AI 단서.
- **격식·정형 과다·중립 어조** — 짧은 댓글인데 격식체·헤지 정형구("것 같다")·감정 중립.
- **길이 일관성** — 문장/댓글 길이 분산이 부자연스럽게 작음.
- **이모지·특수문자 획일성** — 유무가 아니라 표준·공통기호만 획일적으로 쓰는지(유무로 판단 금지).

**방향 주의:** 카테고리 8(시각 장식)은 문어체에서 _장식 과잉_=AI지만, 단문에서는 _포맷팅·반복문자 결핍_=AI로
**신호 방향이 반대**다. 단문 모드에서는 결핍 쪽을 본다. 개별 신호는 약하므로 **여러 축이 겹칠 때만** 가중한다.
</phase>

<phase n="2" name="점수·판정">
신호를 합산해 **AI 가능성**과 **신뢰도**를 산정한다(`<scoringRubric>`·`<fluencyTrap>`). 확정이 아니라 추정임을 유지한다.
</phase>

</workflow>

<cautions>
**단정하지 말 것.**

- 이 판별은 **확률적 추정**이다. "AI가 썼다"고 단정하지 말고 "AI 티 신호가 강하다/약하다"로 표현한다.
- **유창성 함정**(`<fluencyTrap>`)을 기억한다 — 매끄럽다고 사람, 어설프다고 AI가 아니다.
- 사람도 번역투·상투어·쉼표 습관을 쓸 수 있다. **위양성**을 항상 경계한다.
- **경동사·대동사 군더더기('~을 실시/수행/진행하다')는 약한 신호다** — 격식·보도·공문서체 사람 글에도 매우 흔하다(공공언어 가이드가 _사람의_ 과용을 교정하려 존재). 학술 1차 근거도 없고 실무·규범 처방 기반이다. **단독으로 'AI'라 판정하지 말 것** — 다축이 겹칠 때만 가산.
- **단문/SNS 축(Phase 1-S)은 단문·구어체에만** 적용한다. 문어체에 "반복문자 없으니 AI"를 들이대면 위양성이다(장르 게이트 필수).
- **이모지 유무로 판단 금지** — 사람·AI 모두 이모지를 쓴다. 신호는 사용의 *획일성/표준화 정도*지 유무가 아니다.
- 표절·부정행위·학사 징계 등 **불이익 판정의 단독 근거로 쓰지 않는다**. 보조 참고 자료일 뿐이다.
- 탐지기를 속이기 위한 용도가 아니다(그건 윤문의 목적도 아니다).
</cautions>

<outOfScope>
- 글을 사람처럼 고쳐쓰기 → **humanize** 스킬(윤문)
- 맞춤법·오탈자 교정, 번역, 사실 검증(팩트체크)
</outOfScope>
