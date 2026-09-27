#!/usr/bin/env python3
"""Mechanical checks for a note: 汉字 count, unbalanced $ per line, image links.

Usage: python3 check_note.py notes/L2/187-....md [more notes...]
Exit code 1 if any check fails.
"""
import os
import re
import sys

LIMITS = {"L1": (1500, 3000), "L2": (3500, 6500)}


def check(path):
    ok = True
    s = open(path, encoding="utf8").read()
    level = "L1" if "/L1/" in path else "L2"
    n = len(re.findall(r"[一-鿿]", s))
    lo, hi = LIMITS[level]
    flag = "" if lo <= n <= hi else f"  (outside {level} target {lo}-{hi}; fine if formula-heavy)"
    print(f"{path}: {n} 汉字{flag}")
    for i, line in enumerate(s.split("\n"), 1):
        if line.replace("$$", "").count("$") % 2:
            print(f"  odd number of $ on line {i}: {line[:80]}")
            ok = False
    for m in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", s):
        p = os.path.join(os.path.dirname(path), m)
        if not os.path.exists(p):
            print(f"  missing image: {m}")
            ok = False
    if "http" in s:
        for u in re.findall(r"\((https?://[^)]+)\)", s):
            if "eprint.iacr.org" in u and not re.search(r"/20\d\d/\d+$", u):
                print(f"  suspicious ePrint URL: {u}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if all(check(p) for p in sys.argv[1:]) else 1)
