#!/usr/bin/env python3
"""
read_vault.py — Read all .md and .pdf files from a vault raw/ directory.

Usage:
    python3 read_vault.py [raw_dir]

Output:
    JSON to stdout:
    {
      "files": [
        {"name": "...", "path": "...", "type": "md|pdf", "content": "...", "chars": N}
      ],
      "count": N,
      "total_chars": N,
      "errors": [...]
    }
"""

import sys
import os
import json
import subprocess
from pathlib import Path


MAX_CHARS_PER_FILE = 80_000  # ~20k tokens per file cap
MAX_TOTAL_CHARS = 400_000  # ~100k tokens total cap


def read_md(path: Path) -> str:
    """Read a markdown file, stripping Obsidian frontmatter."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        # Strip YAML frontmatter if present
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                text = text[end + 3 :].lstrip("\n")
        return text
    except Exception as e:
        return f"[ERROR reading {path.name}: {e}]"


def read_pdf_pdftotext(path: Path) -> str | None:
    """Try pdftotext (poppler-utils)."""
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def read_pdf_pymupdf(path: Path) -> str | None:
    """Try PyMuPDF (fitz)."""
    try:
        import fitz  # type: ignore

        doc = fitz.open(str(path))
        pages = []
        for i, page in enumerate(doc):
            pages.append(f"--- Page {i + 1} ---\n{page.get_text()}")
        return "\n".join(pages)
    except ImportError:
        pass
    except Exception:
        pass
    return None


def read_pdf_pdfplumber(path: Path) -> str | None:
    """Try pdfplumber."""
    try:
        import pdfplumber  # type: ignore

        with pdfplumber.open(str(path)) as pdf:
            pages = []
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append(f"--- Page {i + 1} ---\n{text}")
        return "\n".join(pages)
    except ImportError:
        pass
    except Exception:
        pass
    return None


def read_pdf(path: Path) -> tuple[str, str]:
    """
    Try multiple PDF extraction methods.
    Returns (content, method_used).
    """
    for reader, name in [
        (read_pdf_pdftotext, "pdftotext"),
        (read_pdf_pymupdf, "pymupdf"),
        (read_pdf_pdfplumber, "pdfplumber"),
    ]:
        content = reader(path)
        if content and content.strip():
            return content, name

    hint = (
        f"[PDF: {path.name} — could not extract text. "
        "Install one of: pdftotext (brew install poppler / apt install poppler-utils), "
        "pymupdf (pip install pymupdf), or pdfplumber (pip install pdfplumber)]"
    )
    return hint, "none"


def collect_files(raw_dir: Path) -> tuple[list[dict], list[str]]:
    files = []
    errors = []
    total_chars = 0

    # Walk in sorted order for reproducibility
    all_paths = sorted(raw_dir.rglob("*"))

    for fpath in all_paths:
        if not fpath.is_file():
            continue

        ext = fpath.suffix.lower()
        if ext not in {".md", ".pdf"}:
            continue

        rel_path = str(fpath.relative_to(raw_dir.parent))

        if total_chars >= MAX_TOTAL_CHARS:
            errors.append(
                f"Skipped {fpath.name}: total character limit ({MAX_TOTAL_CHARS:,}) reached"
            )
            continue

        if ext == ".md":
            content = read_md(fpath)
            ftype = "md"
            method = "text"
        else:
            content, method = read_pdf(fpath)
            ftype = "pdf"

        # Truncate individual files
        if len(content) > MAX_CHARS_PER_FILE:
            content = (
                content[:MAX_CHARS_PER_FILE]
                + f"\n[TRUNCATED at {MAX_CHARS_PER_FILE:,} chars]"
            )
            errors.append(f"Truncated {fpath.name} to {MAX_CHARS_PER_FILE:,} chars")

        total_chars += len(content)

        files.append(
            {
                "name": fpath.name,
                "path": rel_path,
                "type": ftype,
                "method": method,
                "chars": len(content),
                "content": content,
            }
        )

    return files, errors


def main():
    raw_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("raw")

    if not raw_dir.exists():
        out = {
            "files": [],
            "count": 0,
            "total_chars": 0,
            "errors": [f"Directory not found: {raw_dir}"],
        }
        print(json.dumps(out, ensure_ascii=False))
        sys.exit(1)

    files, errors = collect_files(raw_dir)
    total_chars = sum(f["chars"] for f in files)

    out = {
        "files": files,
        "count": len(files),
        "total_chars": total_chars,
        "errors": errors,
    }
    print(json.dumps(out, ensure_ascii=False, indent=None))


if __name__ == "__main__":
    main()
