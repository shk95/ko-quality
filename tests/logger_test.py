#!/usr/bin/env python3
"""Offline test for logger/ko_quality_log.py with synthetic hook payloads (no harness). Run from the repository root."""
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


def call(home, plugin_root, event, payload):
    env = dict(os.environ, KO_QUALITY_HOME=str(home), CLAUDE_PLUGIN_ROOT=str(plugin_root))
    env.pop("PLUGIN_ROOT", None)
    r = subprocess.run([sys.executable, str(LOGGER), event], input=json.dumps(payload, ensure_ascii=False),
                       env=env, capture_output=True, text=True)
    assert r.returncode == 0 and r.stdout == "", (event, r.returncode, r.stdout, r.stderr)


def main():
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp); home = tmp / "home"; plugin = tmp / "plugin"; plugin.mkdir()
        (plugin / "ko-quality.stamp.json").write_text(json.dumps({"profile": "agent-reply", "harness": "claude-code",
            "injection_point": "output-style", "upstream_versions": {"im-not-ai": "9747f03"}}), encoding="utf-8")
        sid = "s-1"
        call(home, plugin, "SessionStart", {"session_id": sid, "model": "test-model"})
        call(home, plugin, "UserPromptSubmit", {"session_id": sid, "prompt": "배포 결과를 정리해줘. token=abcd1234secret"})
        call(home, plugin, "PostToolUse", {"session_id": sid, "tool_name": "Edit", "tool_response": {"is_error": False}})
        call(home, plugin, "SubagentStop", {"session_id": sid, "agent_type": "ko-quality:korean-reviewer", "last_assistant_message": KO})
        call(home, plugin, "Stop", {"session_id": sid, "last_assistant_message": "짧은 답입니다."})
        call(home, plugin, "SessionEnd", {"session_id": sid})
        call(home, plugin, "Stop", {})  # malformed payload: must still exit 0 silently
        logs = sorted((home / "logs" / "agent-reply").glob("*.jsonl"))
        recs = [json.loads(l) for p in logs for l in p.read_text(encoding="utf-8").splitlines()]
        def check(cond, msg):
            if not cond:
                failures.append(msg)
        check(len(recs) == 2, f"expected 2 records, got {len(recs)}")
        sub = next((r for r in recs if r["harness_position"] == "sub-to-orchestrator"), None)
        main_ = next((r for r in recs if r["harness_position"] == "main-to-user"), None)
        check(sub and sub["agent_type"] == "ko-quality:korean-reviewer", "subagent record agent_type")
        check(sub and sub["usable"] is True, "long Korean output is usable")
        check(main_ and main_["usable"] is False, "short output is not usable")
        check(all(r["profile"] == "agent-reply" and r["harness"] == "claude-code" for r in recs), "profile and harness from stamp")
        check(all(r["upstream_versions"] == {"im-not-ai": "9747f03"} for r in recs), "upstream_versions from stamp")
        check(all(r["model"] == "test-model" for r in recs), "model from SessionStart")
        check(all(r["task_type"] == "coding" and r["task_type_method"] == "rule" for r in recs), "task_type rule")
        check(all("abcd1234secret" not in r["task"] and r["masked"] for r in recs), "secret masked")
        check(all(r["tokens"]["method"] == "estimate" for r in recs), "tokens estimate")
        check(not (home / "state" / "s-1.json").exists(), "state removed at SessionEnd")
        check(all(set(r) >= {"id", "ts", "profile", "policy_on", "injection_point", "upstream_versions", "model",
                             "instruction_lang", "artifact_lang", "harness", "harness_position", "task", "task_type",
                             "output", "tokens", "usable", "expect"} for r in recs), "06 §11.3 fields present")
    for f in failures:
        print("FAIL", f)
    print(f"logger test: {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
