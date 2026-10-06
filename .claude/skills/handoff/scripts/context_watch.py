#!/usr/bin/env python3
"""UserPromptSubmit / Stop hook: when context usage >= threshold, tell Claude
to run the handoff skill (once per session per threshold crossing)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from context_usage import usage  # noqa: E402

THRESHOLD = float(os.environ.get("HANDOFF_THRESHOLD", "0.60"))

try:
    d = json.load(sys.stdin)
    used, ratio, _ = usage(d["transcript_path"])
except Exception:
    sys.exit(0)

flag = os.path.join(os.path.dirname(d["transcript_path"]), f".handoff-{d['session_id']}")
if ratio < THRESHOLD or os.path.exists(flag):
    sys.exit(0)
open(flag, "w").close()

msg = (f"[handoff-watch] 上下文已用 {ratio:.0%}（{used} tokens），达到 {THRESHOLD:.0%} 阈值。"
       "请在完成当前这一小步后，立即调用 handoff skill 生成交接档案，"
       "并告知用户到新的 Claude Code 对话继续；不要再开启新的大任务。")
event = d.get("hook_event_name", "UserPromptSubmit")
if event == "Stop":
    print(json.dumps({"decision": "block", "reason": msg}))
else:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event,
                                             "additionalContext": msg}}))
