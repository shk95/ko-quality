"""Derived fields that need the exclusion pass (09 §12.3, S2): instruction_lang, artifact_lang, usable."""
import re

from measure import exclusion

HANGUL = re.compile(r"[가-힣]")
LATIN = re.compile(r"[A-Za-z]")
USABLE_EOJEOL = 20  # >= 20 Korean 어절 after exclusion: a flag, never a filter (E2)


def lang_of(text):
    """ko | en | mixed on text after exclusion. No letters at all reads as mixed (as era 01's logger did)."""
    prose = "\n".join(exclusion.run(text).prose())
    h, l = len(HANGUL.findall(prose)), len(LATIN.findall(prose))
    if h + l == 0:
        return "mixed"
    r = h / (h + l)
    return "ko" if r >= 0.7 else "en" if r <= 0.3 else "mixed"


def korean_eojeol(text):
    prose = "\n".join(exclusion.run(text).prose())
    return sum(1 for w in prose.split() if HANGUL.search(w))


def derive(record):
    return {
        "instruction_lang": lang_of(record.get("task") or ""),
        "artifact_lang": lang_of(record.get("output") or ""),
        "usable": korean_eojeol(record.get("output") or "") >= USABLE_EOJEOL,
    }
