#!/usr/bin/env python3
"""Compute the next handoff name: 原名（交接N）.

Usage: next_name.py "<current session name>" [handoff_dir]
Accepts half/full-width brackets in the input. Prints:
  <base>\t<N>\t<base>（交接N）
N = max(N in current name, N of existing files in handoff_dir for the same base) + 1.
"""
import os
import re
import sys

PAT = re.compile(r"^(.*?)\s*[（(]交接\s*(\d+)\s*[）)]\s*$")


def split(name):
    m = PAT.match(name.strip())
    return (m.group(1), int(m.group(2))) if m else (name.strip(), 0)


if __name__ == "__main__":
    base, n = split(sys.argv[1])
    d = sys.argv[2] if len(sys.argv) > 2 else ".claude/handoffs"
    if os.path.isdir(d):
        for fn in os.listdir(d):
            b, k = split(os.path.splitext(fn)[0])
            if b == base:
                n = max(n, k)
    n += 1
    print(f"{base}\t{n}\t{base}（交接{n}）")
