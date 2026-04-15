---
name: cheatsheet
description: This skill should be used when the user asks to "make a cheatsheet", "generate a cheat sheet", "compress my notes", "create a study sheet", "make a printable reference", or asks for a cheatsheet for a topic from vault notes or PDFs.
version: 1.0.0
---

# Cheatsheet Skill

You generate information-dense, exam-ready LaTeX cheatsheets from raw vault
notes. The output is a compilable `.tex` file plus an attempted PDF compilation.

---

## Step 0 - Gather parameters

If the user did not provide all of the following, ask for them **in a single
message** before proceeding:

| Parameter | Default | Notes |
|-----------|---------|-------|
| `topic` | (required) | e.g. "QF604 Econometrics", "LeetCode Patterns" |
| `subtopics` | all | Comma-separated focus areas, or "all" to use everything |
| `columns` | 3 | 2 or 3 |
| `font_size` | 8 | 7, 8, 9, or 10 (pt) |
| `raw_dir` | `raw/` | Path to the folder containing source files |
| `output_dir` | `cheatsheets/` | Where to save `.tex` and `.pdf` |
| `paper` | `a4paper,landscape` | or `letterpaper,landscape` |

---

## Step 1 - Read the vault

Run the reader script to pull all `.md` and `.pdf` files from `raw_dir`:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/read_vault.py" "<raw_dir>"
```

The script outputs JSON: `{"files": [{"name":..., "type":..., "content":...}], "count": N}`.

- If `count` is 0: stop and tell the user no source files were found in `raw_dir`.
- If `subtopics` is not "all": mentally filter content to sections that match the
  requested subtopics. You may include tangential content if it aids understanding.
- Summarize to the user: "Found N files - reading [file1.md, file2.pdf, ...]"

---

## Step 2 - Plan the cheatsheet

Before writing LaTeX, briefly outline (in your thinking) the sections you will
include, ordered by density of useful information. Prioritise:

1. Definitions and key formulas
2. Algorithms / step-by-step procedures
3. Decision rules and heuristics
4. Edge cases and gotchas
5. Quick-reference tables

Do NOT include: prose explanations longer than 2 lines, redundant examples,
anything that doesn't add information density.

---

## Step 3 - Generate LaTeX

Write the **complete, compilable** `.tex` file. Use the template below as a
skeleton - fill in everything between `\begin{multicols}` and
`\end{multicols}`.

### Base Template

```latex
\documentclass[FONT_SIZEpt]{extarticle}
\usepackage[margin=0.4cm,PAPER]{geometry}
\usepackage{multicol}
\usepackage{amsmath,amssymb,mathtools}
\usepackage[dvipsnames,table]{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{microtype}
\usepackage{booktabs}
\usepackage{array}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{mdframed}
\usepackage{tikz}           % only if graphs needed
\usepackage{pgfplots}       % only if plots needed
\pgfplotsset{compat=1.18}

%%% Typography & spacing %%%
\titleformat{\section}{\small\bfseries\color{NavyBlue}}{}{0em}{}[\vspace{-2pt}\rule{\columnwidth}{0.4pt}]
\titlespacing{\section}{0pt}{3pt}{1pt}
\titleformat{\subsection}{\footnotesize\bfseries\color{BrickRed}}{}{0em}{}
\titlespacing{\subsection}{0pt}{2pt}{0pt}
\setlist[itemize]{noitemsep,topsep=0pt,leftmargin=8pt,label=\textbullet}
\setlist[enumerate]{noitemsep,topsep=0pt,leftmargin=10pt}
\setlength{\parindent}{0pt}
\setlength{\parskip}{1pt}
\setlength{\columnsep}{4pt}
\setlength{\columnseprule}{0.3pt}
\setlength{\abovedisplayskip}{1pt}
\setlength{\belowdisplayskip}{1pt}

%%% Convenience macros %%%
\newcommand{\kw}[1]{\textbf{#1}}           % keyword
\newcommand{\code}[1]{\texttt{\small #1}}  % inline code
\newcommand{\warn}[1]{\colorbox{yellow!40}{\footnotesize #1}}  % warning box
\newmdenv[linecolor=NavyBlue,linewidth=0.5pt,innerleftmargin=3pt,
  innerrightmargin=3pt,innertopmargin=2pt,innerbottommargin=2pt,
  skipabove=2pt,skipbelow=2pt]{notebox}

\begin{document}
\begin{center}
  {\small\bfseries TOPIC - SUBTOPICS} \hfill {\tiny \today}
\end{center}
\vspace{-4pt}
\begin{multicols}{COLUMNS}

%%% ---- YOUR CONTENT HERE ---- %%%

\end{multicols}
\end{document}
```

Replace `FONT_SIZE`, `PAPER`, `COLUMNS`, `TOPIC`, `SUBTOPICS` with actual values.

### Content Rules

**Every line earns its place. Follow these strictly:**

- Section headers: `\section{Title}` - one per major concept cluster
- Subsection headers: `\subsection{Title}` - use sparingly
- Key formula: display math with `\[ ... \]` or inline `$ ... $`
- Numbered steps: `\begin{enumerate} \item ... \end{enumerate}`
- Quick list: `\begin{itemize} \item ... \end{itemize}`
- Important callout: `\begin{notebox} ... \end{notebox}`
- Two-column table:
  ```latex
  \begin{tabular}{@{}ll@{}}
  \toprule A & B \\ \midrule ... \\ \bottomrule
  \end{tabular}
  ```
- Warning highlight: `\warn{text}`
- Code snippet: `\code{snippet}` or `\begin{verbatim}...\end{verbatim}`

**TikZ graphs**: include ONLY if the concept is fundamentally visual (e.g. a
decision tree, a state machine, a distribution shape). Keep them under 4cm
tall and 1 column wide.

**Math**: write all formulas in LaTeX math mode. Never use Unicode math symbols
in body text - use `$\beta$` not `beta` or Unicode variants.

**Density targets**:
- Aim for >= 80% of column space filled
- Formulas and tables preferred over prose
- Bullet points <= 6 words each
- No blank lines between items in a list

---

## Step 4 - Save the `.tex` file

Determine the output filename:

```
<output_dir>/<topic-slug>_cheatsheet_<YYYY-MM-DD>.tex
```

where `topic-slug` = topic in lowercase-kebab-case, e.g. `qf604-econometrics`.

Create `<output_dir>` if it doesn't exist, then write the file.

Tell the user: "LaTeX saved to `<path>`."

---

## Step 5 - Compile to PDF

Run the compiler script:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/compile_latex.sh" "<tex_path>" "<output_dir>"
```

**On SUCCESS** (exit 0): tell the user the PDF path and offer to open it.

**On ERROR** (exit 2 - `pdflatex` missing):

> `pdflatex` not found. Install it and rerun, or compile manually:
> - macOS: `brew install --cask mactex-no-gui`
> - Ubuntu: `sudo apt install texlive-full`
> - Then: `pdflatex <tex_path>`
> Your `.tex` file is ready at `<path>`.

**On ERROR** (exit 3 - compile failure): show the last 20 lines of the `.log`
file and offer to fix the LaTeX.

---

## Step 6 - Report

Print a compact summary:

```
Cheatsheet generated
  Topic:    <topic>
  Sources:  <N> files read (<list of names>)
  Sections: <list of section names>
  Output:   <tex_path>
  PDF:      <pdf_path | "compile manually - see above">
```

---

## Quality Checklist

- [ ] Document compiles without `\usepackage` errors (all packages are standard TeX Live)
- [ ] No `??` references (no `\ref{}` without `\label{}`)
- [ ] No placeholder text (no `TODO`, `...`, `INSERT HERE`)
- [ ] Columns roughly balanced in density
- [ ] All formulas in math mode
- [ ] `\begin{...}` matched by `\end{...}`
