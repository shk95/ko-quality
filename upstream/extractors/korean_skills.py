"""korean-skills (procedure.grammar) extractor — added to the pipeline using only
upstream/interface/*.schema.yaml and upstream/extractors/README.md's conventions
(abstraction test, P4; its frontmatter and duplicate-anchor workarounds moved into markdown.py afterwards).
NAME and extract(commit) follow the README contract:
extract(commit) -> ({normalized relative path: text}, [(id, reason), ...] failures).

Sources (roles: procedure.grammar, per upstream/lock.yaml):
  skills/grammar-checker/SKILL.md                         -> procedure/grammar.yaml
  skills/grammar-checker/references/rules.md               -> reference/grammar/rules.yaml
  skills/grammar-checker/references/common-errors.md       -> reference/grammar/common-errors.yaml
"""
import re

from . import markdown
from .normalized import excluded_lines, fragment_lines
from .source import read

NAME = "korean-skills"
SKILL_PATH = "skills/grammar-checker/SKILL.md"
RULES_PATH = "skills/grammar-checker/references/rules.md"
ERRORS_PATH = "skills/grammar-checker/references/common-errors.md"

BOLD_LABEL_ONLY = re.compile(r"^\*\*[^*]+\*\*:$")

# One supplier per procedure slot (procedure.schema.yaml); headings under ## 작업 흐름,
# ## 중요 지침 and ## 특수 상황 처리 map 1:1 to a selection kind for every block in them.
CTX_KIND = {
    "### 1단계: 텍스트 입력 받기": "input",
    "### 2단계: 오류 검사": "step",
    "### 3단계: 참조 문서 로드 (필요 시)": "step",
    "### 4단계: 결과 제시": "output",
    "### 1. 문맥 고려": "invariant",
    "### 3. 교육적 설명": "invariant",
    "### 4. 우선순위 준수": "invariant",
    "### 5. 과도한 교정 피하기": "invariant",
    "### 매우 짧은 텍스트 (1-2문장)": "output",
    "### 코드 주석이나 기술 문서": "invariant",
    "### 학습 목적 사용": "step",
}

FRONTMATTER_EXCLUSIONS = [
    ("name", "skill id; assigned by assemble/skills/<name>.md, not procedure content (06 §7)"),
    ("description", "harness-facing invocation description; assemble/ supplies description per 06 §7"),
    ("license", "packaging metadata; already recorded in upstream/lock.yaml"),
    ("metadata", "packaging metadata (author, version); not procedure content"),
    ("allowed-tools", "harness-bound tool list (Claude Code specific); procedure role carries steps/invariants, not tool bindings"),
]


def _classify(block):
    """-> (kind, note) to keep the block as a fragment, or (None, reason) to exclude it."""
    ctx, kind, text = block["ctx"], block["kind"], block["text"]
    stripped = text.strip()

    if kind == "heading":
        return None, "heading; structure supplied by the renderer, not a fragment (procedure.schema.yaml render_notes)"
    if ctx == "## 예시":
        return None, "points to skills/grammar-checker/examples/*; no fragment role assigned within this extraction"
    if kind == "paragraph" and BOLD_LABEL_ONLY.match(stripped):
        return None, ("bold-label paragraph groups the items that follow; no content of its own, "
                       "treated like a heading (procedure.schema.yaml render_notes) though it is not one syntactically")

    note = None
    if ctx == "## 소개":
        sem = "summary" if kind == "paragraph" else "invariant"
        if sem == "invariant" and "맞춤법/철자" in stripped:
            note = ("no selection kind matches 'scope of error categories checked' — grammar has no taxonomy "
                    "slot (06 §5.3 table has taxonomy only for rewrite/diagnose); classified as invariant "
                    "(a standing constraint), the closest of the seven")
        return sem, note
    if ctx == "### 2. 확신도 표시":
        sem = "invariant" if kind == "paragraph" else "grade"
        if sem == "grade" and "확실한 오류" in stripped:
            note = ("the three confidence tiers (확실한 오류/권장 사항/제안) read as a rating scale, matching "
                    "procedure.schema.yaml's 'grade' kind better than an invariant")
        return sem, note
    if ctx == "### 실시간 교정 모드":
        return ("output" if stripped.startswith("```") else "step"), None
    if ctx == "## 최종 확인사항":
        return ("summary" if stripped.startswith("당신의 목표는") else "check"), None
    if ctx in CTX_KIND:
        if "Read 도구" in stripped:
            note = ("names the Read tool (harness-bound) inside an otherwise portable input-contract "
                    "sentence; kept verbatim rather than edited to 'adapted' (README step 3 / 06 §5.4 says avoid it)")
        return CTX_KIND[ctx], note
    return None, None  # unreached if every ctx above is covered; caller reports as a failure, not silently


def _procedure_fragments(commit):
    raw = read(NAME, SKILL_PATH, commit)
    blocks = markdown.parse(raw)

    excluded = [(SKILL_PATH, f"frontmatter > {key}", reason) for key, reason in FRONTMATTER_EXCLUSIONS]
    frags, failures, counters = [], [], {}
    for b in blocks:
        kind, info = _classify(b)
        if kind is None:
            if info is None:
                failures.append((b["anchor"] or b["ctx"], "no classification rule matched this context"))
            else:
                excluded.append((SKILL_PATH, b["anchor"], info))
            continue
        counters[kind] = counters.get(kind, 0) + 1
        frag = {"id": f"{kind}.{counters[kind]}", "kind": kind, "text": b["text"],
                "path": SKILL_PATH, "anchor": b["anchor"], "transform": "verbatim"}
        if info:
            frag["note"] = info
        frags.append(frag)

    lines = ["role: procedure", "slot: grammar", "fragments:"]
    for f in frags:
        lines += fragment_lines(f, NAME, commit)
    lines += excluded_lines(excluded)
    return "\n".join(lines) + "\n", failures


def _reference_file(commit, name, path, kind):
    text = read(NAME, path, commit)
    blocks = markdown.parse(text)
    lines = ["role: reference", "slot: grammar", f"name: {name}", f"kind: {kind}", "fragments:"]
    for i, b in enumerate(blocks, start=1):
        frag = {"id": f"{name}.{i:03d}", "kind": b["kind"], "text": b["text"],
                "path": path, "anchor": b["anchor"], "transform": "verbatim"}
        lines += fragment_lines(frag, NAME, commit)
    return "\n".join(lines) + "\n"


def extract(commit):
    files, failures = {}, []

    procedure_text, proc_failures = _procedure_fragments(commit)
    files["procedure/grammar.yaml"] = procedure_text
    failures += proc_failures

    # rules.md: normative rule statements the procedure reads when unsure (kind: rubric).
    files["reference/grammar/rules.yaml"] = _reference_file(commit, "rules", RULES_PATH, "rubric")
    # common-errors.md: a lookup table of known wrong -> right fixes (kind: recipes).
    files["reference/grammar/common-errors.yaml"] = _reference_file(commit, "common-errors", ERRORS_PATH, "recipes")

    return files, failures
