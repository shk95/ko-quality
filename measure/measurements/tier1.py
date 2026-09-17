"""Tier 1 measurements (09 §15.4): the morphological analyser, on the output after the exclusion pass.

The analyser runs once per prose line inside the exclusion pass (raw lines, before sentence splitting: E2), and its
sentences are kept on the Result. A token is `excluded` when any of its characters lies in a removed zone (code, paths,
numbers, proper nouns, ...): it is never counted as a subject, and a judgment that depends on it is left undetermined.

Sentences are read from paragraph lines only. coding.12 exempts headings and lists, and a list item's telegraphic form is
a format choice that bullet_density already measures. Tags are matched by prefix (VV-I, VV-R). Nothing here applies a
threshold (09 §15.1).
"""
import re
from collections import Counter

from measure import analyser
from measure.measurements.tier0 import eojeol, per100

S_TRAIL = ("SF", "SP", "SS", "SE", "SO", "SW", "W_EMOJI")   # 09 §15.4: pop trailing punctuation before testing EF
CHEEON = ("NNG", "NNP", "NNB", "NP", "NR")                  # 체언
NOUN_RUN = ("NNG", "NNP", "NNB")                           # NN*: noun_run_length is strict
EF_NOMINAL = ("ᆷ", "음")                                    # F15: 개조식 -함/-음 tagged EF counts as a noun ending
HANGUL = re.compile(r"[가-힣]")
SPEECH_LEVELS = ("hapsyo", "haeyo", "haera", "hae")


def _ctx(res):
    ctx = getattr(res, "_tier1", None)
    if ctx is None:
        mask = res.removed_mask()
        sents = []
        for s, e, kind in res.lines:
            if kind == "paragraph" and (s, e) in res.analysis:
                for sent in res.analysis[(s, e)]:
                    toks = [(t, any(mask[t.start:t.end])) for t in sent]
                    if any(not x and HANGUL.search(t.form) for t, x in toks):
                        sents.append(toks)
        ctx = res._tier1 = {"mask": mask, "sentences": sents}
    return ctx


def _content(sent):
    """The sentence without trailing punctuation and symbols."""
    toks = list(sent)
    while toks and analyser.is_tag(toks[-1][0].tag, *S_TRAIL):
        toks.pop()
    return toks


def ratio(n, d):
    return round(n / d, 4) if d else None


def final_class(sent):
    toks = _content(sent)
    if not toks:
        return None
    last, excluded = toks[-1]
    if excluded:
        return "excluded"
    tag = last.tag
    if tag.startswith("EF"):
        return "ef_nominal" if last.form in EF_NOMINAL else "verbal"
    if tag.startswith("JX") and last.form == "요" and len(toks) > 1 and toks[-2][0].tag.startswith(("EF", "EC")):
        return "verbal"
    if analyser.is_tag(tag, *CHEEON) or tag.startswith("XSN"):
        return "nominal"
    if tag.startswith("ETN"):
        return "etn"
    if tag.startswith("EC"):
        return "connective"
    return "other"


def noun_ending_ratio(res):
    """coding.12: sentences that end in a noun phrase (체언, XSN, ETN, or EF ᆷ/음), over sentences whose end is not excluded."""
    classes = Counter(c for c in (final_class(s) for s in _ctx(res)["sentences"]) if c)
    counted = sum(n for c, n in classes.items() if c != "excluded")
    noun = classes["nominal"] + classes["etn"] + classes["ef_nominal"]
    return {"sentences": counted, "noun_endings": noun, "ratio": ratio(noun, counted),
            "by_final": {k: classes[k] for k in ("verbal", "nominal", "etn", "ef_nominal", "connective", "other", "excluded")}}


def particle_absence_ratio(res):
    """coding.14: 체언 not followed by a particle. XSN/XSM are skipped when looking ahead; 체언 + XSV/XSA is a verb stem and
    leaves the denominator (09 §15.4). VCP (이다) counts as a particle: 서술격 조사. A 체언 whose next token is excluded,
    or which is itself excluded, is undetermined and leaves the denominator."""
    nouns = absent = verbalised = undetermined = 0
    by_next = Counter()
    for sent in _ctx(res)["sentences"]:
        for i, (t, excluded) in enumerate(sent):
            if not analyser.is_tag(t.tag, *CHEEON):
                continue
            if excluded:
                undetermined += 1
                continue
            j = i + 1
            while j < len(sent) and analyser.is_tag(sent[j][0].tag, "XSN", "XSM"):
                j += 1
            if j == len(sent):
                nouns += 1; absent += 1; by_next["end"] += 1
                continue
            nxt, nxt_excluded = sent[j]
            if analyser.is_tag(nxt.tag, "XSV", "XSA"):
                verbalised += 1
            elif nxt_excluded:
                undetermined += 1
            elif analyser.is_tag(nxt.tag, "J", "VCP"):
                nouns += 1
            else:
                nouns += 1; absent += 1
                key = ("noun" if analyser.is_tag(nxt.tag, *CHEEON) else "punctuation" if analyser.is_tag(nxt.tag, *S_TRAIL)
                       else "predicate_after_NNB" if t.tag.startswith("NNB") and analyser.is_tag(nxt.tag, "VV", "VA", "VX", "VCN")
                       else "other")
                by_next[key] += 1
    return {"nouns": nouns, "absent": absent, "ratio": ratio(absent, nouns), "absent_by_next": dict(sorted(by_next.items())),
            "verbalised_dropped": verbalised, "undetermined_dropped": undetermined}


def speech_label(sent):
    """Speech level of one sentence from its final ending. Never a judge reference (E3)."""
    c = final_class(sent)
    if c in (None, "excluded"):
        return None
    if c in ("nominal", "etn", "ef_nominal"):
        return "nominal"
    if c != "verbal":
        return c
    toks = _content(sent)
    form = toks[-1][0].form if toks[-1][0].tag.startswith("EF") else toks[-2][0].form + toks[-1][0].form
    if form.endswith(("니다", "니까", "시오", "ᆸ시다", "읍시다")):
        return "hapsyo"
    if form.endswith(("요", "죠")):
        return "haeyo"
    if form.endswith(("다", "냐", "니", "자", "라", "마")):
        return "haera"
    return "hae"


def speech_level(res):
    """coding.09, honorific, E-7, grammar: the distribution of sentence speech levels. `dominant` and `levels_present` read
    the four verbal levels only."""
    labels = Counter(l for l in (speech_label(s) for s in _ctx(res)["sentences"]) if l)
    verbal = {k: labels[k] for k in SPEECH_LEVELS if labels[k]}
    dominant = max(sorted(verbal), key=lambda k: verbal[k]) if verbal else None
    return {"sentences": sum(labels.values()), "labels": dict(sorted(labels.items())), "dominant": dominant,
            "levels_present": len(verbal)}


def noun_run_length(res):
    """coding.15: runs of consecutive NN* tokens with nothing between (strict). An excluded token ends a run."""
    runs = []
    for sent in _ctx(res)["sentences"]:
        n = 0
        for t, excluded in sent:
            if not excluded and analyser.is_tag(t.tag, *NOUN_RUN):
                n += 1
            else:
                if n:
                    runs.append(n)
                n = 0
        if n:
            runs.append(n)
    return {"runs": len(runs), "mean": round(sum(runs) / len(runs), 4) if runs else None, "max": max(runs, default=None),
            "multi_noun_runs": sum(1 for r in runs if r > 1)}


def genitive_ui_ratio(res):
    """coding.11b, diag 11.6: 의 tagged JKG, over 체언 not excluded; and per 100 어절."""
    jkg = nouns = 0
    for sent in _ctx(res)["sentences"]:
        for t, excluded in sent:
            if t.tag.startswith("JKG"):
                jkg += 1
            elif not excluded and analyser.is_tag(t.tag, *CHEEON):
                nouns += 1
    return {"jkg": jkg, "nouns": nouns, "ratio": ratio(jkg, nouns), "per_100_eojeol": per100(jkg, eojeol(res, ("paragraph",)))}


def ending_key(sent):
    """The sentence's closing ending: trailing EP/EF/EC/ETN/VX/VCP tokens (up to four), e.g. 었+습니다, 고+있+다."""
    toks = _content(sent)
    parts = []
    for t, excluded in reversed(toks):
        if excluded or not analyser.is_tag(t.tag, "EP", "EF", "EC", "ETN", "VX", "VCP") or len(parts) == 4:
            break
        parts.append(t.form)
    return "+".join(reversed(parts)) or None


def ending_monotony(res):
    """E-2, diag 9.1: how concentrated the closing endings are. `ratio` is the most common ending's share of sentences;
    `longest_run` the longest stretch of consecutive sentences with the same ending."""
    keys = [ending_key(s) for s in _ctx(res)["sentences"]]
    keys = [k for k in keys if k]
    if not keys:
        return {"sentences": 0, "distinct": 0, "ratio": None, "longest_run": 0}
    longest = cur = 1
    for a, b in zip(keys, keys[1:]):
        cur = cur + 1 if a == b else 1
        longest = max(longest, cur)
    top = Counter(keys).most_common(1)[0][1]
    return {"sentences": len(keys), "distinct": len(set(keys)), "ratio": ratio(top, len(keys)), "longest_run": longest}


def pos_ngram_diversity(res):
    """diag 9.4: distinct POS trigrams over all POS trigrams, within sentences. Tag subtypes are folded (VV-I → VV) and an
    excluded token is one tag, X. The ratio falls with length: `trigrams` is reported beside it."""
    grams = []
    for sent in _ctx(res)["sentences"]:
        tags = ["X" if excluded else t.tag.split("-")[0] for t, excluded in sent]
        grams += [tuple(tags[i:i + 3]) for i in range(len(tags) - 2)]
    return {"trigrams": len(grams), "distinct": len(set(grams)), "ratio": ratio(len(set(grams)), len(grams))}


def adnominal_chain_depth(res):
    """A-18, diag 1.8: adnominal modifiers (ETM, MM) stacked before one 체언 head. `count` is heads with two or more;
    `max` and `depths` (a histogram) carry the rest. A 체언 followed by XSV/XSA is a verb stem, not a head."""
    depths = Counter()
    for sent in _ctx(res)["sentences"]:
        pending = 0
        for i, (t, _) in enumerate(sent):
            if analyser.is_tag(t.tag, "ETM", "MM"):
                pending += 1
            elif analyser.is_tag(t.tag, *CHEEON):
                nxt = sent[i + 1][0].tag if i + 1 < len(sent) else ""
                if pending and not analyser.is_tag(nxt, "XSV", "XSA"):
                    depths[pending] += 1
                    pending = 0
            elif analyser.is_tag(t.tag, "EF", "EC", *S_TRAIL):
                pending = 0
    return {"count": sum(n for d, n in depths.items() if d >= 2), "max": max(depths, default=0),
            "depths": {str(d): depths[d] for d in sorted(depths)}}


def suffix_jeok_density(res):
    """diag 7.2, F-4/F-5: the XSN suffixes 적, 성, 화. `count` and `per_100_eojeol` are for 적; `followed_by_noun` is 적
    directly before a 체언 (F-5's "~적 N")."""
    by = Counter()
    jeok_n = 0
    for sent in _ctx(res)["sentences"]:
        for i, (t, _) in enumerate(sent):
            if t.tag.startswith("XSN") and t.form in ("적", "성", "화"):
                by[t.form] += 1
                if t.form == "적" and i + 1 < len(sent) and analyser.is_tag(sent[i + 1][0].tag, *CHEEON):
                    jeok_n += 1
    return {"count": by["적"], "per_100_eojeol": per100(by["적"], eojeol(res, ("paragraph",))), "followed_by_noun": jeok_n,
            "by_suffix": {k: by[k] for k in ("적", "성", "화")}}


def spacing_errors(res):
    """grammar: gaps between two Hangul characters where the analyser's spacing differs from the text's, on paragraph
    lines. A gap next to an excluded character is not read. A line whose characters the analyser changed is skipped."""
    mask = _ctx(res)["mask"]
    inserted = removed = skipped = 0
    for s, e, kind in res.lines:
        if kind != "paragraph":
            continue
        raw = res.text[s:e]
        fixed = analyser.space(raw)
        a = [(i, ch) for i, ch in enumerate(raw) if not ch.isspace()]
        b = [ch for ch in fixed if not ch.isspace()]
        if [ch for _, ch in a] != b:
            skipped += 1
            continue
        fixed_space_before = []
        k = 0
        for ch_i, ch in enumerate(fixed):
            if not ch.isspace():
                fixed_space_before.append(ch_i > 0 and fixed[ch_i - 1].isspace())
                k += 1
        for n in range(1, len(a)):
            (i0, c0), (i1, c1) = a[n - 1], a[n]
            if not (HANGUL.match(c0) and HANGUL.match(c1)) or mask[s + i0] or mask[s + i1]:
                continue
            orig = i1 > i0 + 1
            if fixed_space_before[n] and not orig:
                inserted += 1
            elif orig and not fixed_space_before[n]:
                removed += 1
    return {"count": inserted + removed, "missing_space": inserted, "extra_space": removed,
            "per_100_eojeol": per100(inserted + removed, eojeol(res, ("paragraph",))), "lines_skipped": skipped}


# name, function, layer(s), tier  (09 §15.4 Tier 1)
MEASUREMENTS = [
    ("noun_ending_ratio", noun_ending_ratio, ("policy",), 1),
    ("particle_absence_ratio", particle_absence_ratio, ("policy",), 1),
    ("speech_level", speech_level, ("policy",), 1),
    ("noun_run_length", noun_run_length, ("policy",), 1),
    ("genitive_ui_ratio", genitive_ui_ratio, ("policy",), 1),
    ("ending_monotony", ending_monotony, ("skill",), 1),
    ("pos_ngram_diversity", pos_ngram_diversity, ("skill",), 1),
    ("adnominal_chain_depth", adnominal_chain_depth, ("skill",), 1),
    ("suffix_jeok_density", suffix_jeok_density, ("skill",), 1),
    ("spacing_errors", spacing_errors, ("skill",), 1),
]
