#!/usr/bin/env python3
"""Print context usage of a Claude Code session transcript.

Usage: context_usage.py <transcript.jsonl> [--json]
Window size: env HANDOFF_CONTEXT_WINDOW, else 1M if the model id contains
"[1m]", else 200k.
"""
import json
import os
import sys


def usage(path):
    last, model = None, ""
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("isSidechain"):
                continue
            m = e.get("message") or {}
            u = m.get("usage")
            if e.get("type") == "assistant" and u and m.get("model") != "<synthetic>":
                last, model = u, m.get("model", model)
    if not last:
        return 0, 0.0, model
    used = (last.get("input_tokens", 0) + last.get("cache_read_input_tokens", 0)
            + last.get("cache_creation_input_tokens", 0))
    window = int(os.environ.get("HANDOFF_CONTEXT_WINDOW", 0)) or (
        1_000_000 if "[1m]" in model else 200_000)
    return used, used / window, model


if __name__ == "__main__":
    used, ratio, model = usage(sys.argv[1])
    if "--json" in sys.argv:
        print(json.dumps({"used": used, "ratio": ratio, "model": model}))
    else:
        print(f"{used} tokens, {ratio:.0%}")
