---
name: ko-diagnose
description: Diagnoses whether a Korean text shows signs of AI writing and reports AI 가능성, 신뢰도, 번역문 가능성, genre and evidence, without changing the text. Use when the user asks whether Korean text was written by AI or GPT, asks for AI detection, or asks "사람이 쓴 글 맞아?" — short SNS posts and comments included. Do not use to rewrite text (that is ko-rewrite), for spelling, translation or fact-checking, or as sole evidence of plagiarism or misconduct.
---

## Notes

- Korean sentences inside the tags are upstream (yoonmoon) and unchanged. The title, tag lines and English lines are ours.
- Paths in upstream sentences: `../humanize/references/ai-tell-taxonomy.md` and `ai-tell-taxonomy.md` mean `references/taxonomy-diagnose.md`; `../humanize/references/katfishnet-research.md` means `references/katfishnet-research.md`. `references/lread-rubric.md` and `references/xdac-research.md` are as named. Links to `translationese-research.md` point to a file not included here.
- `<fluencyTrap>`, `<scoringRubric>` and `<outputFormat>` are in `references/scoring-and-report.md`. Read it before Phase 2.
- The `humanize` skill means `ko-rewrite`. `polish-all` is not part of this toolkit; still fill 번역문 가능성 and 장르.
- Do not read `ko-rewrite`'s reference files.
