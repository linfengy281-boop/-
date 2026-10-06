#!/usr/bin/env bash
# 把 handoff skill 安装到用户级 ~/.claude（所有项目通用）。可重复运行。
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)/.claude/skills/handoff"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
mkdir -p "$DEST/skills"
rm -rf "$DEST/skills/handoff"
cp -r "$SRC" "$DEST/skills/handoff"
chmod +x "$DEST/skills/handoff/scripts/"*.py
python3 - "$DEST" <<'PY'
import json, os, sys
dest = sys.argv[1]
p = os.path.join(dest, "settings.json")
s = json.load(open(p)) if os.path.exists(p) else {}
cmd = f'python3 "{dest}/skills/handoff/scripts/context_watch.py"'
for ev in ("UserPromptSubmit", "Stop"):
    groups = s.setdefault("hooks", {}).setdefault(ev, [])
    if not any("handoff/scripts/context_watch.py" in h.get("command", "")
               for g in groups for h in g.get("hooks", [])):
        groups.append({"hooks": [{"type": "command", "command": cmd}]})
json.dump(s, open(p, "w"), ensure_ascii=False, indent=2)
PY
echo "已安装到 $DEST。重启 Claude Code 后生效；输入 /handoff 可手动触发。"
