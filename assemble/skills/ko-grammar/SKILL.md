---
name: ko-grammar
description: Checks Korean text for spelling, spacing, grammar and punctuation errors against standard Korean rules and explains each correction. Use when the user asks to proofread Korean or check 맞춤법, 띄어쓰기, 문법 or 문장 부호. Do not use to remove AI-writing tone (that is ko-rewrite), to judge whether a text was written by AI (ko-diagnose), or to translate.
metadata:
  provenance: SKILL.provenance.yaml
---

# ko-grammar

## Notes

- Korean sentences and section headings are upstream (korean-skills grammar-checker) and unchanged. The title and English lines are ours.
- The result format (4단계), 중요 지침 and 특수 상황 처리 are in `references/guidelines.md`. Read it before step 2.
- `references/rules.md` and `references/common-errors.md` are the reference documents step 3 names.
- Do not write files unless the user asks. Corrections go in the reply.

@blocks procedure/grammar select=["## 소개","### 1단계","### 2단계","### 3단계","## 최종 확인사항"] blanks=single headings=anchor
