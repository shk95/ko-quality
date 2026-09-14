"""im-not-ai → procedure/rewrite, taxonomy/rewrite (flow.md D1, D5). Selection ported from the P1 hand extraction."""
import re

from .markdown import headings
from .normalized import excluded_lines, fragment_lines
from .source import AnchorNotFound, read

NAME = "im-not-ai"
B = "codex/skills/humanize-korean/SKILL.md"
C = "agents/humanize-monolith.md"
A = "skills/humanize-korean/SKILL.md"
H = "skills/humanize-korean/references/quick-rules.header.md"
F = "skills/humanize-korean/references/quick-rules.footer.md"
T = "skills/humanize-korean/references/ai-tell-taxonomy.md"
Q = "skills/humanize-korean/references/quick-rules.md"
HDR = "# Temporary format (P1, flow.md). Schema is derived in P4. Text values are exact upstream bytes; JSON-quoted strings are valid YAML."
PRIME = "## 철칙 (Prime Directives — 위반 시 즉시 롤백)"
STEPS = "## 절차 (단일 호출 안에서)"
S2 = "### 단계 2: 1차 패턴 탐지 (도구 호출 0회 — 메모리)"
S3 = "### 단계 3: 윤문 (도구 호출 0회 — 메모리)"
S4 = "### 단계 4: 자체검증 (도구 호출 0회 — 메모리)"
RESP = "## 응답 형식 (사용자에게 직접 반환)"
CHECK = "## 자체검증 체크리스트 (monolith 윤문 후 자가 점검)"
GRADE = "## 등급 기준 (자가 채점)"


class Doc:
    def __init__(self, commit):
        self.commit, self.cache = commit, {}

    def lines(self, path):
        if path not in self.cache:
            self.cache[path] = read(NAME, path, self.commit)
        return self.cache[path].split("\n")

    def section(self, path, heading):
        lines = self.lines(path)
        hs = headings(lines)
        idx = [i for i, (n, t) in enumerate(hs) if t == heading]
        if len(idx) != 1:
            raise AnchorNotFound(f"{path}: heading {heading!r} found {len(idx)} times")
        start = hs[idx[0]][0] + 1
        end = hs[idx[0] + 1][0] if idx[0] + 1 < len(hs) else len(lines)
        return lines[start:end]

    def numbered(self, path, heading, n):
        sec = self.section(path, heading)
        starts = [i for i, l in enumerate(sec) if l.startswith(f"{n}. ")]
        if len(starts) != 1:
            raise AnchorNotFound(f"{path}: {heading} > {n} found {len(starts)} times")
        j = starts[0] + 1
        while j < len(sec) and sec[j].startswith("   "):
            j += 1
        return "\n".join(sec[starts[0]:j])[len(f"{n}. "):]

    def bullet(self, path, heading, n):
        bs = [l for l in self.section(path, heading) if l.startswith("- ")]
        if len(bs) < n:
            raise AnchorNotFound(f"{path}: {heading} > bullet {n} missing")
        return bs[n - 1][2:]

    def labeled(self, path, label):
        ls = [l for l in self.lines(path) if l.lstrip().startswith(label) or l.lstrip().startswith("- " + label)]
        if len(ls) != 1:
            raise AnchorNotFound(f"{path}: bold label {label} found {len(ls)} times")
        l = ls[0].lstrip()
        return l[2:] if l.startswith("- ") else l


def first_sentence(text, where):
    k = text.find(". ")
    if k < 0:
        raise AnchorNotFound(f"{where}: no sentence boundary")
    return text[:k + 1]


EXCLUDED = [
    (B, "## 철칙 (위반 시 즉시 롤백)", "replaced by C's 철칙 1-9 (flow D1)"),
    (B, f"{STEPS} > 7", "writes _workspace/{run_id}/final.md (harness-bound, flow D1)"),
    (B, f"{STEPS} > 8", "response shape taken from C 응답 1-3; item ④ recommends Claude Code 정밀 모드 (flow D1)"),
    (B, "## 등급", "C/D line recommends Claude Code strict mode; footer 등급 기준 used instead"),
    (B, "## 참고", "playbook and full taxonomy not supplied (flow D5)"),
    (H, "bold label **내용 앵커 (탐지 전에 내부 목록화):**", "covered by C 철칙 1 and anchor_ledger steps"),
    (H, "bold label **과윤문 가드:**", "names verify_change_rate.py; 30/50 covered by C 철칙 5"),
    (F, f"{CHECK} > paragraph after list (위반 시 …)", "writes into final.md; retry-once covered by B step 6"),
    (Q, "whole file", "generated; selection reproduced from taxonomy entries (flow D5)"),
    ("skills/humanize-korean/references/rewriting-playbook.md", "whole file", "not required by the steps (flow D5)"),
]


def fragments(commit):
    """(procedure fragments, taxonomy fragments, failures). A failure is (id, reason): the anchor did not resolve."""
    d = Doc(commit)
    proc, tax, failures = [], [], []

    def frag(out, fid, kind, path, anchor, get, transform="verbatim", note=None):
        try:
            text = get()
        except AnchorNotFound as e:
            failures.append((fid, str(e))); return
        out.append(dict(id=fid, kind=kind, text=text, path=path, anchor=anchor, transform=transform, note=note))

    h1 = "# Humanize Korean — Single-call Path (Codex · GitHub Copilot CLI)"
    frag(proc, "intro", "summary", B, f"{h1} > paragraph 1 > sentence 1",
         lambda: first_sentence(d.section(B, h1)[1], "B intro"), "selected",
         "sentences 2-3 name harnesses (Codex, Copilot CLI, Claude Code)")
    for n in range(1, 10):
        frag(proc, f"invariant.{n}", "invariant", C, f"{PRIME} > {n}", lambda n=n: d.numbered(C, PRIME, n))
    frag(proc, "invariant.10", "invariant", H, "bold label **서법 보존 (v2.4, 필수):**",
         lambda: d.labeled(H, "**서법 보존 (v2.4, 필수):**"))
    for n in range(1, 7):
        frag(proc, f"step.{n}", "step", B, f"{STEPS} > {n}", lambda n=n: d.numbered(B, STEPS, n))
    frag(proc, "step.2.hygiene", "step", A,
         "## Phase 1: 입력 저장 + 정량 사전 점수 (input shim — 전 경로 공통) > 2 > bold label **챗봇 잔재 위생 (v2.6)**",
         lambda: d.labeled(A, "**챗봇 잔재 위생 (v2.6)**"))
    frag(proc, "step.4.anchor", "step", C, f"{S2} > bullet 1", lambda: d.bullet(C, S2, 1))
    frag(proc, "step.5.anchor", "step", C, f"{S3} > bullet 4", lambda: d.bullet(C, S3, 4))
    frag(proc, "step.5.abort", "step", C, "## 에러 핸들링 > bullet 3 > sentence 1",
         lambda: first_sentence(d.bullet(C, "## 에러 핸들링", 3), "C error 3"), "selected",
         "sentence 2 writes over_polish_aborted into final.md")
    frag(proc, "step.6.anchor", "step", C, f"{S4} > bullet 2", lambda: d.bullet(C, S4, 2))
    for n in range(1, 4):
        frag(proc, f"reply.{n}", "output", C, f"{RESP} > {n}", lambda n=n: d.numbered(C, RESP, n))
    for n in range(1, 7):
        if n == 2:
            frag(proc, "check.2", "check", F, f"{CHECK} > 2 > sentence 1",
                 lambda: first_sentence(d.numbered(F, CHECK, 2), "footer check 2"), "selected",
                 "sentence 2 names the orchestrator's verify_change_rate.py")
        else:
            frag(proc, f"check.{n}", "check", F, f"{CHECK} > {n}", lambda n=n: d.numbered(F, CHECK, n))
    for n, g in enumerate("ABCD", 1):
        frag(proc, f"grade.{g}", "grade", F, f"{GRADE} > bullet {n}", lambda n=n: d.bullet(F, GRADE, n))
    frag(proc, "options", "input", B, "## 옵션 (인자 끝에 자연어로) > bullet 1",
         lambda: d.bullet(B, "## 옵션 (인자 끝에 자연어로)", 1))

    for n in range(1, 4):
        frag(tax, f"severity.S{n}", "severity", T, f"## 심각도 기준 > bullet {n}", lambda n=n: d.bullet(T, "## 심각도 기준", n))
    frag(tax, "do-not", "exclusion", H, "bold label **Do-NOT (탐지·윤문 모두 제외):**",
         lambda: d.labeled(H, "**Do-NOT (탐지·윤문 모두 제외):**"))
    # selection = ids present in upstream's generated quick-rules.md at the same commit
    qids = re.findall(r"^- \*\*([A-J]-\d+)\*\*", "\n".join(d.lines(Q)), re.M)
    tlines = d.lines(T)
    cats = {}
    for l in tlines:
        m = re.match(r"^## ([A-J])\. ", l)
        if m:
            cats[m.group(1)] = l
    for cid in sorted(set(q[0] for q in qids), key=lambda c: "ABCDEFGHIJ".index(c)):
        def cat(cid=cid):
            if cid not in cats:
                raise AnchorNotFound(f"{T}: id prefix {cid}. not found")
            return cats[cid]
        frag(tax, f"category.{cid}", "category", T, f"id prefix {cid}.", cat)
    hs = headings(tlines)
    for qid in qids:
        def pattern(qid=qid):
            hl = [(k, i, t) for k, (i, t) in enumerate(hs) if re.match(rf"^#+ {re.escape(qid)}\. ", t)]
            if len(hl) != 1:
                raise AnchorNotFound(f"{T}: id prefix {qid} found {len(hl)} times")
            k, i, t = hl[0]
            end = hs[k + 1][0] if k + 1 < len(hs) else len(tlines)
            meta = [l for l in tlines[i:end] if "_quick:" in l]
            if len(meta) != 1:
                raise AnchorNotFound(f"{T}: {qid} quick meta found {len(meta)} times")
            return t + "\n" + meta[0]
        frag(tax, f"pattern.{qid}", "pattern", T, f"id prefix {qid}", pattern, "selected",
             "heading line + quick meta line only (quick_pattern, quick_fix)")
    return proc, tax, failures


def extract(commit):
    """{normalized relative path: text}, failures."""
    proc, tax, failures = fragments(commit)

    def doc(role, frs, excluded):
        out = [HDR, f"role: {role}", "slot: rewrite", "fragments:"]
        for f in frs:
            out += fragment_lines(f, NAME, commit)
        if excluded:
            out += excluded_lines(excluded)
        return "\n".join(out) + "\n"

    return {"procedure/rewrite.yaml": doc("procedure", proc, EXCLUDED),
            "taxonomy/rewrite.yaml": doc("taxonomy", tax, None)}, failures
