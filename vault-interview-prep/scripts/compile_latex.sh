#!/usr/bin/env bash
# compile_latex.sh — Compile a .tex file to PDF using pdflatex.
#
# Usage:
#   bash compile_latex.sh <input.tex> [output_dir]
#
# Exit codes:
#   0  — success, PDF written
#   1  — wrong arguments
#   2  — pdflatex not found
#   3  — compilation failed

set -euo pipefail

TEX_FILE="${1:-}"
OUTPUT_DIR="${2:-$(dirname "${TEX_FILE:-/tmp}")}"

# ── Argument check ─────────────────────────────────────────────────────────────
if [[ -z "$TEX_FILE" ]]; then
  echo "Usage: compile_latex.sh <input.tex> [output_dir]" >&2
  exit 1
fi

if [[ ! -f "$TEX_FILE" ]]; then
  echo "ERROR: File not found: $TEX_FILE" >&2
  exit 1
fi

# ── Dependency check ───────────────────────────────────────────────────────────
if ! command -v pdflatex &>/dev/null; then
  echo "ERROR: pdflatex not found." >&2
  echo "" >&2
  echo "Install instructions:" >&2
  echo "  macOS:  brew install --cask mactex-no-gui" >&2
  echo "  Ubuntu: sudo apt install texlive-full" >&2
  echo "  Other:  https://tug.org/texlive/" >&2
  exit 2
fi

# ── Prepare output directory ───────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"

TEX_ABS="$(cd "$(dirname "$TEX_FILE")" && pwd)/$(basename "$TEX_FILE")"
OUT_ABS="$(cd "$OUTPUT_DIR" && pwd)"
BASENAME="$(basename "$TEX_FILE" .tex)"
LOG_FILE="${OUT_ABS}/${BASENAME}.log"

echo "Compiling: $TEX_ABS"
echo "Output to: $OUT_ABS"

# ── Compile (run twice for cross-references) ───────────────────────────────────
compile_once() {
  pdflatex \
    -interaction=nonstopmode \
    -halt-on-error \
    -output-directory="$OUT_ABS" \
    "$TEX_ABS" \
    > /dev/null 2>&1
}

if compile_once; then
  compile_once || true   # second pass for refs; ignore minor errors
else
  echo "" >&2
  echo "ERROR: LaTeX compilation failed." >&2
  echo "Last 30 lines of log:" >&2
  tail -30 "$LOG_FILE" 2>/dev/null >&2 || echo "(no log file found)" >&2
  exit 3
fi

PDF_PATH="${OUT_ABS}/${BASENAME}.pdf"

if [[ -f "$PDF_PATH" ]]; then
  echo "SUCCESS: ${PDF_PATH}"
else
  echo "ERROR: Compilation appeared to succeed but PDF not found." >&2
  exit 3
fi
