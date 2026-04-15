---
name: interview-questions
description: This skill should be used when the user asks to "generate interview questions", "make interview prep", "quiz me on" a topic, "practice questions for" a topic, "create Q&A" from vault notes, or asks for flashcards or Obsidian interview-prep output.
version: 1.0.0
---

# Interview Questions Skill

You generate structured interview questions from vault notes, saved as
Obsidian-compatible markdown with collapsible callout blocks.

---

## Step 0 - Gather parameters

Ask for missing parameters **in a single message**:

| Parameter | Default | Notes |
|-----------|---------|-------|
| `topic` | (required) | e.g. "OLS regression", "Dynamic Programming", "Options pricing" |
| `raw_dir` | `raw/` | Source folder |
| `count` | 15 | Number of questions |
| `difficulty` | Mixed | Easy / Medium / Hard / Mixed |
| `types` | Mixed | See type table below |
| `role` | General | Quant Researcher / SWE / ML Engineer / Trading |
| `output_dir` | `outputs/interview-questions/` | Where to save the `.md` |

**Question types** (comma-separated, or "Mixed"):

| Code | Type | Best for |
|------|------|----------|
| `concept` | Definition + intuition | All roles |
| `scenario` | "What would you do if..." | Trading / Quant |
| `gotcha` | Common misconception traps | All roles |
| `explain` | "Explain to a non-expert" | All roles |

---

## Step 1 - Read the vault

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/read_vault.py" "<raw_dir>"
```

- Summarize: "Found N files. Using: [list]"
- Filter content to the requested topic. If you find nothing relevant,
  say so and offer to generate questions from your own knowledge instead
  (ask user to confirm).

---

## Step 2 - Plan question distribution

Before writing, plan the spread:
- If `difficulty = Mixed`: roughly 30% Easy, 50% Medium, 20% Hard
- If `types = Mixed`: spread across concept, derive/code, scenario, gotcha
- Ensure questions are **not redundant** - each should test a distinct idea
- Weight toward what's commonly tested in real interviews for `role`

For **Quant / Trading roles**, prioritise:
- Derivations (OVB proof, Wald statistic, GMM consistency, etc.)
- Numerical intuition ("What happens to beta-hat if you add a correlated regressor?")
- Market microstructure / options pricing edge cases

For **ML Engineer**, prioritise:
- Bias-variance, regularisation, overfitting
- Implementation traps (data leakage, class imbalance)
- System design components

---

## Step 3 - Generate the markdown

### Output format

Every question uses Obsidian's **collapsible callout** syntax:

```markdown
> [!question]- Q{n} [{difficulty}] [{type}]: {Question text}
>
> **Answer:**
> {Core answer - clear and complete. Use $LaTeX$ for math.}
>
> **Key Points:**
> - {Point 1}
> - {Point 2}
> - {Point 3}
>
> **Common Mistake:**
> {One specific wrong answer / confusion to avoid}
>
> **Follow-up:** {One harder follow-up question}
```

The `-` after `[!question]` makes it collapsed by default in Obsidian.

### Difficulty badges

Use these exactly:
- `[Easy]` - can be answered in < 60 seconds
- `[Medium]` - requires 1-3 minutes of reasoning
- `[Hard]` - derivation or deep systems thinking required

### Type badges

Use: `[Concept]`, `[Derive]`, `[Code]`, `[Scenario]`, `[Gotcha]`, `[Explain]`

### Special formatting rules

**Math**: Use `$...$` for inline and `$$...$$` for display math.
Example: `$\hat{\beta} = (X'X)^{-1}X'Y$`

**Code blocks**: Use fenced code blocks with language tag:
````markdown
> ```python
> def binary_search(arr, target):
>     lo, hi = 0, len(arr) - 1
>     ...
> ```
````
Note: inside a callout, indent code blocks with `>` prefix.

**Tables**: Use markdown tables inside the callout:
```markdown
> | Model | ACF | PACF |
> |-------|-----|------|
> | AR(p) | Decay | Cuts off |
```

**Derivation questions**: Structure the answer as numbered steps, each <= 2
lines. Show the key algebra, don't skip steps that would trip up an interviewer.

---

## Step 4 - File structure

The complete output file:

```markdown
---
topic: {topic}
date: {YYYY-MM-DD}
role: {role}
difficulty: {difficulty}
count: {count}
sources: [{list of source filenames}]
tags: [interview-prep, {topic-slug}]
---

# Interview Questions: {topic}

> **Role:** {role} | **Difficulty:** {difficulty} | **Generated:** {date}

---

{Q1 callout}

{Q2 callout}

...

{QN callout}

---
*Sources: {comma-separated filenames} | vault-skills v1.0*
```

---

## Step 5 - Save

Filename: `<output_dir>/<topic-slug>_interviews_<YYYY-MM-DD>.md`

Create `<output_dir>` if it doesn't exist. Write the file.

Tell the user: "Saved {count} questions to `<path>`."

---

## Step 6 - Report

```
Interview questions generated
  Topic:      {topic}
  Role:       {role}
  Count:      {count} questions
  Difficulty: {difficulty distribution, e.g. "5 Easy / 8 Medium / 2 Hard"}
  Types:      {type distribution}
  Sources:    {N} files
  Output:     {path}

Tip: In Obsidian, click the arrow on each callout to expand.
     Use Ctrl+Click to open in a new pane for side-by-side review.
```

---

## Quality Checklist

- [ ] Every callout has Answer, Key Points, Common Mistake, Follow-up
- [ ] No two questions test the same concept
- [ ] Math is in LaTeX math mode (not Unicode)
- [ ] Code questions have correct syntax
- [ ] Difficulty labels match actual difficulty
- [ ] Frontmatter YAML is valid
- [ ] Callout syntax uses `> [!question]-` (with dash for collapsed)
