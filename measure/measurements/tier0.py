"""Tier 0 measurements (09 §15.4): standard library only, on the output after the exclusion pass.

Every function takes an exclusion Result and returns a number or a small dict of numbers. Nothing here applies a threshold:
upstream thresholds live in data/phrase_battery.json as data (09 §15.1).
"""
import json
import re
import statistics
from pathlib import Path

from measure import exclusion

DATA = Path(__file__).resolve().parent.parent / "data"
HANGUL = re.compile(r"[가-힣]")
LATIN = re.compile(r"[A-Za-z]")
PROSE = ("paragraph", "heading", "list_item")          # table rows are left out where a table is a known false positive
ALL_PROSE = ("paragraph", "heading", "list_item", "table_row")
EMOJI = re.compile("[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF"
                   "\U0001F1E6-\U0001F1FF☀-⛿✀-➿⭐⬆⬇⬅➡⤴⤵〰〽]")
BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*|__(?=\S)(.+?)(?<=\S)__")
SENTENCE_END = re.compile(r"(?<=[.?!。])\s+|(?<=[다요죠음함임됨까])\s*\n|\n")
CONNECTIVE_COMMA = re.compile(r"[가-힣]*(?:고|며|지만|면서|아서|어서|는데|니까|으나|거나)\s?,")
CONJUNCTION_COMMA = re.compile(r"(?:^|(?<=\s))(?:그리고|하지만|또한|그러나|따라서|그래서|즉|게다가|더욱이)\s?,")
FORMULAIC_HEADINGS = {"서론", "본론", "결론", "개요", "요약", "마무리", "들어가며", "나가며", "맺음말"}
GLOSS = re.compile(r"[가-힣]{1,20}\s?\(\s?([A-Za-z][A-Za-z .&/-]{1,60})\)")
TRIAD = ("먼저", "반면", "결국")
DENYLIST = {"되요": re.compile(r"되요"), "됬": re.compile(r"됬"), "왠 (outside 왠지)": re.compile(r"왠(?!지)"), "!!!": re.compile(r"!{3,}")}

# 받침 arithmetic (E3 scope: ㄹ-irregular stems, and numerals or acronyms whose 받침 follows pronunciation, are out of scope;
# the exclusion pass removes numbers and abbreviations, so a particle left standing alone is not counted)
LEXICAL_EXCEPTIONS = {
    "을": {"가을", "마을", "노을", "고을", "이을", "지을", "나을", "부을", "그을", "저을", "잇을"},
    "은": {"지은", "나은", "부은", "이은", "그은", "저은"},
    "과": {"사과", "효과", "교과", "부과", "초과", "치과", "외과", "내과", "제과", "모과", "대과", "오과", "비과", "세과"},
    "을까요": {"지을까요", "나을까요", "부을까요", "이을까요"},
}


def eojeol(res, kinds=ALL_PROSE):
    return sum(len(line.split()) for line in res.prose(kinds))


def per100(n, words):
    return round(100.0 * n / words, 4) if words else None


def em_dash_count(res):
    n = sum(line.count("—") for line in res.prose(PROSE))
    return {"count": n, "per_100_eojeol": per100(n, eojeol(res))}


def emoji_count(res):
    n = sum(len(EMOJI.findall(line)) for line in res.prose(ALL_PROSE))
    return {"count": n, "per_100_eojeol": per100(n, eojeol(res))}


def bold_density(res):
    text_lines = res.prose(ALL_PROSE, zones=("code", "url_path_id"))
    n = sum(len(BOLD.findall(line)) for line in text_lines)
    return {"count": n, "per_100_eojeol": per100(n, eojeol(res))}


def bullet_density(res):
    kinds = [k for _, _, k in res.lines if k not in ("blank", "code")]
    items = kinds.count("list_item")
    return {"list_items": items, "lines": len(kinds), "ratio": round(items / len(kinds), 4) if kinds else None}


def header_formula(res):
    heads = [exclusion.HEADING.sub("", res.text[s:e]).strip() for s, e, k in res.lines if k == "heading"]
    colon = sum(1 for h in heads if re.search(r"\S\s*:\s+\S", h))
    formulaic = sum(1 for h in heads if re.sub(r"^[\dIVX.\s]+", "", h).strip() in FORMULAIC_HEADINGS)
    return {"headings": len(heads), "colon_subtitle": colon, "formulaic": formulaic,
            "ratio": round((colon + formulaic) / len(heads), 4) if heads else None}


def quote_emphasis_count(res):
    return {"count": len(res.spans["rhetorical_quote"])}


def english_ratio(res):
    prose = "\n".join(res.prose(ALL_PROSE))
    h, l = len(HANGUL.findall(prose)), len(LATIN.findall(prose))
    return {"latin": l, "hangul": h, "ratio": round(l / (h + l), 4) if h + l else None}


def english_gloss_repeat(res):
    """B-1: a term glossed again after its first gloss. The first gloss of a term is upstream's correct form, so `count` is
    repeats only; `glosses` is every 한글(English) gloss, and `terms` the distinct glossed terms (keyed by the English)."""
    lines = res.prose(ALL_PROSE, zones=("code", "url_path_id", "quotation", "number"))
    seen, glosses, repeats = set(), 0, 0
    for line in lines:
        for m in GLOSS.finditer(line):
            key = " ".join(m.group(1).lower().split())
            glosses += 1
            repeats += key in seen
            seen.add(key)
    return {"count": repeats, "glosses": glosses, "terms": len(seen)}


def sentences(res, kinds=("paragraph", "list_item")):
    out = []
    for line in res.prose(kinds):
        for s in re.split(r"(?<=[.?!。])\s+", line):
            s = s.strip()
            if HANGUL.search(s):
                out.append(s)
    return out


def sentence_len_var(res):
    lens = [len(s) for s in sentences(res, ("paragraph",))]
    if not lens:
        return {"n": 0, "mean": None, "stdev": None, "cv": None, "max": None}
    mean = statistics.mean(lens)
    sd = statistics.pstdev(lens) if len(lens) > 1 else 0.0
    return {"n": len(lens), "mean": round(mean, 4), "stdev": round(sd, 4), "cv": round(sd / mean, 4) if mean else None, "max": max(lens)}


def paragraphs(res):
    """Blocks of consecutive paragraph lines, as prose text."""
    blocks, cur = [], []
    prose_iter = iter(res.prose(("paragraph",)))
    for _, _, kind in res.lines:
        if kind == "paragraph":
            cur.append(next(prose_iter))
        elif cur:
            blocks.append(" ".join(cur)); cur = []
    if cur:
        blocks.append(" ".join(cur))
    return [b for b in blocks if b.strip()]


def paragraph_initial_repeat(res):
    openers = [b.split()[0] for b in paragraphs(res)]
    seen, repeated = set(), 0
    for o in openers:
        repeated += o in seen
        seen.add(o)
    triad = int(all(any(o.startswith(t) for o in openers) for t in TRIAD))
    return {"paragraphs": len(openers), "repeated_openers": repeated,
            "ratio": round(repeated / len(openers), 4) if openers else None, "triad_먼저_반면_결국": triad}


def comma_rate(res):
    sents = sentences(res)
    text = "\n".join(res.prose(("paragraph", "list_item")))
    commas = text.count(",")
    return {"commas": commas, "sentences": len(sents), "per_sentence": round(commas / len(sents), 4) if sents else None,
            "after_connective": len(CONNECTIVE_COMMA.findall(text)) + len(CONJUNCTION_COMMA.findall(text))}


def spelling_denylist(res):
    text = "\n".join(res.prose(ALL_PROSE))
    counts = {k: len(p.findall(text)) for k, p in DENYLIST.items()}
    return {"count": sum(counts.values()), "by_item": counts}


PAIRS = {"“": "”", "‘": "’", "「": "」", "『": "』"}


def quote_balance(res):
    """True when every curly or corner quote closes in order and straight double quotes are even, per line."""
    for line in res.prose(ALL_PROSE, zones=("code", "url_path_id")):
        stack = []
        for ch in line:
            if ch in PAIRS:
                stack.append(PAIRS[ch])
            elif ch in PAIRS.values():
                if not stack or stack.pop() != ch:
                    return {"balanced": False}
        if stack or line.count('"') % 2:
            return {"balanced": False}
    return {"balanced": True}


def has_batchim(syllable):
    code = ord(syllable) - 0xAC00
    return 0 <= code <= 11171 and code % 28 != 0


def batchim_is_rieul(syllable):
    code = ord(syllable) - 0xAC00
    return 0 <= code <= 11171 and code % 28 == 8


ALLOMORPH_RULES = [
    # (kind, suffix, error when the preceding syllable has 받침?)  True: error after 받침; False: error after no 받침
    ("을까요", "을까요", False),
    ("습니다", "습니다", False),
    ("를", "를", True),
    ("을", "을", False),
    ("은", "은", False),
    ("와", "와", True),
    ("과", "과", False),
]
NOT_COUNTED = "이/가 and 는: lexical words (국가, 평가, 아이) and verbal endings (먹는, 있는) make them ambiguous without an analyser"


def allomorph_errors(res):
    counts = {k: 0 for k, _, _ in ALLOMORPH_RULES}
    for line in res.prose(ALL_PROSE):
        for token in line.split():
            word = re.sub(r"[^가-힣]+$", "", token)
            for kind, suffix, after_batchim in ALLOMORPH_RULES:
                if not word.endswith(suffix) or len(word) <= len(suffix):
                    continue
                prev = word[-len(suffix) - 1]
                if word in LEXICAL_EXCEPTIONS.get(kind, ()) or not HANGUL.match(prev):
                    break
                if kind in ("을까요", "습니다") and batchim_is_rieul(prev):
                    break      # ㄹ-irregular stems: out of scope (E3)
                if has_batchim(prev) == after_batchim:
                    counts[kind] += 1
                break
    return {"count": sum(counts.values()), "by_kind": counts, "not_counted": NOT_COUNTED}


def honorific_address(res):
    return {"present": any("사용자님" in line for line in res.prose(ALL_PROSE, zones=("code", "url_path_id")))}


_BATTERY = None


def battery():
    global _BATTERY
    if _BATTERY is None:
        data = json.loads((DATA / "phrase_battery.json").read_text(encoding="utf-8"))
        for e in data["entries"]:
            e["_re"] = re.compile(e["pattern"])
        _BATTERY = data
    return _BATTERY


def _matches(entry, text):
    n = 0
    for m in entry["_re"].finditer(text):
        if entry["anchor"] == "sentence_start":
            before = text[:m.start()].rstrip(" ")
            if before and before[-1] not in ".?!\n":
                continue
        if entry["id"] == "rewrite.A-10" and not batchim_is_rieul(m.group(1)):
            continue
        n += 1
    return n


def phrase_battery(res):
    data = battery()
    paras = paragraphs(res) + [line for line in res.prose(("list_item", "table_row", "heading"))]
    document = "\n".join(paras)
    out = {}
    for e in data["entries"]:
        count = _matches(e, document)
        row = {"count": count}
        if e["scope"] == "paragraph":
            row["max_per_paragraph"] = max((_matches(e, p) for p in paras), default=0)
        out[e["id"]] = row
    return {"version": data["version"], "entries": out, "total": sum(r["count"] for r in out.values())}


# name, function, layer(s), tier  (09 §15.4 Tier 0)
MEASUREMENTS = [
    ("em_dash_count", em_dash_count, ("policy", "skill"), 0),
    ("emoji_count", emoji_count, ("skill",), 0),
    ("bold_density", bold_density, ("skill",), 0),
    ("bullet_density", bullet_density, ("skill",), 0),
    ("header_formula", header_formula, ("skill",), 0),
    ("quote_emphasis_count", quote_emphasis_count, ("skill",), 0),
    ("phrase_battery", phrase_battery, ("skill", "policy"), 0),
    ("english_ratio", english_ratio, ("policy",), 0),
    ("english_gloss_repeat", english_gloss_repeat, ("skill",), 0),
    ("sentence_len_var", sentence_len_var, ("skill",), 0),
    ("paragraph_initial_repeat", paragraph_initial_repeat, ("skill",), 0),
    ("comma_rate", comma_rate, ("skill",), 0),
    ("spelling_denylist", spelling_denylist, ("skill",), 0),
    ("quote_balance", quote_balance, ("skill",), 0),
    ("allomorph_errors", allomorph_errors, ("skill",), 0),
    ("honorific_address", honorific_address, ("policy",), 0),
]
