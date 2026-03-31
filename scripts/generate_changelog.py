#!/usr/bin/env python3
"""Generate or refresh CHANGELOG.md from git tags and commit history."""
from pathlib import Path
import subprocess

REPO_URL = "https://github.com/dgarana/vulcano"


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()


def commits_for(rev_range: str):
    out = sh("git", "log", "--pretty=format:%H%x09%h%x09%s", rev_range)
    if not out:
        return []
    commits = []
    for line in out.splitlines():
        full_sha, short_sha, subject = line.split("\t", 2)
        commits.append(f"- {subject} ([{short_sha}]({REPO_URL}/commit/{full_sha}))")
    return commits


def main():
    tags = [t for t in sh("git", "tag", "--sort=creatordate").splitlines() if t]
    lines = ["# CHANGELOG", "", "_Generated from repository tags and commit history._", ""]
    if not tags:
        lines += ["## Unreleased", "", "- No tags found yet."]
    else:
        previous = None
        for tag in tags:
            lines += [f"## {tag}", ""]
            if previous is None:
                commits = commits_for(tag)
            else:
                commits = commits_for(f"{previous}..{tag}")
            lines += commits or ["- No commit summary available."]
            lines.append("")
            previous = tag
    Path("CHANGELOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
