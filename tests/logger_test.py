#!/usr/bin/env python3
"""Offline test for logger/ko_quality_log.py against 09 §11–§12.1 (no harness). Run from the repository root.

Two kinds of input:
- replays: the event sequences recorded in tests/runs/02-spec/hook-payloads.json (Claude Code 2.1.273, a delegation
  whose report travels through SubagentHandback) and tests/runs/99-retest/codex-channels.json (Codex 0.154.0, runs r1
  and a1-1). Each payload has exactly the recorded keys; values are synthetic, filled by key name.
- scenarios: hand-written payloads for what the recordings do not exercise (paths, skills, truncation, masking,
  Codex marker and installer manifest, malformed input).
Every payload value here is synthetic. No real text.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGGER = ROOT / "logger/ko_quality_log.py"
KO = ("이번 배포에서는 캐시 무효화 시점을 조정했습니다. 사용자 요청이 몰리는 시간에도 응답 지연이 늘지 않도록 "
      "만료 시간을 짧게 두고, 갱신은 백그라운드에서 처리하도록 바꾸었습니다. 다음 주에는 실제 트래픽에서 "
      "지연 시간이 어떻게 달라졌는지 확인하고 결과를 공유하겠습니다.")
STUB = "I sent my report to the agent that started me."
REQUIRED = {"id", "ts", "session_id", "turn_key", "project", "harness", "harness_position", "agent_type", "agent_id",
            "plugin_present", "build_id", "tool_version", "upstream_versions", "policy_on", "injection_point", "profile",
            "policy_method", "model", "task", "output", "injected_prompts", "skills_invoked", "skills_method", "task_type",
            "task_type_method", "tool_output_chars", "tool_errors", "tokens", "masked"}
GONE = {"preset", "instruction_lang", "artifact_lang", "usable", "upstream_report", "expect",
        "gate_on", "gate_fired", "gate_retries", "gate_fired_on"}
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


class Env:
    def __init__(self, tmp, harness="claude-code", stamp=True):
        self.tmp = tmp
        self.home = tmp / "home"
        self.userhome = tmp / "userhome"; self.userhome.mkdir(exist_ok=True)
        self.plugin = tmp / "plugin"; self.plugin.mkdir(exist_ok=True)
        self.codex_home = tmp / "codex-home"; self.codex_home.mkdir(exist_ok=True)
        self.project = tmp / "project"; (self.project / ".git").mkdir(parents=True, exist_ok=True)
        self.cwd = self.project / "sub"; self.cwd.mkdir(exist_ok=True)
        if stamp:
            data = {"tool": "ko-quality", "version": "0.2.0", "plugin": "ko-quality", "harness": harness,
                    "upstream_versions": {"im-not-ai": "9747f03"}, "build_id": "0123456789abcdef"}
            if harness == "codex":
                data["profile"] = "agent-reply"
            (self.plugin / "ko-quality.stamp.json").write_text(json.dumps(data), encoding="utf-8")

    def call(self, event, payload, raw=None, home_value=None):
        env = dict(os.environ, KO_QUALITY_HOME=home_value or str(self.home), HOME=str(self.userhome),
                   CODEX_HOME=str(self.codex_home))
        env.pop("PLUGIN_ROOT", None)
        env["CLAUDE_PLUGIN_ROOT"] = str(self.plugin)
        data = raw if raw is not None else json.dumps(payload, ensure_ascii=False)
        r = subprocess.run([sys.executable, str(LOGGER), event], input=data, env=env, capture_output=True, text=True)
        check(r.returncode == 0 and r.stdout == "" and r.stderr == "", f"{event}: exit {r.returncode}, stdout {r.stdout!r}, stderr {r.stderr[:200]!r}")

    def records(self, home=None):
        logs = sorted(((home or self.home) / "logs").glob("*.jsonl"))
        return [json.loads(l) for p in logs for l in p.read_text(encoding="utf-8").splitlines()]


def fill(key, ev, env, sid, i):
    """A synthetic value for a recorded key."""
    tool = ev.get("tool_name")
    values = {
        "session_id": sid, "cwd": str(env.cwd), "hook_event_name": ev["event"], "transcript_path": "/tmp/t.jsonl",
        "agent_transcript_path": "/tmp/a.jsonl", "source": "startup", "permission_mode": "default", "reason": "other",
        "prompt_id": "prompt-1", "turn_id": "turn-1", "tool_use_id": f"tool-{i}", "effort": "high",
        "duration_ms": 10, "stop_hook_active": False, "background_tasks": [], "session_crons": [],
        "model": "gpt-5.6-luna", "agent_id": "agent-1", "agent_type": ev.get("agent_type"), "tool_name": tool,
    }
    if key in values:
        return values[key]
    if key == "prompt":
        head = ev.get("prompt_head") or "리스트와 튜플의 차이를 설명해 줘."
        return head + (" 보고입니다." if head.startswith("<agent-message") else "")
    if key == "last_assistant_message":
        head = ev.get("last_assistant_message_head")
        if ev["event"] == "SubagentStop" and head == STUB:
            return STUB
        return (head or "") + "\n\n" + KO
    if key == "tool_input":
        if tool == "SubagentHandback":
            return {"message": "HANDBACK-REPORT " + KO}
        if tool == "Agent":
            return {"description": "review", "prompt": "DELEGATION-PROMPT 이 문장을 검토해 줘.", "subagent_type": "general-purpose"}
        if tool == "Bash":
            return {"command": "echo hi"}
        return {}
    if key == "tool_response":
        if tool == "Agent":
            return {"status": "completed", "agentId": "agent-1", "agentType": "general-purpose",
                    "content": [{"type": "text", "text": "hi"}], "totalTokens": 100}
        if tool == "Bash":
            return {"stdout": "hi 안녕", "stderr": "", "interrupted": False}
        return {"ok": True}
    return None


def replay(env, events, sid):
    for i, ev in enumerate(events):
        payload = {k: fill(k, ev, env, sid, i) for k in ev["keys"]}
        env.call(ev["event"], payload)


def test_claude_code_replay(tmp):
    env = Env(tmp)
    events = json.loads((ROOT / "tests/runs/02-spec/hook-payloads.json").read_text(encoding="utf-8"))["events"]
    replay(env, events, "cc-replay")
    recs = env.records()
    check(len(recs) == 2, f"cc replay: expected 2 records, got {len(recs)}")
    sub = next((r for r in recs if r["harness_position"] == "sub-to-orchestrator"), {})
    main = next((r for r in recs if r["harness_position"] == "main-to-user"), {})
    check(sub.get("output", "").startswith("HANDBACK-REPORT"), "cc replay: sub output is the SubagentHandback message, not the stub")
    check(sub.get("task", "").startswith("DELEGATION-PROMPT"), "cc replay: sub task is the Agent tool's delegation prompt")
    check(sub.get("agent_id") == "agent-1" and sub.get("agent_type") == "general-purpose", "cc replay: sub agent_id and agent_type")
    check((sub.get("policy_on"), sub.get("injection_point"), sub.get("profile"), sub.get("policy_method")) == (False, "none", None, "agent-type"),
          "cc replay: non-shipped sub agent → policy_on false, none, null, agent-type (§11.3)")
    check(main.get("injected_prompts") == 1, "cc replay: the <agent-message from= prompt is counted in injected_prompts")
    check(main.get("task") == "Use the Agent tool with subagent_type general-purpose, and t", "cc replay: injected prompt does not overwrite task")
    check(main.get("tool_output_chars", {}).get("latin", -1) >= 0, "cc replay: tool_output_chars present")
    check(sub.get("tool_output_chars", {}).get("hangul") == 2 and main.get("tool_output_chars", {}).get("hangul") == 0,
          "cc replay: the subagent's Bash output is counted in the sub record only")
    check((main.get("policy_on"), main.get("injection_point"), main.get("profile"), main.get("policy_method")) == (None, None, None, None),
          "cc replay: Claude Code main record leaves policy_on, injection_point, profile, policy_method null (§11.3)")
    check(main.get("model") is None and sub.get("model") is None, "cc replay: model null on Claude Code")
    check(main.get("turn_key") == "prompt-1", "cc replay: turn_key is the task's prompt_id")
    check(all(r.get("plugin_present") is True and r.get("build_id") == "0123456789abcdef" and r.get("tool_version") == "0.2.0" for r in recs),
          "cc replay: plugin_present, build_id, tool_version from the stamp")
    check(all(r.get("harness") == "claude-code" and r.get("session_id") == "cc-replay" for r in recs), "cc replay: harness and session_id")
    project = hashlib.sha256(str(env.project).encode("utf-8")).hexdigest()[:16]
    check(all(r.get("project") == project for r in recs), "cc replay: project is the hash of the git root above cwd")
    check(all(REQUIRED <= set(r) and not (GONE & set(r)) for r in recs), f"cc replay: §12.1 keys exactly (missing {REQUIRED - set(recs[0]) if recs else '?'}, extra {GONE & set(recs[0]) if recs else '?'})")
    check(not (env.home / "state" / "cc-replay.json").exists(), "cc replay: state removed at SessionEnd")
    check(sorted(p.name for p in (env.home / "logs").iterdir()) == sorted({p.name for p in (env.home / "logs").glob("*.jsonl")}),
          "cc replay: logs/ holds monthly files only, no per-profile split")


def test_codex_replay(tmp):
    env = Env(tmp, harness="codex")
    runs = {r["id"]: r for r in json.loads((ROOT / "tests/runs/99-retest/codex-channels.json").read_text(encoding="utf-8"))["runs"]}
    # installed as the retest had it: section in global AGENTS.md, agents written by the installer
    (env.codex_home / "AGENTS.md").write_text("# mine\n\n<!-- ko-quality:begin profile=agent-reply -->\n정책\n<!-- ko-quality:end -->\n", encoding="utf-8")
    (env.codex_home / "agents").mkdir()
    (env.codex_home / "agents" / "korean-reviewer.toml").write_text('name = "korean-reviewer"\n', encoding="utf-8")
    (env.codex_home / ".ko-quality-install.json").write_text(json.dumps({"agents": ["korean-reviewer.toml"], "created_agents_md": False}), encoding="utf-8")
    replay(env, runs["a1-1"]["hook_payloads"], "cx-a1")
    replay(env, runs["r1"]["hook_payloads"], "cx-r1")
    recs = env.records()
    a1 = [r for r in recs if r["session_id"] == "cx-a1"]
    r1 = [r for r in recs if r["session_id"] == "cx-r1"]
    check(len(a1) == 2 and len(r1) == 1, f"codex replay: expected 2 + 1 records, got {len(a1)} + {len(r1)}")
    sub = next((r for r in a1 if r["harness_position"] == "sub-to-orchestrator"), {})
    main = next((r for r in a1 if r["harness_position"] == "main-to-user"), {})
    check(sub.get("output", "").startswith("CODEX-CANARY-AGENT-8081"), "codex replay: sub output is SubagentStop's own message")
    check((sub.get("policy_on"), sub.get("injection_point"), sub.get("profile"), sub.get("policy_method")) == (True, "agent-definition", None, "agent-type"),
          "codex replay: installer-written agent → policy_on true, agent-definition, profile null (§11.3)")
    check((main.get("policy_on"), main.get("injection_point"), main.get("profile"), main.get("policy_method")) == (True, "agents-md", "agent-reply", "agents-md-marker"),
          "codex replay: marker in global AGENTS.md → policy_on true, agents-md, marker profile")
    check(main.get("tool_output_chars", {}).get("hangul") == 2 and sub.get("tool_output_chars", {}).get("hangul") == 8,
          "codex replay: subagent Bash outputs counted in the sub record, main's own in main")
    check(all(r.get("model") == "gpt-5.6-luna" and r.get("harness") == "codex" for r in recs), "codex replay: model from the payload, harness codex")
    check(all(r.get("task_type") == "conversation" and r.get("task_type_method") == "rule-codex" for r in recs), "codex replay: two-value task_type, rule-codex")
    check(all(r.get("turn_key") == "turn-1" and r.get("skills_method") == "path-read" for r in recs), "codex replay: turn_key from turn_id, skills_method path-read")
    check(all(REQUIRED <= set(r) and not (GONE & set(r)) for r in recs), "codex replay: §12.1 keys exactly")


def test_scenarios(tmp):
    env = Env(tmp)
    sid = "cc-s"
    P = lambda **k: dict(session_id=sid, cwd=str(env.cwd), **k)
    env.call("SessionStart", P(source="startup"))
    env.call("UserPromptSubmit", P(prompt="문서를 정리해 줘. 연락처 010-1234-5678, 주민번호 900101-1234567, 카드 1234-5678-9012-3456, 경로 "
                                   + str(env.userhome) + "/notes/a.md, /Users/someone/x.txt", prompt_id="p-1"))
    env.call("PostToolUse", P(tool_name="Skill", tool_input={"skill": "ko-quality:ko-rewrite"}, tool_response={"success": True}, prompt_id="p-1"))
    env.call("PostToolUse", P(tool_name="Write", tool_input={"file_path": str(env.cwd / "notes.md"), "content": "x"},
                              tool_response={"type": "create"}, prompt_id="p-1"))
    env.call("PostToolUse", P(tool_name="Read", tool_input={"file_path": "big.txt"}, tool_response={"file": {"content": "가" * 60000 + "a" * 60000}}, prompt_id="p-1"))
    env.call("PostToolUse", P(tool_name="Bash", tool_input={"command": "false"}, tool_response={"is_error": True, "stderr": "boom"}, prompt_id="p-1"))
    # a subagent edits source; it must not make the main turn coding
    env.call("PostToolUse", P(tool_name="Edit", agent_id="ag-2", agent_type="ko-quality:korean-editor",
                              tool_input={"file_path": "src/app.py"}, tool_response={}, prompt_id="p-1"))
    # era 01 route: real text in SubagentStop, no hand-back and no Agent PostToolUse before Stop
    env.call("SubagentStop", P(agent_id="ag-2", agent_type="ko-quality:korean-editor", last_assistant_message=KO, prompt_id="p-1"))
    env.call("Stop", P(last_assistant_message="정리했습니다. " + KO, prompt_id="p-1"))
    # second turn: nopath edit
    env.call("UserPromptSubmit", P(prompt="고쳐 줘", prompt_id="p-2"))
    env.call("PostToolUse", P(tool_name="Edit", tool_input={}, tool_response={}, prompt_id="p-2"))
    env.call("Stop", P(last_assistant_message="고쳤습니다.", prompt_id="p-2"))
    # a background agent's completion notice is injected, not a task (2.1.274)
    env.call("UserPromptSubmit", P(prompt="<task-notification>\n<task-id>ag-9</task-id>\n</task-notification>", prompt_id="p-3"))
    env.call("Stop", P(last_assistant_message="이미 전했습니다.", prompt_id="p-3"))
    env.call("SessionEnd", P(reason="other"))
    recs = env.records()
    check(len(recs) == 4, f"scenarios: expected 4 records, got {len(recs)}")
    sub = next((r for r in recs if r["harness_position"] == "sub-to-orchestrator"), {})
    m1 = next((r for r in recs if r["harness_position"] == "main-to-user" and r["turn_key"] == "p-1"), {})
    m2 = next((r for r in recs if r["harness_position"] == "main-to-user" and r["turn_key"] == "p-2" and r["injected_prompts"] == 0), {})
    m3 = next((r for r in recs if r["harness_position"] == "main-to-user" and r["injected_prompts"] == 1), {})
    check(sub.get("output") == KO and sub.get("task") == "", "scenarios: sub without hand-back keeps SubagentStop text; no delegation prompt → empty task")
    check((sub.get("policy_on"), sub.get("injection_point"), sub.get("task_type")) == (True, "agent-definition", "coding"), "scenarios: shipped sub agent, its own source edit")
    check((m1.get("task_type"), m1.get("task_type_method")) == ("document", "rule"), "scenarios: prose-only edit → document (subagent's .py edit excluded)")
    check((m2.get("task_type"), m2.get("task_type_method")) == ("coding", "rule-nopath"), "scenarios: edit without path → coding, rule-nopath")
    check(m1.get("skills_invoked") == ["ko-quality:ko-rewrite"] and m1.get("skills_method") == "tool", "scenarios: Skill tool input → skills_invoked")
    toc = m1.get("tool_output_chars", {})
    check(toc.get("truncated_calls") == 1 and toc.get("hangul") == 60000 and toc.get("latin") == 40000 + len("create") + len("boom"), f"scenarios: 100,000-character scan cap per call ({toc})")
    check(m1.get("tool_errors") == 1, "scenarios: tool error counted")
    t = m1.get("task", "")
    check(all(s not in t for s in ("010-1234-5678", "900101-1234567", "1234-5678-9012-3456", str(env.userhome), "/Users/someone")) and m1.get("masked") is True,
          f"scenarios: phone, 주민등록번호, card and home paths masked ({t!r})")
    check("~/notes/a.md" in t, "scenarios: a home path keeps its tail after the home directory")
    check(m1.get("tokens") == {"output": round(1.51 * sum(1 for c in m1.get("output", "") if "가" <= c <= "힣") + 0.34 * sum(1 for c in m1.get("output", "") if not "가" <= c <= "힣")), "method": "estimate-v2"},
          "scenarios: tokens estimate-v2")
    check(m3.get("task") == "고쳐 줘" and m3.get("turn_key") == "p-2", "scenarios: a <task-notification> prompt is counted, and does not overwrite task or turn_key")
    check(m2.get("injected_prompts") == 0 and m2.get("skills_invoked") == [] and m2.get("tool_errors") == 0, "scenarios: per-turn counters reset at the next task")


def test_codex_scenarios(tmp):
    env = Env(tmp, harness="codex")
    sid = "cx-s"
    P = lambda **k: dict(session_id=sid, cwd=str(env.cwd), model="gpt-5.6-terra", **k)
    env.call("SessionStart", P(source="startup"))
    env.call("UserPromptSubmit", P(prompt="윤문해 줘", turn_id="t-1"))
    env.call("PostToolUse", P(tool_name="Bash", tool_input={"command": "sed -n 1,200p /x/plugins/ko-quality/skills/ko-rewrite/SKILL.md"},
                              tool_response="…", turn_id="t-1"))
    env.call("PostToolUse", P(tool_name="apply_patch", tool_input={"patch": "*** Begin Patch"}, tool_response="ok", turn_id="t-1"))
    env.call("SubagentStop", P(agent_id="x-1", agent_type="worker", last_assistant_message="done", turn_id="t-1"))
    env.call("Stop", P(last_assistant_message="고쳤습니다.", turn_id="t-1"))
    recs = env.records()
    main = next((r for r in recs if r["harness_position"] == "main-to-user"), {})
    sub = next((r for r in recs if r["harness_position"] == "sub-to-orchestrator"), {})
    check(main.get("skills_invoked") == ["ko-rewrite"] and main.get("skills_method") == "path-read", "codex scenarios: SKILL.md shell read → skills_invoked")
    check((main.get("task_type"), main.get("task_type_method")) == ("coding", "rule-codex"), "codex scenarios: apply_patch → coding, rule-codex")
    check((main.get("policy_on"), main.get("injection_point"), main.get("profile")) == (False, "none", None), "codex scenarios: no marker → policy_on false")
    check((sub.get("policy_on"), sub.get("injection_point")) == (False, "none"), "codex scenarios: agent not written by the installer → policy_on false")
    # project AGENTS.md between cwd and the git root
    (env.project / "AGENTS.md").write_text("<!-- ko-quality:begin profile=formal-report -->\n정책\n<!-- ko-quality:end -->\n", encoding="utf-8")
    env.call("UserPromptSubmit", P(prompt="다시", turn_id="t-2"))
    env.call("Stop", P(last_assistant_message="네.", turn_id="t-2"))
    main2 = [r for r in env.records() if r["turn_key"] == "t-2"]
    check(main2 and (main2[0]["policy_on"], main2[0]["profile"]) == (True, "formal-report"), "codex scenarios: marker in project AGENTS.md above cwd")


def test_edges(tmp):
    # no stamp → plugin_present false
    for d in ("nostamp", "tilde", "bad"):
        (tmp / d).mkdir()
    env = Env(tmp / "nostamp", stamp=False)
    env.call("UserPromptSubmit", {"session_id": "n", "cwd": str(env.cwd), "prompt": "안녕", "prompt_id": "p"})
    env.call("Stop", {"session_id": "n", "cwd": str(env.cwd), "last_assistant_message": "안녕하세요", "prompt_id": "p"})
    recs = env.records()
    check(len(recs) == 1 and recs[0]["plugin_present"] is False and recs[0]["build_id"] is None and recs[0]["harness"] == "claude-code",
          "edges: no stamp → plugin_present false, build_id null, harness inferred from prompt_id")
    # expanduser on KO_QUALITY_HOME
    env2 = Env(tmp / "tilde")
    env2.call("UserPromptSubmit", {"session_id": "t", "cwd": str(env2.cwd), "prompt": "안녕", "prompt_id": "p"}, home_value="~/.kq-dev")
    env2.call("Stop", {"session_id": "t", "cwd": str(env2.cwd), "last_assistant_message": "네", "prompt_id": "p"}, home_value="~/.kq-dev")
    check(len(env2.records(env2.userhome / ".kq-dev")) == 1 and not (env2.cwd / "~").exists() and not (Path.cwd() / "~").exists(),
          "edges: KO_QUALITY_HOME '~/…' is expanded")
    # malformed payloads: exit 0, print nothing, write no record
    env3 = Env(tmp / "bad")
    env3.call("Stop", None, raw='{"session_id": "b", "last_assistant_mess')
    env3.call("Stop", {})
    env3.call("PostToolUse", {"session_id": "b", "tool_response": None})
    env3.call("NoSuchEvent", {"session_id": "b"})
    env3.call("", None, raw="not json at all")
    env3.call("SubagentStop", {"session_id": "b", "agent_id": 5, "last_assistant_message": ["x"]})
    check(env3.records() == [], "edges: malformed payloads write no record")


def main():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        for name, fn in [("cc", test_claude_code_replay), ("cx", test_codex_replay), ("sc", test_scenarios),
                         ("cxs", test_codex_scenarios), ("edges", test_edges)]:
            d = t / name; d.mkdir()
            fn(d)
    for f in failures:
        print("FAIL", f)
    print(f"logger test: {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
