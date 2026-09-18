#!/usr/bin/env python3
"""ko-quality logger (09 §11–§12.1). A hook command: reads one hook payload on stdin, never blocks, never judges.

  python3 ko_quality_log.py <SessionStart|UserPromptSubmit|PostToolUse|Stop|SubagentStop|SessionEnd>

- Records only what a hook payload establishes. A field no hook can establish is null, never guessed from the stamp (§11.1).
- Values that need the exclusion pass (instruction_lang, artifact_lang, usable) are not computed here (S2).
- Standard library only. Never reads transcripts. Spends no tokens.
- State per session, and within a session per agent (`agent_id`, or `main`), in <home>/state/<session_id>.json,
  deleted at SessionEnd (§11.2).
- One record per assistant output: `Stop` (main-to-user) and `SubagentStop` (sub-to-orchestrator), appended to
  <home>/logs/<yyyy-mm>.jsonl. <home> = $KO_QUALITY_HOME with ~ expanded, or ~/.ko-quality (§11.4).
- On Claude Code a subagent's delegation prompt arrives in the `Agent` tool's PostToolUse, after SubagentStop. The sub
  record waits in state for it and is written then, or at the next Stop or SessionEnd without it.
- plugin_present, build_id, tool_version and upstream_versions come from the build stamp `ko-quality.stamp.json` in the
  plugin root ($PLUGIN_ROOT for Codex, $CLAUDE_PLUGIN_ROOT for Claude Code, or the directory above this file).
- Always exits 0 and prints nothing, so a logging failure never changes the session.
"""
import datetime
import hashlib
import json
import os
import re
import sys
import uuid
from pathlib import Path

HOME = Path(os.path.expanduser(os.environ.get("KO_QUALITY_HOME") or "~/.ko-quality"))
SCAN_CAP = 100000  # characters of tool_response scanned per call (10_plan.md §2, L2)
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "apply_patch", "ApplyPatch"}
PROSE_EXT = {".md", ".markdown", ".mdx", ".txt", ".rst", ".adoc", ".org"}
# harness-injected prompts are not tasks (§11.2): a hand-back, and a background agent's completion notice (2.1.274)
INJECTED = ("<agent-message from=", "<task-notification>")
SHIPPED_PREFIX = "ko-quality:"
MARKER = re.compile(r"<!-- ko-quality:begin profile=(\S+) -->")
SKILL_READ = re.compile(r"skills/([A-Za-z0-9_-]+)/SKILL\.md")
HANGUL = re.compile(r"[가-힣]")
LATIN = re.compile(r"[A-Za-z]")
SECRETS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password|passwd)\b\s*[:=]\s*\S+"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    re.compile(r"(?<!\d)\d{6}-[1-8]\d{6}(?!\d)"),                            # 주민등록번호
    re.compile(r"(?<!\d)\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}(?!\d)"),            # card numbers
    re.compile(r"(?<!\d)(?:\+82[- ]?)?0\d{1,2}[- ]\d{3,4}[- ]\d{4}(?!\d)"),  # phone numbers
    re.compile(r"(?<!\d)01[016789]\d{7,8}(?!\d)"),                           # mobile numbers without separators
]
HOME_PATHS = re.compile(r"(?:/Users|/home)/[^/\s\"'`]+")


def stamp():
    for root in (os.environ.get("PLUGIN_ROOT"), os.environ.get("CLAUDE_PLUGIN_ROOT"), str(Path(__file__).resolve().parent.parent)):
        if root and (Path(root) / "ko-quality.stamp.json").exists():
            return json.loads((Path(root) / "ko-quality.stamp.json").read_text(encoding="utf-8"))
    return {}


def mask(text):
    text = text if isinstance(text, str) else ""
    hit = False
    home = str(Path.home())
    if len(home) > 1 and home in text:
        text = text.replace(home, "~"); hit = True
    text, n = HOME_PATHS.subn("~", text)
    hit = hit or n > 0
    for pat in SECRETS:
        text, n = pat.subn("[masked]", text)
        hit = hit or n > 0
    return text, hit


def git_root(cwd):
    p = Path(cwd)
    for d in [p] + list(p.parents):
        if (d / ".git").exists():
            return d
    return None


def project_hash(cwd):
    if not cwd:
        return None
    root = git_root(cwd) or Path(cwd)
    return hashlib.sha256(str(root).encode("utf-8")).hexdigest()[:16]


def state_path(sid):
    return HOME / "state" / f"{re.sub(r'[^A-Za-z0-9_-]', '_', sid)}.json"


def load_state(sid):
    p = state_path(sid)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_state(sid, st):
    p = state_path(sid); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")


def new_agent():
    return {"source_edit": False, "prose_edit": False, "nopath_edit": False, "skills": [], "tool_errors": 0,
            "hangul": 0, "latin": 0, "truncated_calls": 0, "masked": False}


def string_leaves(value):
    """String leaves of a tool response, keys skipped (E4 item 1)."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from string_leaves(v)
    elif isinstance(value, list):
        for v in value:
            yield from string_leaves(v)


def count_output(ag, response):
    budget, truncated = SCAN_CAP, False
    for leaf in string_leaves(response):
        if budget <= 0:
            truncated = True
            break
        part = leaf[:budget]
        truncated = truncated or len(leaf) > budget
        budget -= len(part)
        ag["hangul"] += len(HANGUL.findall(part))
        ag["latin"] += len(LATIN.findall(part))
    if truncated:
        ag["truncated_calls"] += 1


def harness_of(stp, payload, st):
    if stp.get("harness"):
        return stp["harness"]
    if st.get("harness"):
        return st["harness"]
    if "turn_id" in payload:
        return "codex"
    if "prompt_id" in payload:
        return "claude-code"
    return None


def codex_home():
    return Path(os.path.expanduser(os.environ.get("CODEX_HOME") or "~/.codex"))


def between(cwd):
    """cwd and its parents up to the git root (or cwd alone outside a repository), nearest first."""
    if not cwd:
        return []
    p, root = Path(cwd), git_root(cwd)
    if root is None:
        return [p]
    return [d for d in [p] + list(p.parents) if d == root or root in d.parents]


def codex_marker(cwd):
    for d in between(cwd) + [codex_home()]:
        f = d / "AGENTS.md"
        if f.is_file():
            m = MARKER.search(f.read_text(encoding="utf-8", errors="replace"))
            if m:
                return m.group(1)
    return None


def codex_shipped_agents(cwd):
    """Agent names the installer wrote, as `ko_quality_codex.py status` reports them (global and project scope)."""
    names = set()
    places = [(codex_home() / ".ko-quality-install.json", codex_home() / "agents")]
    places += [(d / ".codex" / ".ko-quality-install.json", d / ".codex" / "agents") for d in between(cwd)]
    for manifest, agents_dir in places:
        if manifest.is_file():
            for n in json.loads(manifest.read_text(encoding="utf-8")).get("agents", []):
                if (agents_dir / n).exists():
                    names.add(n[:-5] if n.endswith(".toml") else n)
    return names


def policy_fields(harness, position, agent_type, cwd):
    """(policy_on, injection_point, profile, policy_method) as §11.3 allows a hook to establish them."""
    if position == "sub-to-orchestrator":
        if harness == "codex":
            shipped = agent_type in codex_shipped_agents(cwd)
        else:
            shipped = isinstance(agent_type, str) and agent_type.startswith(SHIPPED_PREFIX)
        return (True, "agent-definition", None, "agent-type") if shipped else (False, "none", None, "agent-type")
    if harness == "codex":
        profile = codex_marker(cwd)
        return (True, "agents-md", profile, "agents-md-marker") if profile else (False, "none", None, "agents-md-marker")
    return (None, None, None, None)


def task_type(harness, ag):
    edited = ag["source_edit"] or ag["prose_edit"] or ag["nopath_edit"]
    if harness == "codex":
        return ("coding" if edited else "conversation"), "rule-codex"
    if ag["source_edit"]:
        return "coding", "rule"
    if ag["nopath_edit"]:
        return "coding", "rule-nopath"
    if ag["prose_edit"]:
        return "document", "rule"
    return "conversation", "rule"


def tokens_estimate(text):
    h = len(HANGUL.findall(text))
    return {"output": round(1.51 * h + 0.34 * (len(text) - h)), "method": "estimate-v2"}


def record(st, stp, harness, position, ag, task, output, agent_type=None, agent_id=None, turn_key=None, masked=False):
    out, m = mask(output)
    policy_on, injection_point, profile, policy_method = policy_fields(harness, position, agent_type, st.get("cwd"))
    ttype, tmethod = task_type(harness, ag)
    return {
        "id": str(uuid.uuid4()),
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "session_id": st.get("session_id"),
        "turn_key": turn_key,
        "project": project_hash(st.get("cwd")),
        "harness": harness,
        "harness_position": position,
        "agent_type": agent_type,
        "agent_id": agent_id,
        "plugin_present": bool(stp),
        "build_id": stp.get("build_id"),
        "tool_version": stp.get("version"),
        "upstream_versions": stp.get("upstream_versions", {}),
        "policy_on": policy_on,
        "injection_point": injection_point,
        "profile": profile,
        "policy_method": policy_method,
        "model": st.get("model") if harness == "codex" else None,
        "task": task or "",
        "output": out,
        "injected_prompts": st.get("injected_prompts", 0) if position == "main-to-user" else 0,
        "skills_invoked": ag["skills"],
        "skills_method": {"claude-code": "tool", "codex": "path-read"}.get(harness),
        "task_type": ttype,
        "task_type_method": tmethod,
        "tool_output_chars": {"hangul": ag["hangul"], "latin": ag["latin"], "truncated_calls": ag["truncated_calls"]},
        "tool_errors": ag["tool_errors"],
        "tokens": tokens_estimate(out),
        "masked": bool(masked or m or ag.get("masked")),
    }


def append(rec):
    now = datetime.datetime.now(datetime.timezone.utc)
    p = HOME / "logs" / f"{now:%Y-%m}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def flush_pending(st, agent_id=None, task=None, task_masked=False):
    """Write waiting sub records: one (with its delegation prompt), or all (without)."""
    pending = st.get("pending", {})
    for aid in ([agent_id] if agent_id is not None else list(pending)):
        rec = pending.pop(aid, None)
        if rec is None:
            continue
        if task is not None:
            rec["task"] = task
            rec["masked"] = rec["masked"] or task_masked
        append(rec)


def text_of(value):
    return value if isinstance(value, str) else ""


def handle(event, payload):
    if not isinstance(payload, dict):
        return
    sid = payload.get("session_id")
    if not isinstance(sid, str) or not sid:
        return
    st = load_state(sid)
    st["session_id"] = sid
    stp = stamp()
    harness = harness_of(stp, payload, st)
    st["harness"] = harness
    if isinstance(payload.get("cwd"), str):
        st["cwd"] = payload["cwd"]
    if isinstance(payload.get("model"), str):
        st["model"] = payload["model"]
    agents = st.setdefault("agents", {})
    turn_key = payload.get("prompt_id") or payload.get("turn_id")

    if event == "SessionStart":
        pass
    elif event == "UserPromptSubmit":
        prompt = text_of(payload.get("prompt"))
        if prompt.startswith(INJECTED):
            st["injected_prompts"] = st.get("injected_prompts", 0) + 1
        else:
            st["task"], st["task_masked"] = mask(prompt)
            st["turn_key"] = turn_key
            st["injected_prompts"] = 0
            agents["main"] = new_agent()
    elif event == "PostToolUse":
        aid = payload.get("agent_id")
        key = aid if isinstance(aid, str) and aid else "main"
        ag = agents.setdefault(key, new_agent())
        tool = payload.get("tool_name")
        tin = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else {}
        resp = payload.get("tool_response")
        if tool in EDIT_TOOLS:
            path = tin.get("file_path") or tin.get("notebook_path")
            if not isinstance(path, str) or not path:
                ag["nopath_edit"] = True
            elif Path(path).suffix.lower() in PROSE_EXT:
                ag["prose_edit"] = True
            else:
                ag["source_edit"] = True
        if tool == "Skill" and isinstance(tin.get("skill"), str):
            ag["skills"].append(tin["skill"])
        if harness == "codex":
            for name in SKILL_READ.findall(json.dumps(tin, ensure_ascii=False)):
                if name not in ag["skills"]:
                    ag["skills"].append(name)
        if isinstance(resp, dict) and (resp.get("is_error") or resp.get("error")):
            ag["tool_errors"] += 1
        count_output(ag, resp)
        if tool == "SubagentHandback" and key != "main":
            st.setdefault("handbacks", {})[key] = mask(text_of(tin.get("message")))
        if tool == "Agent" and isinstance(resp, dict) and isinstance(resp.get("agentId"), str):
            task, m = mask(text_of(tin.get("prompt")))
            if resp["agentId"] in st.get("pending", {}):
                flush_pending(st, resp["agentId"], task, m)
            else:
                st.setdefault("delegations", {})[resp["agentId"]] = [task, m]
    elif event == "SubagentStop":
        aid = payload.get("agent_id")
        key = aid if isinstance(aid, str) and aid else None
        ag = agents.pop(key, None) or new_agent() if key else new_agent()
        handback = st.get("handbacks", {}).pop(key, None) if key else None
        output = handback[0] if handback else text_of(payload.get("last_assistant_message"))
        if output:
            deleg = st.get("delegations", {}).pop(key, None) if key else None
            agent_type = payload.get("agent_type") if isinstance(payload.get("agent_type"), str) else None
            rec = record(st, stp, harness, "sub-to-orchestrator", ag, deleg[0] if deleg else "", output, agent_type, key,
                         turn_key or st.get("turn_key"), bool(handback and handback[1]) or bool(deleg and deleg[1]))
            if deleg or harness != "claude-code" or key is None:
                append(rec)
            else:
                st.setdefault("pending", {})[key] = rec
    elif event == "Stop":
        flush_pending(st)
        output = text_of(payload.get("last_assistant_message"))
        if output:
            ag = agents.get("main") or new_agent()
            append(record(st, stp, harness, "main-to-user", ag, st.get("task"), output, None, None,
                          st.get("turn_key") or turn_key, st.get("task_masked", False)))
    elif event == "SessionEnd":
        flush_pending(st)
        p = state_path(sid)
        if p.exists():
            p.unlink()
        return
    else:
        return
    save_state(sid, st)


def main():
    try:
        event = sys.argv[1] if len(sys.argv) > 1 else ""
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        handle(event or (payload.get("hook_event_name", "") if isinstance(payload, dict) else ""), payload)
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
