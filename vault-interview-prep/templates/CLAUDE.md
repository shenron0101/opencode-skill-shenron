# Vault Project Instructions

This project uses the `vault-skills` Claude Code plugin.

## Preferred Plugin Skills

Use these plugin skills when the user wants generated study material from vault notes:

- `/vault-skills:cheatsheet` for dense LaTeX reference sheets
- `/vault-skills:interview-questions` for Obsidian interview-prep question packs

## Expected Project Layout

- `raw/` contains source notes and PDFs
- `cheatsheets/` contains generated `.tex` and `.pdf` files
- `Questions/` contains generated `.md` files

## Working Rules

- Treat files in `raw/` as source material; do not rewrite or reorganize them unless asked.
- Prefer using the plugin skills over ad hoc prompts when the task matches the plugin.
- If a required command-line dependency is missing, keep the generated source file and report the exact missing dependency.

## Cheatsheet Defaults

Unless the user specifies otherwise:

- `raw_dir="raw/"`
- `columns=3`
- `font_size=8`
- `paper="a4paper,landscape"`

## Interview Question Defaults

Unless the user specifies otherwise:

- `raw_dir="raw/"`
- `count=15`
- `difficulty="Mixed"`
- `types="Mixed"`
- `role="General"`

### Rules

- For interview questions the goal is to search the raw folder for sources that contain information related to the prompt passed by the user and must also take inspiration from the existing questions if any for this use case. 
- The Agent must also read raw/ for any existing interview question sources.
- The Agent must as well as read the current Questions/ to ensure that there are no redundant questions being created.

## Output Expectations

- Cheatsheets should be compact, printable, and math-safe in LaTeX.
- Interview question files should use valid Obsidian collapsible callout syntax.
- When generation depends on vault content, summarize which source files were used.
