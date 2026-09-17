"""Headless corpus generator (09 §18.2, §12.2). Standard library only.

  python3 -m corpus run --batch <id> --home <corpus home> --work <scratch dir> [--arms A,B,C] [--prompts set-1.json]
                        [--per-stratum 3] [--ceiling-usd 21] [--spent-usd 0]
  python3 -m corpus canary --batch <id> --home <canary home> --work <scratch dir> [--mislabel]

One session per (prompt, arm), sequential, through the shipped logger:

  arm A  a logger-only plugin: the shipped hooks and logger, no stamp, no styles, skills or agents. Nothing else of
         ours loads, so plugin_present is false, and the logger still writes the record (09 §12.1, 05 §plugin_present)
  arm B  a copy of the built plugin, no style selected
  arm C  the same copy with a style selected in the project's settings.local.json; after the first prompt the session
         switches to the other profile with /output-style (stream-json input) and takes the next prompt of the stratum

Each session runs in a fresh scratch project (the fixture project copied in), so no arm inherits another's selection
(§18.2). The generator reads the stream: `init.output_style` is checked against the arm on every turn, and per-turn
`result` events give usage and cost. After the session it reads its own session's main records from logs/ (read only)
to learn each turn's `turn_key`, and appends one annotation per turn to annotations/ (its only file kind, §11.4).
"""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist" / "claude-code" / "ko-quality"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "project"
PROMPTS = Path(__file__).resolve().parent / "prompts" / "set-1.json"
MODEL = "claude-sonnet-5"                                   # flow.md F4
PROFILES = ("agent-reply", "formal-report")
STYLE = {p: f"ko-quality:{p}" for p in PROFILES}
DEFAULT_STYLE = "default"
MAX_TURNS = 8
TIMEOUT = 900


def generator_version():
    h = hashlib.sha256()
    for f in sorted(Path(__file__).resolve().parent.rglob("*")):
        if f.is_file() and "__pycache__" not in f.parts:
            h.update(str(f.relative_to(ROOT)).encode() + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def build_id():
    return json.loads((DIST / "ko-quality.stamp.json").read_text(encoding="utf-8")).get("build_id")


# ---- plugins ----------------------------------------------------------------------------------------------------

def plugin_copy(work, marker=None):
    """A copy of the built plugin. With `marker`, a canary copy (flow.md F3): one line added to each style and agent body."""
    dest = Path(work) / ("plugin-canary" if marker else "plugin")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(DIST, dest)
    if marker:
        for f in sorted((dest / "output-styles").glob("*.md")):
            with f.open("a", encoding="utf-8") as fh:
                fh.write(f"\nBegin every reply with the line {marker}-style-{f.stem}\n")
        for f in sorted((dest / "agents").glob("*.md")):
            with f.open("a", encoding="utf-8") as fh:
                fh.write(f"\nBegin your report with the line {marker}-agent-{f.stem}\n")
    return dest


def logger_only_plugin(work):
    """Arm A: the shipped hooks and logger only. No stamp, so the logger records plugin_present: false."""
    dest = Path(work) / "plugin-logger-only"
    if dest.exists():
        shutil.rmtree(dest)
    (dest / ".claude-plugin").mkdir(parents=True)
    shutil.copytree(DIST / "hooks", dest / "hooks")
    shutil.copytree(DIST / "logger", dest / "logger")
    (dest / ".claude-plugin" / "plugin.json").write_text(json.dumps(
        {"name": "ko-quality-logger-only", "version": "0.0.0", "description": "corpus arm A: logger hooks only"}, indent=2), encoding="utf-8")
    return dest


# ---- sessions ---------------------------------------------------------------------------------------------------

def session_plan(prompts, arms, per_stratum):
    """[(arm, [(prompt, profile or None)], key)]. Arm C takes prompt i under one profile, then prompt i+1 of the same
    stratum under the other; the starting profile alternates with i."""
    by = {}
    for p in prompts:
        by.setdefault(p["stratum"], []).append(p)
    plan = []
    for stratum in sorted(by):
        ps = by[stratum][:per_stratum]
        for i, p in enumerate(ps):
            for arm in arms:
                if arm == "C":
                    first, second = PROFILES[i % 2], PROFILES[(i + 1) % 2]
                    turns = [(p, first), (ps[(i + 1) % len(ps)], second)]
                else:
                    turns = [(p, None)]
                plan.append((arm, turns, f"{stratum}-{i + 1}-{arm}"))
    return plan


def make_project(work, key, home, first_profile):
    proj = Path(work) / "projects" / key
    if proj.exists():
        shutil.rmtree(proj)
    shutil.copytree(FIXTURE, proj)
    (proj / ".claude").mkdir(exist_ok=True)
    settings = {"env": {"KO_QUALITY_HOME": str(home)}}
    if first_profile:
        settings["outputStyle"] = STYLE[first_profile]
    (proj / ".claude" / "settings.local.json").write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return proj


def user_line(text):
    return json.dumps({"type": "user", "message": {"role": "user", "content": text}}, ensure_ascii=False)


def run_session(arm, turns, key, plugin, home, work):
    proj = make_project(work, key, home, turns[0][1])
    lines, expected = [], []
    for n, (prompt, profile) in enumerate(turns):
        if n and profile != turns[n - 1][1]:
            lines.append(user_line(f"/output-style {STYLE[profile]}"))
            expected.append(("command", profile))
        lines.append(user_line(prompt["text"]))
        expected.append(("prompt", profile))
    cmd = ["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
           "--plugin-dir", str(plugin), "--add-dir", str(plugin), "--model", MODEL, "--max-turns", str(MAX_TURNS),
           "--permission-mode", "acceptEdits"]   # --add-dir: a skill reads its references under the plugin root (P8)
    started = datetime.datetime.now(datetime.timezone.utc)
    stdout, rc, err = converse(cmd, proj, lines)
    (Path(work) / "streams").mkdir(parents=True, exist_ok=True)
    (Path(work) / "streams" / f"{key}.jsonl").write_text(stdout, encoding="utf-8")   # raw stream, outside the tree
    return parse_stream(stdout, expected), rc, err, started


def converse(cmd, cwd, lines):
    """Send one input line, wait for its `result` event, then send the next (P8: lines written all at once were queued
    into a running tool turn and merged, so turns and records no longer lined up). Returns (stdout, returncode, stderr)."""
    import threading
    proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    err_chunks = []
    t = threading.Thread(target=lambda: err_chunks.append(proc.stderr.read()), daemon=True)
    t.start()
    timer = threading.Timer(TIMEOUT, proc.kill)
    timer.start()
    out, pending, running = [], list(lines), set()
    try:
        proc.stdin.write(pending.pop(0) + "\n")
        proc.stdin.flush()
        for line in proc.stdout:
            out.append(line)
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") == "system" and e.get("subtype") == "task_started":
                running.add(e.get("task_id"))
            elif e.get("type") == "system" and e.get("subtype") == "task_notification":
                running.discard(e.get("task_id"))
            elif e.get("type") == "system" and e.get("subtype") == "task_updated" and (e.get("patch") or {}).get("status") in ("completed", "failed", "killed"):
                running.discard(e.get("task_id"))
            if e.get("type") == "result" and not running:   # a background agent's notification turn comes first
                if pending:
                    proc.stdin.write(pending.pop(0) + "\n")
                    proc.stdin.flush()
                else:
                    proc.stdin.close()
        proc.wait()
    finally:
        timer.cancel()
        if proc.poll() is None:
            proc.kill()
    t.join(timeout=5)
    rc = proc.returncode if proc.returncode != -9 else "timeout"
    return "".join(out), rc, "".join(err_chunks)[-2000:]


def parse_stream(stdout, expected):
    """Per input line (command or prompt): the init output_style, assistant text, and the result event."""
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    turns, cur = [], None
    session_id, model = None, None
    notified_after_result = False
    for e in events:
        if e.get("type") == "system" and e.get("subtype") == "task_notification" and cur is not None and cur["result"] is not None:
            notified_after_result = True
        if e.get("type") == "system" and e.get("subtype") == "init":
            session_id = e.get("session_id") or session_id
            model = e.get("model") or model
            if notified_after_result:            # a background agent's notification turn: part of the prompt turn before it
                cur["notification_turns"] += 1
                notified_after_result = False
                continue
            cur = {"output_style": e.get("output_style"), "texts": [], "tools": [], "result": None, "notification_turns": 0}
            turns.append(cur)
        elif e.get("type") == "assistant" and cur is not None and not e.get("parent_tool_use_id"):
            for c in e.get("message", {}).get("content", []):
                if c.get("type") == "text":
                    cur["texts"].append(c.get("text", ""))
                elif c.get("type") == "tool_use":
                    cur["tools"].append(c.get("name"))
        elif e.get("type") == "result" and cur is not None:
            cur["result"] = e
    out = []
    for (kind, profile), t in zip(expected, turns):
        r = t["result"] or {}
        usage = r.get("usage") or {}
        out.append({"kind": kind, "profile": profile, "output_style": t["output_style"], "text": "\n".join(t["texts"]),
                    "tools": t["tools"], "is_error": r.get("is_error"), "subtype": r.get("subtype"),
                    "cumulative_cost_usd": r.get("total_cost_usd"), "output_tokens": usage.get("output_tokens"),
                    "thinking_tokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
                    "subagent_stats": r.get("subagent_stats"), "result_text": r.get("result"), "notification_turns": t["notification_turns"]})
    return {"session_id": session_id, "model": model, "turns": out, "turns_seen": len(turns), "turns_expected": len(expected)}


def expected_style(arm, profile):
    return STYLE[profile] if arm == "C" else DEFAULT_STYLE


def session_records(home, session_id):
    recs = []
    for f in sorted((Path(home) / "logs").glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("session_id") == session_id:
                    recs.append(r)
    return recs


def append_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")


def annotate(batch, arm, turns, parsed, home, gen_version, bid):
    """One annotation per prompt turn (09 §12.2), keyed by (session_id, turn_key)."""
    sid = parsed["session_id"]
    mains_all = [r for r in session_records(home, sid) if r.get("harness_position") == "main-to-user"]
    keys = []
    for r in mains_all:                        # a notification turn writes a second main record under the same turn_key
        if r.get("turn_key") not in keys:
            keys.append(r.get("turn_key"))
    mains = [next(r for r in mains_all if r.get("turn_key") == k) for k in keys]
    rows, prev_cost, switched, idx = [], 0.0, False, -1
    for t in parsed["turns"]:
        cost = t["cumulative_cost_usd"]
        turn_cost = round(cost - prev_cost, 6) if isinstance(cost, (int, float)) else None
        prev_cost = cost if isinstance(cost, (int, float)) else prev_cost
        if t["kind"] == "command":
            switched = True
            continue
        idx += 1
        prompt = turns[idx][0]
        stats = t["subagent_stats"] or {}
        spawned_by_sub = stats.get("spawned_by_subagents") if isinstance(stats, dict) else None
        rows.append({
            "session_id": sid, "turn_key": mains[idx]["turn_key"] if idx < len(mains) else None,
            "corpus_prompt_id": prompt["id"], "stratum": prompt["stratum"], "arm": arm,
            "profile_selected": t["profile"], "model": parsed["model"],
            "tokens": {"output": (t["output_tokens"] or 0) - (t["thinking_tokens"] or 0), "thinking": t["thinking_tokens"], "method": "usage"},
            "sub_to_sub_present": bool(spawned_by_sub) if spawned_by_sub is not None else None,
            "sub_to_sub_method": "session-stats", "generator_version": gen_version,
            "batch_id": batch, "build_id": bid, "turn_index": idx, "first_turn_after_switch": switched,
            "init_output_style": t["output_style"], "arm_check": t["output_style"] == expected_style(arm, t["profile"]),
            "cost_usd": turn_cost, "is_error": t["is_error"], "log_record_found": idx < len(mains),
            "task_matches_prompt": idx < len(mains) and mains[idx].get("task") == prompt["text"],
            "notification_turns": t["notification_turns"],
            "main_records_in_turn": sum(1 for r in mains_all if idx < len(keys) and r.get("turn_key") == keys[idx]),
            "turns_complete": parsed["turns_seen"] == parsed["turns_expected"],
        })
        switched = False
    return rows


def run_batch(batch, home, work, arms=("A", "B", "C"), prompts_path=PROMPTS, per_stratum=3, ceiling=None, spent=0.0, only=None):
    home, work = Path(home).expanduser(), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    prompts = json.loads(Path(prompts_path).read_text(encoding="utf-8"))["prompts"]
    plugins = {"A": logger_only_plugin(work), "B": plugin_copy(work)}
    plugins["C"] = plugins["B"]
    gen_version, bid = generator_version(), build_id()
    plan = session_plan(prompts, arms, per_stratum)
    if only:
        plan = [s for s in plan if s[2] in only]
    progress = work / f"{batch}.progress.jsonl"
    done = set()
    if progress.exists():
        for line in progress.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            done.add(row["key"])
            spent += row.get("cost_usd") or 0
    for arm, turns, key in plan:
        if key in done:
            continue
        if ceiling is not None and spent >= ceiling:
            append_jsonl(progress, [{"key": key, "skipped": "ceiling", "spent_usd": round(spent, 4)}])
            continue
        parsed, rc, err, started = run_session(arm, turns, key, plugins[arm], home, work)
        rows = annotate(batch, arm, turns, parsed, home, gen_version, bid) if parsed["session_id"] else []
        append_jsonl(home / "annotations" / f"{started:%Y-%m}.jsonl", rows)
        cost = parsed["turns"][-1]["cumulative_cost_usd"] if parsed["turns"] else None
        spent += cost or 0
        append_jsonl(progress, [{"key": key, "arm": arm, "session_id": parsed["session_id"], "rc": rc, "stderr_tail": err[-300:] if rc else "",
                                 "turns_seen": parsed["turns_seen"], "turns_expected": parsed["turns_expected"],
                                 "annotations": len(rows), "arm_check": all(r["arm_check"] for r in rows) if rows else False,
                                 "task_matches": all(r["task_matches_prompt"] for r in rows) if rows else False,
                                 "log_records_found": sum(r["log_record_found"] for r in rows), "cost_usd": cost, "spent_usd": round(spent, 4)}])
        print(f"{key}: rc={rc} turns={parsed['turns_seen']}/{parsed['turns_expected']} cost={cost} spent={spent:.2f}", file=sys.stderr, flush=True)
    return progress


# ---- canary -----------------------------------------------------------------------------------------------------

CANARY_PROMPT = {"id": "canary/1", "stratum": "canary", "text": "파이썬에서 리스트와 튜플의 차이를 두 문장으로 설명해 줘."}
CANARY_PROMPT_2 = {"id": "canary/2", "stratum": "canary", "text": "자바스크립트에서 let과 const의 차이를 두 문장으로 설명해 줘."}


def canary(batch, home, work, mislabel=False):
    """One canary session per arm (09 §18.2, flow.md F3), through the same arm setup as the batch, with the marked copy
    for B and C. A marker in the wrong arm rejects the batch. `mislabel` runs arm B's setup labelled C, once, to show that
    the rejection path works."""
    home, work = Path(home).expanduser(), Path(work)
    work.mkdir(parents=True, exist_ok=True)
    marker = f"KQ-CANARY-{batch}"
    marked = plugin_copy(work, marker)
    setups = {"A": logger_only_plugin(work), "B": marked, "C": marked}
    runs = [("A", "A"), ("B", "B"), ("C", "C")] if not mislabel else [("B", "C")]
    report = {"batch": batch, "marker_prefix": marker, "runs": [], "rejected": False}
    for setup_arm, label in runs:
        turns = [(CANARY_PROMPT, None)] if label != "C" else [(CANARY_PROMPT, PROFILES[0]), (CANARY_PROMPT_2, PROFILES[1])]
        key = f"canary-{setup_arm}-as-{label}"
        if setup_arm == "C":
            parsed, rc, err, _ = run_session("C", turns, key, setups["C"], home, work)
        else:
            parsed, rc, err, _ = run_session(setup_arm, [(t[0], None) for t in turns], key, setups[setup_arm], home, work)
            for t, (_, profile) in zip([x for x in parsed["turns"] if x["kind"] == "prompt"], turns):
                t["profile"] = profile   # the label claims this profile
        checks = []
        for t in [x for x in parsed["turns"] if x["kind"] == "prompt"]:
            found = sorted({tok for tok in [f"{marker}-style-{p}" for p in PROFILES] if tok in t["text"]})
            want = [f"{marker}-style-{t['profile']}"] if label == "C" else []
            checks.append({"profile_label": t["profile"], "output_style": t["output_style"], "markers_found": found,
                           "markers_expected": want, "pass": found == want, "cost_usd": t["cumulative_cost_usd"]})
        ok = bool(checks) and all(c["pass"] for c in checks)
        report["runs"].append({"setup": setup_arm, "label": label, "session_id": parsed["session_id"], "rc": rc, "checks": checks, "pass": ok,
                               "cost_usd": parsed["turns"][-1]["cumulative_cost_usd"] if parsed["turns"] else None})
        report["rejected"] = report["rejected"] or not ok
    report["verdict"] = "batch rejected: a marker is missing or in the wrong arm" if report["rejected"] else "batch accepted: every arm's markers are where its label says"
    return report
