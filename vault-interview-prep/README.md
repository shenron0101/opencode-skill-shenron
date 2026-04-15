# vault-skills

A Claude Code plugin for generating:

- dense LaTeX cheatsheets from vault notes
- Obsidian-formatted interview question packs from the same source material

Input comes from `.md` and `.pdf` files in `raw/`.
Output goes to `outputs/cheatsheets/` or `outputs/interview-questions/`.

## Plugin Layout

This repository follows the minimal skill-based plugin structure:

```text
vault-skills/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── cheatsheet/
│   │   └── SKILL.md
│   └── interview-questions/
│       └── SKILL.md
├── scripts/
│   ├── compile_latex.sh
│   └── read_vault.py
└── README.md
```

## Install

```bash
claude plugin install /path/to/vault-skills
```

Or load it for a single session:

```bash
claude --plugin-dir /path/to/vault-skills
```

## Skills

### `/vault-skills:cheatsheet`

Generates a multi-column LaTeX cheatsheet from your vault notes and tries to compile it to PDF.

Example:

```text
/vault-skills:cheatsheet topic="QF604 Econometrics" subtopics="OLS, OVB, GMM, Panel Data" columns=3
```

Parameters:

| Parameter | Default | Options |
|-----------|---------|---------|
| `topic` | required | any string |
| `subtopics` | all | comma-separated list |
| `columns` | 3 | 2 or 3 |
| `font_size` | 8 | 7, 8, 9, 10 |
| `raw_dir` | `raw/` | any path |
| `output_dir` | `outputs/cheatsheets/` | any path |
| `paper` | `a4paper,landscape` | or `letterpaper,landscape` |

### `/vault-skills:interview-questions`

Generates structured interview questions in Obsidian collapsible-callout format.

Example:

```text
/vault-skills:interview-questions topic="OLS and Wald Tests" count=20 difficulty="Hard" role="Quant Researcher"
```

Parameters:

| Parameter | Default | Options |
|-----------|---------|---------|
| `topic` | required | any string |
| `count` | 15 | integer |
| `difficulty` | Mixed | Easy / Medium / Hard / Mixed |
| `types` | Mixed | concept, derive, code, scenario, gotcha, explain |
| `role` | General | Quant Researcher / SWE / ML Engineer / Trading |
| `raw_dir` | `raw/` | any path |
| `output_dir` | `outputs/interview-questions/` | any path |

The plugin exposes these skills directly from `skills/`:

- `cheatsheet`
- `interview-questions`

## Vault Structure

Recommended layout for a project using this plugin:

```text
your-vault/
├── raw/
│   ├── QF604_Cheat_Sheet.pdf
│   ├── lecture-notes-L3.md
│   └── ...
├── outputs/
│   ├── cheatsheets/
│   └── interview-questions/
└── CLAUDE.md
```

A default project template is included at `templates/CLAUDE.md`.

## PDF Reading

`scripts/read_vault.py` tries these PDF extraction methods in order:

| Method | Requires |
|--------|---------|
| `pdftotext` | `brew install poppler` or `apt install poppler-utils` |
| `pymupdf` | `pip install pymupdf` |
| `pdfplumber` | `pip install pdfplumber` |

Install at least one for PDF support. Markdown files work with no extra dependencies.

## PDF Compilation

For automatic PDF output, install `pdflatex`:

```bash
# macOS
brew install --cask mactex-no-gui

# Ubuntu/Debian
sudo apt install texlive-full
```

## License

MIT
