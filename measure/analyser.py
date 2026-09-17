"""The morphological analyser for Tier 1 (09 §15.3, S3-A): kiwipiepy, pinned in measure/requirements.txt.

Imported lazily, so Tier 0 runs on the standard library alone. When the package is missing, `available()` is False and
the reason is kept: Tier 1 is then not computed, and the run report says so (09 §15.6).

Tags are matched by prefix (E2: irregular stems are tagged VV-I, VV-R). Token offsets are character offsets into the text
that was analysed.
"""
_KIWI = None
_ERROR = None


def _load():
    global _KIWI, _ERROR
    if _KIWI is None and _ERROR is None:
        try:
            from kiwipiepy import Kiwi
            _KIWI = Kiwi()
        except Exception as exc:  # ImportError, or a model that fails to load
            _ERROR = f"{type(exc).__name__}: {exc}"
    return _KIWI


def available():
    return _load() is not None


def version():
    """The analyser version for the run report, or None when it is unavailable."""
    if not available():
        return None
    import kiwipiepy
    try:
        from importlib.metadata import version as dist_version
        model = dist_version("kiwipiepy_model")
    except Exception:
        model = "unknown"
    return f"kiwipiepy {kiwipiepy.__version__} (kiwipiepy_model {model}, {_KIWI.model_type})"


def unavailable_reason():
    _load()
    return _ERROR


class Token:
    __slots__ = ("form", "tag", "start", "end")

    def __init__(self, form, tag, start, end):
        self.form, self.tag, self.start, self.end = form, tag, start, end

    def __repr__(self):
        return f"{self.form}/{self.tag}"


def sentences(text):
    """Sentences of one raw line: a list of token lists, offsets into `text`."""
    kiwi = _load()
    out = []
    for sent in kiwi.split_into_sents(text, return_tokens=True):
        out.append([Token(t.form, t.tag, t.start, t.start + t.len) for t in sent.tokens])
    return out


def space(text):
    """The analyser's spacing of `text` (whitespace reset), for spacing_errors."""
    return _load().space(text, reset_whitespace=True)


def is_tag(tag, *prefixes):
    return any(tag.startswith(p) for p in prefixes)
