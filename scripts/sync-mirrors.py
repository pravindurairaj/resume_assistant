#!/usr/bin/env python3
"""
sync-mirrors.py - Keep agent-agnostic shared content in sync between
                  .github/ and .claude/.

Each tree is adapted to its coding agent:
  .github/  - GitHub Copilot (copilot-instructions.md, prompts/, agents/)
  .claude/  - Claude Code (commands/, agents/, settings.json)

This script only mirrors content that BOTH agents consume: the skill scripts,
SKILL.md procedures, asset templates, context notes, instructions, and master
user resumes. Agent-specific subtrees (commands/, agents/, prompts/,
copilot-instructions.md) are left alone in their native tree.

PII files (career-profile-*.instructions.md, Users/*/*_Resume*.md) are skipped —
they're gitignored and managed manually.

Modes:
    python scripts/sync-mirrors.py            # perform sync
    python scripts/sync-mirrors.py --check    # exit 1 if drift, else 0
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

MIRRORED_SUBTREES = [
    "skills",
    "context",
    "instructions",
    "Users",
]

MIRRORED_ROOT_FILES = [
    "requirements.txt",
]

EXCLUDE_GLOBS = [
    "instructions/career-profile-*.instructions.md",
    "Users/*/*_Resume.md",
    "Users/*/*_Resume_*.md",
    "Users/*/companies/*.md",
    "**/__pycache__/**",
    "**/*.pyc",
]

ROOT_FILE_PAIRS: list[tuple[str, str]] = []


def find_repo_root() -> Path:
    p = Path(__file__).resolve().parent
    while p != p.parent:
        if (p / ".github").is_dir() and (p / ".claude").is_dir():
            return p
        p = p.parent
    print("ERROR: could not find repo root (need both .github/ and .claude/)")
    sys.exit(2)


def is_excluded(rel: Path) -> bool:
    rel_str = rel.as_posix()
    for pat in EXCLUDE_GLOBS:
        if Path(rel_str).match(pat):
            return True
    return False


def collect_files(base: Path, subtree: str) -> set[Path]:
    root = base / subtree
    if not root.exists():
        return set()
    out = set()
    for f in root.rglob("*"):
        if f.is_file():
            rel = f.relative_to(base)
            if is_excluded(rel):
                continue
            out.add(rel)
    return out


def sync_pair(repo_root: Path, check_only: bool) -> list[str]:
    """Return list of drift descriptions; empty list = in sync."""
    gh = repo_root / ".github"
    cl = repo_root / ".claude"
    drift: list[str] = []

    for subtree in MIRRORED_SUBTREES:
        gh_files = collect_files(gh, subtree)
        cl_files = collect_files(cl, subtree)
        all_rels = gh_files | cl_files

        for rel in sorted(all_rels):
            gh_f = gh / rel
            cl_f = cl / rel
            gh_exists = gh_f.exists()
            cl_exists = cl_f.exists()

            if gh_exists and cl_exists:
                if filecmp.cmp(gh_f, cl_f, shallow=False):
                    continue
                # both exist, differ — newer wins
                gh_newer = gh_f.stat().st_mtime >= cl_f.stat().st_mtime
                src, dst = (gh_f, cl_f) if gh_newer else (cl_f, gh_f)
                direction = ".github -> .claude" if gh_newer else ".claude -> .github"
                drift.append(f"DIFF  {rel}  ({direction})")
                if not check_only:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
            elif gh_exists:
                drift.append(f"ADD   {rel}  (.github -> .claude)")
                if not check_only:
                    cl_f.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(gh_f, cl_f)
            else:
                drift.append(f"ADD   {rel}  (.claude -> .github)")
                if not check_only:
                    gh_f.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(cl_f, gh_f)

    for fname in MIRRORED_ROOT_FILES:
        gh_f = gh / fname
        cl_f = cl / fname
        if gh_f.exists() and cl_f.exists():
            if not filecmp.cmp(gh_f, cl_f, shallow=False):
                gh_newer = gh_f.stat().st_mtime >= cl_f.stat().st_mtime
                src, dst = (gh_f, cl_f) if gh_newer else (cl_f, gh_f)
                direction = ".github -> .claude" if gh_newer else ".claude -> .github"
                drift.append(f"DIFF  {fname}  ({direction})")
                if not check_only:
                    shutil.copy2(src, dst)
        elif gh_f.exists():
            drift.append(f"ADD   {fname}  (.github -> .claude)")
            if not check_only:
                shutil.copy2(gh_f, cl_f)
        elif cl_f.exists():
            drift.append(f"ADD   {fname}  (.claude -> .github)")
            if not check_only:
                shutil.copy2(cl_f, gh_f)

    for a_rel, b_rel in ROOT_FILE_PAIRS:
        a = repo_root / a_rel
        b = repo_root / b_rel
        if a.exists() and b.exists():
            if not filecmp.cmp(a, b, shallow=False):
                src, dst = (a, b) if a.stat().st_mtime >= b.stat().st_mtime else (b, a)
                drift.append(f"DIFF  {a_rel} <-> {b_rel}")
                if not check_only:
                    shutil.copy2(src, dst)
        elif a.exists():
            drift.append(f"ADD   {a_rel} -> {b_rel}")
            if not check_only:
                b.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(a, b)
        elif b.exists():
            drift.append(f"ADD   {b_rel} -> {a_rel}")
            if not check_only:
                shutil.copy2(b, a)

    return drift


def main():
    ap = argparse.ArgumentParser(description="Sync .github/ <-> .claude/ mirrors")
    ap.add_argument("--check", action="store_true", help="Report drift without copying; exit 1 if any drift")
    ap.add_argument("--quiet", action="store_true", help="Suppress per-file output")
    args = ap.parse_args()

    repo_root = find_repo_root()
    drift = sync_pair(repo_root, check_only=args.check)

    if drift and not args.quiet:
        for line in drift:
            print(line)

    if args.check:
        if drift:
            print(f"\n{len(drift)} drift entries. Run 'python scripts/sync-mirrors.py' to fix.")
            sys.exit(1)
        if not args.quiet:
            print("In sync.")
        sys.exit(0)
    else:
        if not args.quiet:
            print(f"\nSynced {len(drift)} file(s)." if drift else "Already in sync.")


if __name__ == "__main__":
    main()
