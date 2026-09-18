"""The exclusion pass (09 §15.2). One implementation, versioned, shared by every tier and by the derived language fields.

Works on raw lines, before any sentence splitting. Returns character spans per zone over the original text and the
structure of each line (heading, list item, table row, quote, paragraph, code). Nothing is judged here.

Zones (09 §15.2 table rows):
  code          fenced code blocks and inline code                                    Tier 0
  url_path_id   URLs, paths, identifiers (snake_case, camelCase, dotted names)        Tier 0
  quotation     attributed direct quotation (a quote plus a speech marker), and       Tier 0
                markdown block quotes. A quote without a marker is rhetorical and
                is not excluded; it is reported as `rhetorical_quote`
  number        numbers, dates, times, units, currency                                Tier 0
  structure     headings, list items, table rows: kept as separate spans, not removed Tier 0
  math          mathematical and chemical notation                                    Tier 0
  legal         legal text: 제N조, 제N항, 제N호 markers, and a line that opens with one Tier 0
  abbreviation  Latin all-caps tokens                                                 Tier 0
  proper_noun   Latin capitalised tokens (Tier 0), and 체언 tagged NNP by the analyser Tier 1

With the analyser (measure/analyser.py) the version is EXCLUSION_VERSION; without it the NNP half of the proper_noun zone
is not applied and the version carries `-t0`, so the two are never pooled. The analyser's sentences for every prose line
are kept on the Result (`analysis`), for Tier 1 to reuse.
"""
import re

EXCLUSION_VERSION = "ex-3"  # ex-2: honorific speech verbs (하셨, 하시) after 라고/고 (P4 verification). ex-3: NNP (P6)
TIER0_SUFFIX = "-t0"        # the version of a run without the analyser
A = re.ASCII  # \b and \w must not treat Hangul as a word character: particles attach directly (`320ms에서`, `max_retries를`)
ZONES = ("code", "url_path_id", "quotation", "number", "structure", "math", "legal", "abbreviation", "proper_noun")
REMOVED = ("code", "url_path_id", "quotation", "number", "math", "legal", "abbreviation", "proper_noun")

FENCE = re.compile(r"^\s{0,3}(```|~~~)")
INLINE_CODE = re.compile(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d{1,3}[.)])\s+")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
BLOCKQUOTE = re.compile(r"^\s{0,3}>")

URL = re.compile(r"\b(?:https?|ftp)://[^\s<>()\[\]\"'`가-힣]+|\bwww\.[A-Za-z0-9-]+\.[^\s<>()\[\]\"'`가-힣]+", A)
PATH = re.compile(r"(?<![\w/.])(?:~|\.{1,2})?/(?:[\w.@+-]+/)*[\w.@+-]+/?"
                  r"|(?<![\w/])[A-Za-z]:\\[^\s가-힣]+"
                  r"|(?<![\w/.])(?:[\w.@+-]+/)+[\w@+-]+\.[A-Za-z0-9]{1,8}\b", A)
FILE_NAME = re.compile(r"(?<![\w/.])[A-Za-z_][\w-]*\.(?:py|js|ts|tsx|jsx|json|ya?ml|toml|md|txt|sh|go|rs|java|kt|rb|c|h|cpp|hpp|css|html|sql|lock|cfg|ini|env)\b", A)
SNAKE = re.compile(r"\b[A-Za-z_]*[a-z0-9]_[A-Za-z0-9_]+\b|\b_[A-Za-z0-9_]+\b", A)
CAMEL = re.compile(r"\b[a-z]+(?:[A-Z][a-z0-9]*)+\b|\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]+)+\b", A)
DOTTED = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+(?:\(\))?", A)
CALL = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\(\)", A)

QUOTE_PAIRS = [("\u201c", "\u201d"), ("\u2018", "\u2019"), ('"', '"'), ("'", "'"), ("\u300c", "\u300d"), ("\u300e", "\u300f")]
SPEECH_MARKER = re.compile(r"^\s*(?:(?:이?라고|고|하고)\s*(?:말|했|하였|하셨|하시|한다|합니다|밝혔|전했|물었|묻|답했|답하|적었|썼|주장|강조|설명|덧붙|외쳤|말씀|알렸|지적|토로|반문)|이?라며|이?라는\s*(?:말|답|질문|문구|메시지|지적|설명)|(?:하|이)?며\s|하더라|는\s*말|(?:이|가|의)?\s*(?:말|발표|보도|설명)?에\s*따르면)")  # a speech verb must follow 라고/고: `X라고 부르다` names, it does not quote. Markers from upstream's Do-NOT line: 말했다·밝혔다·따르면

NUMBER = re.compile(
    r"(?:[₩$€£¥]\s?\d[\d,]*(?:\.\d+)?)"                                       # currency prefix
    r"|\d{4}\s*년(?:\s*\d{1,2}\s*월)?(?:\s*\d{1,2}\s*일)?"                        # 2026년 9월 17일
    r"|\d{1,2}\s*월\s*\d{1,2}\s*일"                                               # 9월 17일
    r"|\d{4}[-./]\d{1,2}[-./]\d{1,2}"                                              # 2026-09-17
    r"|\d{1,2}:\d{2}(?::\d{2})?"                                                   # 14:30
    r"|\d[\d,]*(?:\.\d+)?\s?(?:만\s?원|억\s?원|조\s?원|%|퍼센트|원|달러|엔|유로|위안|"
    r"KB|MB|GB|TB|kB|Mb|Gb|ms|ns|µs|us|s|sec|min|h|km|m|cm|mm|kg|g|mg|L|mL|ml|°C|℃|K|Hz|kHz|MHz|GHz|W|kW|V|A|px|pt|em|rem|dpi|fps|rpm|bps|kbps|Mbps|Gbps)(?![A-Za-z])"
    r"|\d[\d,]*(?:\.\d+)?\s?(?:개월|시간|킬로바이트|메가바이트|기가바이트|바이트|초|분|일|주|년|배|회|번|개|명|건|줄|자)"
    r"|v?\d+(?:\.\d+){1,3}"                                                        # versions 1.2.3
    r"|\d[\d,]*(?:\.\d+)?", A)

MATH_INLINE = re.compile(r"\$\$.+?\$\$|\$[^$\s][^$]*?\$|\\\(.+?\\\)|\\\[.+?\\\]")
LATEX_CMD = re.compile(r"\\(?:frac|sqrt|sum|int|alpha|beta|gamma|delta|theta|lambda|mu|sigma|pi|cdot|times|leq|geq|neq|approx|infty)\b[^\s가-힣]*")
CHEM = re.compile(r"\b(?:[A-Z][a-z]?\d*){1,6}(?:[+-]|\d[+-])?\b", A)
EQUATION = re.compile(r"(?<![\w가-힣])[A-Za-z0-9()]+(?:\s*[+\-*/^=<>≤≥≠±×÷]\s*[A-Za-z0-9().]+){2,}(?![\w])"
                      r"|(?<![\w가-힣])[a-zA-Z]\^\d+|(?<![\w가-힣])[a-zA-Z]_\{?\w+\}?", A)

LEGAL_MARK = re.compile(r"제\s?\d+\s?조(?:의\s?\d+)?(?:\s?제\s?\d+\s?항)?(?:\s?제\s?\d+\s?호)?|제\s?\d+\s?[항호]")
LEGAL_LINE = re.compile(r"^\s*(?:[-*+]\s+)?제\s?\d+\s?조")

ABBREV = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9]*[A-Z](?:s)?(?![A-Za-z0-9_])|(?<![A-Za-z0-9_])[A-Z]\d+[A-Z0-9]*(?![A-Za-z0-9_])", A)
CAPITALISED = re.compile(r"(?<![A-Za-z0-9_])[A-Z][a-z]+(?:[A-Z][a-z]+)*(?:\s[A-Z][a-z]+)*(?![A-Za-z0-9_])")


def version(analyse=None):
    from measure import analyser
    return EXCLUSION_VERSION if (analyser.available() if analyse is None else analyse) else EXCLUSION_VERSION + TIER0_SUFFIX


class Result:
    def __init__(self, text):
        self.text = text
        self.spans = {z: [] for z in ZONES}
        self.spans["rhetorical_quote"] = []
        self.lines = []          # (start, end, kind): kind in paragraph, heading, list_item, table_row, quote, code, blank
        self.analysis = None     # {(start, end): [sentence token lists, offsets into self.text]} when the analyser ran
        self.version = EXCLUSION_VERSION + TIER0_SUFFIX

    def removed_mask(self, zones=REMOVED):
        mask = bytearray(len(self.text))
        for z in zones:
            for s, e in self.spans[z]:
                for i in range(s, e):
                    mask[i] = 1
        return mask

    def prose(self, kinds=("paragraph", "heading", "list_item", "table_row"), zones=REMOVED, fill=" "):
        """Text left after exclusion, per line, for the line kinds asked. Excluded characters become `fill` (a space, or a
        placeholder when a measurement needs the excluded text to keep its length)."""
        mask = self.removed_mask(zones)
        out = []
        for s, e, kind in self.lines:
            if kind not in kinds:
                continue
            line = "".join((fill if not self.text[i].isspace() else self.text[i]) if mask[i] else self.text[i] for i in range(s, e))
            if kind == "heading":
                line = HEADING.sub("", line)
            elif kind == "list_item":
                line = LIST_ITEM.sub("", line)
            elif kind == "table_row":
                line = line.replace("|", " ")
            out.append(line)
        return out

    def summary(self):
        return {z: len(v) for z, v in self.spans.items()}


def _free(mask, s, e):
    return not any(mask[s:e])


def _add(res, taken, zone, s, e, allow_overlap=False):
    if e <= s:
        return
    if not allow_overlap and not _free(taken, s, e):
        return
    res.spans[zone].append((s, e))
    for i in range(s, e):
        taken[i] = 1


def _find_quotes(line):
    """(open_index, close_index_exclusive) for balanced quotes on one line."""
    found, i = [], 0
    while i < len(line):
        for o, c in QUOTE_PAIRS:
            if line[i] == o:
                if o == "'" and i > 0 and line[i - 1].isalnum():   # apostrophe inside a word
                    continue
                j = line.find(c, i + 1)
                if j > i + 1:
                    found.append((i, j + 1))
                    i = j
                    break
        i += 1
    return found


def run(text, analyse=None):
    """Apply the pass to one text. Order matters: code first, then zones that could contain other zones' look-alikes.
    `analyse`: None uses the analyser when it is installed; False never does (Tier 0 only)."""
    from measure import analyser
    text = text or ""
    res = Result(text)
    taken = bytearray(len(text))
    pos, in_fence = 0, False
    raw_lines = text.split("\n")
    for raw in raw_lines:
        s, e = pos, pos + len(raw)
        pos = e + 1
        if FENCE.match(raw):
            _add(res, taken, "code", s, e, allow_overlap=True)
            res.lines.append((s, e, "code"))
            in_fence = not in_fence
            continue
        if in_fence:
            _add(res, taken, "code", s, e, allow_overlap=True)
            res.lines.append((s, e, "code"))
            continue
        if not raw.strip():
            res.lines.append((s, e, "blank"))
            continue
        if BLOCKQUOTE.match(raw):
            kind = "quote"
        elif HEADING.match(raw):
            kind = "heading"
        elif TABLE_ROW.match(raw):
            kind = "table_row"
        elif LIST_ITEM.match(raw):
            kind = "list_item"
        else:
            kind = "paragraph"
        res.lines.append((s, e, kind))
        if kind == "quote":
            _add(res, taken, "quotation", s, e)
            continue
        if kind in ("heading", "list_item", "table_row"):
            res.spans["structure"].append((s, e))
        _line_zones(res, taken, raw, s)
    if analyse is None:
        analyse = analyser.available()
    if analyse:
        _nnp(res, taken, analyser)
    for z in res.spans:
        res.spans[z].sort()
    return res


def _line_zones(res, taken, raw, base):
    def each(pattern, zone, group=0, check=None):
        for m in pattern.finditer(raw):
            if check and not check(m):
                continue
            _add(res, taken, zone, base + m.start(group), base + m.end(group))

    each(INLINE_CODE, "code")
    each(MATH_INLINE, "math")
    each(URL, "url_path_id")
    each(PATH, "url_path_id", check=lambda m: ("/" in m.group(0) or "\\" in m.group(0)) and not re.fullmatch(r"\d+(?:/\d+)+", m.group(0)) and len(m.group(0)) > 2)
    each(FILE_NAME, "url_path_id")
    # attributed quotation: a quote followed by a speech marker; otherwise rhetorical
    for qs, qe in _find_quotes(raw):
        if not _free(taken, base + qs, base + qe):
            continue
        if SPEECH_MARKER.match(raw[qe:]):
            _add(res, taken, "quotation", base + qs, base + qe)
        else:
            res.spans["rhetorical_quote"].append((base + qs, base + qe))
    if LEGAL_LINE.match(raw):
        _add(res, taken, "legal", base + len(raw) - len(raw.lstrip()), base + len(raw))
    each(LEGAL_MARK, "legal")
    each(LATEX_CMD, "math")
    each(EQUATION, "math", check=lambda m: re.search(r"[A-Za-z]", m.group(0)) is not None)
    each(DOTTED, "url_path_id", check=lambda m: not re.fullmatch(r"[A-Z][a-z]*\.[A-Z]?[a-z]*", m.group(0)) and not re.fullmatch(r"[\d.]+", m.group(0)))
    each(CALL, "url_path_id")
    each(SNAKE, "url_path_id")
    each(CAMEL, "url_path_id")
    each(CHEM, "math", check=lambda m: re.search(r"\d", m.group(0)) is not None and re.search(r"[A-Z]", m.group(0)) is not None
         and not re.fullmatch(r"[A-Z]\d+", m.group(0)) and _is_formula(m.group(0)))
    each(ABBREV, "abbreviation", check=lambda m: len(m.group(0)) >= 2)
    each(NUMBER, "number")
    # a multi-word name partly taken by another zone (`GitHub Actions`: GitHub is an identifier shape) keeps its free words
    for m in CAPITALISED.finditer(raw):
        for w in re.finditer(r"\S+", m.group(0)):
            _add(res, taken, "proper_noun", base + m.start() + w.start(), base + m.start() + w.end())


def _nnp(res, taken, analyser):
    """Tier 1 half of the proper_noun zone: every token tagged NNP, on raw prose lines, after the Tier 0 zones. Only the
    characters no other zone took are added, so a name partly inside a path keeps its free part."""
    res.analysis = {}
    for s, e, kind in res.lines:
        if kind not in ("paragraph", "heading", "list_item", "table_row"):
            continue
        sents = analyser.sentences(res.text[s:e])
        for sent in sents:
            for t in sent:
                t.start += s
                t.end += s
                if analyser.is_tag(t.tag, "NNP"):
                    i = t.start
                    while i < t.end:
                        if taken[i] or res.text[i].isspace():
                            i += 1
                            continue
                        j = i
                        while j < t.end and not taken[j] and not res.text[j].isspace():
                            j += 1
                        _add(res, taken, "proper_noun", i, j)
                        i = j
        res.analysis[(s, e)] = sents
    res.version = EXCLUSION_VERSION


ELEMENTS = set("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr "
               "Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pt Au Hg Pb Bi U".split())


def _is_formula(token):
    parts = re.findall(r"([A-Z][a-z]?)(\d*)", token)
    return bool(parts) and "".join(a + b for a, b in parts) == token.rstrip("+-") and all(a in ELEMENTS for a, _ in parts) and len(parts) >= 2 or \
        (bool(parts) and len(parts) == 1 and parts[0][0] in ELEMENTS and parts[0][1] != "" and len(parts[0][0]) == 2)
