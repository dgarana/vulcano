#!/usr/bin/env python3
"""Generate a first-pass CHANGELOG.md from git tags and commit history.

This script is intended as a one-shot backfill helper and a starting point
for future release automation.
"""
from pathlib import Path
import subprocess

def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()

tags = [t for t in sh("git", "tag", "--sort=creatordate").splitlines() if t]
lines = ["# CHANGELOG", "", "_Generated from repository tags and commit history._", ""]
if not tags:
    lines += ["## Unreleased", "", "- No tags found yet."]
else:
    previous = None
    for tag in tags:
        lines += [f"## {tag}", ""]
        if previous is None:
            commits = sh("git", "log", "--pretty=format:- %s", tag).splitlines()
        else:
            commits = sh("git", "log", "--pretty=format:- %s", f"{previous}..{tag}").splitlines()
        lines += commits or ["- No commit summary available."]
        lines.append("")
        previous = tag

Path("CHANGELOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
