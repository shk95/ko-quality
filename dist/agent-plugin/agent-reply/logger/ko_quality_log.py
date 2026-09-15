#!/usr/bin/env python3
"""ko-quality minimal logger (06 §11). A hook command: reads one hook payload on stdin, never blocks, never judges.

  python3 ko_quality_log.py <SessionStart|UserPromptSubmit|PostToolUse|Stop|SubagentStop|SessionEnd>

- Assembles records from hook input only; never reads the transcript (06 §2.3).
- One record per assistant output: `Stop` (main-to-user) and `SubagentStop` (sub-to-orchestrator). Session state between
  events lives in <home>/state/<session_id>.json and is removed at SessionEnd.
- Records: <home>/logs/<profile>/<yyyy-mm>.jsonl, <home> = $KO_QUALITY_HOME or ~/.ko-quality (outside any work tree).
- profile, harness and upstream_versions come from the build stamp `ko-quality.stamp.json` in the plugin root
  ($PLUGIN_ROOT for Codex, $CLAUDE_PLUGIN_ROOT for Claude Code, or the directory above this file).
- Always exits 0 and prints nothing, so a logging failure never changes the session.
"""
import datetime
import json
import os
import re
import sys
import uuid
from pathlib import Path

HOME = Path(os.environ.get("KO_QUALITY_HOME") or Path.home() / ".ko-quality")
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch", "ApplyPatch"}
HANGUL = re.compile(r"[가-힣]")
LATIN = re.compile(r"[A-Za-z]")
SECRETS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password|passwd)\b\s*[:=]\s*\S+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
]


def stamp():
    for root in (os.environ.get("PLUGIN_ROOT"), os.environ.get("CLAUDE_PLUGIN_ROOT"), str(Path(__file__).resolve().parent.parent)):
        if root and (Path(root) / "ko-quality.stamp.json").exists():
            return json.loads((Path(root) / "ko-quality.stamp.json").read_text(encoding="utf-8"))
    return {}


def mask(text):
    hit = False
    for pat in SECRETS:
        text, n = pat.subn("[masked]", text)
        hit = hit or n > 0
    return text, hit


def lang(text):
    h, l = len(HANGUL.findall(text or "")), len(LATIN.findall(text or ""))
    if h + l == 0:
        return "mixed"
    r = h / (h + l)
    return "ko" if r >= 0.7 else "en" if r <= 0.3 else "mixed"


def korean_prose(text):
    """Drop fenced code and quote blocks; keep prose lines (06 §13.1 output purity)."""
    text = re.sub(r"```.*?```", "", text or "", flags=re.S)
    return "\n".join(l for l in text.split("\n") if not l.lstrip().startswith(">"))


def usable(text):
    prose = korean_prose(text)
    eojeol = [w for w in prose.split() if HANGUL.search(w)]
    return len(eojeol) >= 20


def state_path(sid):
    return HOME / "state" / f"{re.sub(r'[^A-Za-z0-9_-]', '_', sid)}.json"


def load_state(sid):
    p = state_path(sid)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_state(sid, st):
    p = state_path(sid); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")


def record(st, stp, output, position, agent_type):
    task, m1 = mask(st.get("task") or "")
    out, m2 = mask(output or "")
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "id": str(uuid.uuid4()),
        "ts": now.isoformat(timespec="seconds"),
        "profile": stp.get("profile", "unknown"),
        "preset": None,
        "policy_on": bool(stp),
        "injection_point": stp.get("injection_point", "unknown") if position == "main-to-user" else "agent-definition" if stp else "unknown",
        "upstream_versions": stp.get("upstream_versions", {}),
        "model": st.get("model") or "unknown",
        "instruction_lang": lang(st.get("task")),
        "artifact_lang": lang(korean_prose(output)),
        "harness": stp.get("harness", "unknown"),
        "harness_position": position,
        "agent_type": agent_type,
        "task": task,
        "task_type": "coding" if st.get("edit_tools") else "writing" if st.get("task") else None,
        "task_type_method": "rule",
        "output": out,
        "tokens": {"output": round(len(output or "") / 2.5), "method": "estimate"},
        "upstream_report": None,
        "usable": usable(output),
        "masked": m1 or m2,
        "expect": None,
    }


def append(rec):
    now = datetime.datetime.now(datetime.timezone.utc)
    p = HOME / "logs" / rec["profile"] / f"{now:%Y-%m}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def handle(event, payload):
    sid = payload.get("session_id") or "unknown"
    st = load_state(sid)
    stp = stamp()
    if event == "SessionStart":
        st = {"model": payload.get("model"), "tool_errors": 0, "edit_tools": False}
    elif event == "UserPromptSubmit":
        st["task"] = payload.get("prompt") or payload.get("user_prompt") or ""
        st["edit_tools"] = False
        st.setdefault("model", payload.get("model"))
    elif event == "PostToolUse":
        if payload.get("tool_name") in EDIT_TOOLS:
            st["edit_tools"] = True
        resp = payload.get("tool_response")
        if isinstance(resp, dict) and (resp.get("is_error") or resp.get("error")):
            st["tool_errors"] = st.get("tool_errors", 0) + 1
    elif event in ("Stop", "SubagentStop"):
        position = "main-to-user" if event == "Stop" else "sub-to-orchestrator"
        output = payload.get("last_assistant_message") or ""
        if output:
            append(record(st, stp, output, position, payload.get("agent_type") if event == "SubagentStop" else None))
        if payload.get("model"):
            st["model"] = payload.get("model")
    elif event == "SessionEnd":
        p = state_path(sid)
        if p.exists():
            p.unlink()
        return
    save_state(sid, st)


def main():
    try:
        event = sys.argv[1] if len(sys.argv) > 1 else ""
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        handle(event or payload.get("hook_event_name", ""), payload)
    except Exception as exc:  # never break the session; leave a trace for debugging
        try:
            p = HOME / "logger-errors.log"; p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now().isoformat()} {type(exc).__name__}: {exc}\n")
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
