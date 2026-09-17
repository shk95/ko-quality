"""Tier 2 (09 §15.4): `ko.preserve`, on an original and its rewrite together. Paste-in only.

Each kind returns {"violations": [...], "count": n, "pass": bool}; a kind passes at zero violations. What must survive is
read from the original through the exclusion pass, so the zones are the ones every other measurement uses:

  number_unit_date  number spans (numbers, dates, units, currency): each occurrence must appear among the rewrite's
  quote             attributed direct quotations and block quotes, verbatim (whitespace folded). A rhetorical quote is
                    the writer's own sentence and a rewrite may remove it (J-2), so it is not preserved
  code_url_path     code, URL, path and identifier spans, verbatim, as often as in the original
  proper_noun       proper-noun spans (Latin capitalised and NNP), as often as in the original            Tier 1
  register          the dominant speech level (speech_level) of the rewrite equals the original's            Tier 1

`ko.change_rate` is not built (09 §15.5).
"""
from collections import Counter

from measure import analyser, exclusion
from measure.measurements import tier1

KINDS = ("number_unit_date", "quote", "code_url_path", "proper_noun", "register")
TIER1_KINDS = ("proper_noun", "register")
PASTE_IN_STRATUM = "paste-in"     # annotation stratum prefix that makes a log record a paste-in (09 §18.3)


def fold(s):
    return " ".join(s.split())


def _span_texts(res, zones):
    out = []
    for z in zones:
        for s, e in res.spans[z]:
            t = res.text[s:e]
            if z == "quotation" and t.lstrip().startswith(">"):
                t = t.lstrip()[1:]
            t = fold(t)
            if t:
                out.append(t)
    return Counter(out)


def _missing_substrings(needed, text):
    folded = fold(text)
    return [{"text": t, "original": n, "rewrite": folded.count(t)} for t, n in sorted(needed.items()) if folded.count(t) < n]


def _result(violations):
    return {"violations": violations, "count": len(violations), "pass": not violations}


def preserve(original, rewrite, kinds=KINDS):
    a, b = exclusion.run(original or ""), exclusion.run(rewrite or "")
    out = {}
    for kind in kinds:
        if kind in TIER1_KINDS and a.analysis is None:
            out[kind] = {"unavailable": analyser.unavailable_reason() or "analyser not used"}
            continue
        if kind == "number_unit_date":
            need, have = _span_texts(a, ("number",)), _span_texts(b, ("number",))
            out[kind] = _result([{"text": t, "original": n, "rewrite": have[t]} for t, n in sorted(need.items()) if have[t] < n])
        elif kind == "quote":
            out[kind] = _result(_missing_substrings(_span_texts(a, ("quotation",)), rewrite or ""))
        elif kind == "code_url_path":
            out[kind] = _result(_missing_substrings(_span_texts(a, ("code", "url_path_id")), rewrite or ""))
        elif kind == "proper_noun":
            out[kind] = _result(_missing_substrings(_span_texts(a, ("proper_noun",)), rewrite or ""))
        elif kind == "register":
            before, after = tier1.speech_level(a)["dominant"], tier1.speech_level(b)["dominant"]
            out[kind] = _result([] if before is None or before == after else [{"original": before, "rewrite": after}])
    return out


def pasted_original(task):
    """The pasted text of a paste-in prompt: everything after the first blank line (the instruction comes first), or the
    whole prompt when it has no blank line. The corpus prompt set (P8) writes paste-in prompts in that shape."""
    task = task or ""
    head, sep, rest = task.partition("\n\n")
    return rest if sep and rest.strip() else task
