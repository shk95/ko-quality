---
name: ko-rewrite
description: Rewrites Korean text that reads as AI-written (번역투, AI 관용구, 기계적 병렬, 리듬 균일, 이모지·불릿 과다) so it reads as human-written, without changing its content. Use when the user asks to remove AI tone from Korean text — "AI 티 없애줘", "윤문해줘", "번역투 고쳐줘", "사람이 쓴 것처럼". Do not use for spelling or grammar checks, translation, adding content, or judging whether a text was written by AI.
---

## Notes

- Sentences in Korean under 철칙, 절차, 자체검증 체크리스트, 등급 기준 and 옵션 are upstream (im-not-ai) and unchanged. Headings, numbering and English lines are ours.
- Where an upstream sentence says `quick-rules` or `references/quick-rules.md`, read `references/taxonomy-rewrite.md` in this skill's directory, together with the 자체검증 체크리스트 and 등급 기준 sections below.
- Upstream modes (strict 모드, 정밀 모드, `--strict`) do not exist in this skill. Do not recommend them.
- Do not write files unless the user asks. The rewritten text goes in the reply.

## Reply

Reply with the full rewritten text first, then these items:
