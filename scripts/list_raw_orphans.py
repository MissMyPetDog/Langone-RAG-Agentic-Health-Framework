#!/usr/bin/env python3
"""List data/raw subdirs whose doc_id is not in assets.jsonl (project root).

Run with system python3, or .venv/bin/python — if not already using venv,
re-execs with project .venv/bin/python (or python3) when present.
"""
from __future__ import annotations

import json
import os
import sys


def _reexec_with_project_venv() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, ".."))
    for name in ("python", "python3"):
        cand = os.path.join(root, ".venv", "bin", name)
        if not (os.path.isfile(cand) and os.access(cand, os.X_OK)):
            continue
        try:
            if os.path.samefile(sys.executable, cand):
                return
        except OSError:
            if os.path.abspath(sys.executable) == os.path.abspath(cand):
                return
        script = os.path.abspath(__file__)
        os.execv(cand, [cand, script, *sys.argv[1:]])


_reexec_with_project_venv()

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, ".."))
ASSETS = os.path.join(_ROOT, "assets.jsonl")
RAW = os.path.join(_ROOT, "data", "raw")


def main() -> None:
    if not os.path.isfile(ASSETS):
        print(f"Missing {ASSETS}", file=sys.stderr)
        sys.exit(1)
    reg: set[str] = set()
    with open(ASSETS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line).get("doc_id")
            if d:
                reg.add(d)
    orphan: list[str] = []
    for name in sorted(os.listdir(RAW)):
        p = os.path.join(RAW, name)
        if os.path.isdir(p) and name not in reg:
            orphan.append(name)
    print("Folders under data/raw NOT listed in assets.jsonl:")
    for x in orphan:
        print(f"  {x}")
    print(f"\nTotal: {len(orphan)}")


if __name__ == "__main__":
    main()
