#!/usr/bin/env python3
"""
extract-resume.py — Extract structured Markdown from a resume file using Microsoft MarkItDown.

Supports: .docx, .pdf, .pptx, .html, and any other format MarkItDown handles.

Usage:
    python extract-resume.py <path/to/resume.docx>
    python extract-resume.py <path/to/resume.pdf>
    python extract-resume.py <path/to/resume.docx> -o <output.md>

Requirements:
    pip install 'markitdown[docx,pdf]'
"""

import sys
from pathlib import Path


def check_dependency():
    try:
        from markitdown import MarkItDown  # noqa: F401
    except ImportError:
        print("ERROR: markitdown is not installed.")
        print("Run:  pip install 'markitdown[docx,pdf]'")
        sys.exit(1)


def extract(input_path: str) -> str:
    from markitdown import MarkItDown
    md = MarkItDown(enable_plugins=False)
    result = md.convert(input_path)
    return result.text_content.strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract-resume.py <resume.docx|pdf> [-o output.md]")
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    # Optional -o <output.md> flag
    output_path = None
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_path = Path(sys.argv[idx + 1])

    check_dependency()
    content = extract(str(input_path))

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print(f"Saved: {output_path}")
    else:
        print(f"=== EXTRACTED RESUME: {input_path.name} ===")
        print()
        print(content)
        print()
        print("=== END OF RESUME ===")


if __name__ == "__main__":
    main()
