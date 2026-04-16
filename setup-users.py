#!/usr/bin/env python3
"""
setup-users.py — Bootstrap or update user directories from {Name}_Resume.docx files.

Discovers *_Resume.docx files in the project root, extracts Markdown via the
existing extract-resume.py logic (DRY: reuses extract() via importlib), writes
to both .github/Users/{Name}/ and .claude/Users/{Name}/, and creates all
required output folders.

Usage:
    python setup-users.py                   # process all *_Resume.docx in root
    python setup-users.py Pravin Navya      # specific users only

Output per user:
    .github/Users/{Name}/{Name}_Resume.md   (created or updated)
    .claude/Users/{Name}/{Name}_Resume.md   (created or updated)
    {Name}/Resumes/                         (created if missing)
    {Name}/JobSearch/archive/               (created if missing)
    {Name}/History/                         (created if missing)

Requirements:
    pip install 'markitdown[docx,pdf]'   (included in requirements.txt)
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.resolve()

# Reuse extract() from the existing script — no logic duplication
_EXTRACT_SCRIPT = REPO_ROOT / ".github" / "skills" / "resume-tailor" / "scripts" / "extract-resume.py"

_USER_MIRROR_BASES = [
    ".github/Users",
    ".claude/Users",
]

_OUTPUT_SUBDIRS = [
    "Resumes",
    "JobSearch/archive",
    "History",
]


def _load_extract_fn():
    """Load extract() from extract-resume.py using importlib (avoids hyphen import issue)."""
    spec = importlib.util.spec_from_file_location("extract_resume", _EXTRACT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.extract


def _find_resume_docx(users: list[str] | None) -> dict[str, Path]:
    """Return {Name: Path} for all *_Resume.docx files in REPO_ROOT."""
    found = {}
    for docx in sorted(REPO_ROOT.glob("*_Resume.docx")):
        name = docx.stem.replace("_Resume", "")
        if users is None or name in users:
            found[name] = docx
    return found


def _ensure_output_dirs(name: str) -> None:
    """Create {name}/Resumes, {name}/JobSearch/archive, {name}/History."""
    for subdir in _OUTPUT_SUBDIRS:
        path = REPO_ROOT / name / subdir
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / ".gitkeep"
        if not gitkeep.exists() and not any(p for p in path.iterdir() if p.name != ".gitkeep"):
            gitkeep.touch()


def _write_resume_md(name: str, content: str) -> None:
    """Write/update resume Markdown in both .github/Users and .claude/Users."""
    for base in _USER_MIRROR_BASES:
        out_dir = REPO_ROOT / base / name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{name}_Resume.md"
        action = "Updated" if out_file.exists() else "Created"
        out_file.write_text(content, encoding="utf-8")
        print(f"  {action}: {out_file.relative_to(REPO_ROOT)}")


def setup_user(name: str, docx_path: Path, extract_fn) -> None:
    print(f"\n>> {name}  ({docx_path.name})")
    content = extract_fn(str(docx_path))
    _write_resume_md(name, content)
    _ensure_output_dirs(name)
    print(f"  Dirs:    {name}/Resumes/  {name}/JobSearch/archive/  {name}/History/")


def main() -> None:
    users = sys.argv[1:] or None

    resumes = _find_resume_docx(users)
    if not resumes:
        if users:
            missing = ", ".join(f"{u}_Resume.docx" for u in users)
            print(f"No matching docx files found. Expected: {missing}")
        else:
            print("No *_Resume.docx files found in project root.")
        sys.exit(0)

    try:
        extract = _load_extract_fn()
    except Exception as exc:
        print(f"ERROR loading extract-resume.py: {exc}")
        sys.exit(1)

    for name, docx_path in resumes.items():
        setup_user(name, docx_path, extract)

    print(f"\nDone. Processed: {', '.join(resumes.keys())}")


if __name__ == "__main__":
    main()
