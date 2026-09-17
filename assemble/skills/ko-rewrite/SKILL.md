---
name: ko-rewrite
description: Rewrites Korean text that reads as AI-written (번역투, AI 관용구, 기계적 병렬, 리듬 균일, 이모지·불릿 과다) so it reads as human-written, without changing its content. Use when the user asks to remove AI tone from Korean text — "AI 티 없애줘", "윤문해줘", "번역투 고쳐줘", "사람이 쓴 것처럼". Do not use for spelling or grammar checks, translation, adding content, or judging whether a text was written by AI.
metadata:
  provenance: SKILL.provenance.yaml
---

# ko-rewrite

@frag procedure/rewrite#intro

## Notes

- Sentences in Korean under 철칙, 절차, 자체검증 체크리스트, 등급 기준 and 옵션 are upstream (im-not-ai) and unchanged. Headings, numbering and English lines are ours.
- Where an upstream sentence says `quick-rules` or `references/quick-rules.md`, read `references/taxonomy-rewrite.md` in this skill's directory, together with the 자체검증 체크리스트 and 등급 기준 sections below.
- Upstream modes (strict 모드, 정밀 모드, `--strict`) do not exist in this skill. Do not recommend them.
- Do not write files unless the user asks. The rewritten text goes in the reply.

## 철칙

@frag procedure/rewrite#invariant.1 prefix="1. "
@frag procedure/rewrite#invariant.2 prefix="2. "
@frag procedure/rewrite#invariant.3 prefix="3. "
@frag procedure/rewrite#invariant.4 prefix="4. "
@frag procedure/rewrite#invariant.5 prefix="5. "
@frag procedure/rewrite#invariant.6 prefix="6. "
@frag procedure/rewrite#invariant.7 prefix="7. "
@frag procedure/rewrite#invariant.8 prefix="8. "
@frag procedure/rewrite#invariant.9 prefix="9. "
@frag procedure/rewrite#invariant.10 prefix="10. "

## 절차

@frag procedure/rewrite#step.1 prefix="1. "
   In this skill that file is `references/taxonomy-rewrite.md`. `references/quick-rules.md` does not exist here.
@frag procedure/rewrite#step.2 prefix="2. "
@frag procedure/rewrite#step.2.hygiene prefix="   - "
@frag procedure/rewrite#step.3 prefix="3. "
@frag procedure/rewrite#step.4 prefix="4. "
@frag procedure/rewrite#step.4.anchor prefix="   - "
@frag procedure/rewrite#step.5 prefix="5. "
@frag procedure/rewrite#step.5.anchor prefix="   - "
@frag procedure/rewrite#step.5.abort prefix="   - "
@frag procedure/rewrite#step.6 prefix="6. "
@frag procedure/rewrite#step.6.anchor prefix="   - "
7. Reply with the full rewritten text first, then these items:
@frag procedure/rewrite#reply.1 prefix="   - "
@frag procedure/rewrite#reply.2 prefix="   - "
@frag procedure/rewrite#reply.3 prefix="   - "

## 자체검증 체크리스트

@frag procedure/rewrite#check.1 prefix="1. "
@frag procedure/rewrite#check.2 prefix="2. "
@frag procedure/rewrite#check.3 prefix="3. "
@frag procedure/rewrite#check.4 prefix="4. "
@frag procedure/rewrite#check.5 prefix="5. "
@frag procedure/rewrite#check.6 prefix="6. "

## 등급 기준

@frag procedure/rewrite#grade.A prefix="- "
@frag procedure/rewrite#grade.B prefix="- "
@frag procedure/rewrite#grade.C prefix="- "
@frag procedure/rewrite#grade.D prefix="- "

## 옵션

@frag procedure/rewrite#options prefix="- "
