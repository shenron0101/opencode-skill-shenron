# Claude2OpenCode Skill

Convert Claude Code project configurations to OpenCode format.

## Description

This skill provides a migration toolkit for converting Claude Code project configurations (.claude directory, CLAUDE.md, MCP settings) to OpenCode format.

## Usage

```bash
# Load the skill
/skill claude2opencode

# Run the migration
python3 ~/.claude/tools/migrate_claude_project.py --target opencode --project-root .
```

## What It Migrates

- **CLAUDE.md / .claude/CLAUDE.md** → AGENTS.md (project rules)
- **Agents** (.claude/agents/) → OpenCode prompts
- **Commands** (.claude/commands/) → OpenCode commands
- **Skills** (.claude/skills/) → OpenCode instructions
- **MCP Servers** (settings.json, mcp*.json) → MCP.md with setup instructions

## Supported Targets

| Target | Description |
|--------|-------------|
| `opencode` | Full OpenCode format with `.opencode.jsonc` configuration |
| `codex` | Codex-friendly markdown bundle for manual integration |

## Output Structure

```
.migration_out/opencode/
├── AGENTS.md                    # Migrated rules from CLAUDE.md
├── MCP.md                       # MCP server setup instructions
├── MIGRATION_REPORT.md          # Summary of migration
├── manifest.json                # File mapping manifest
├── opencode.jsonc               # OpenCode configuration
└── .opencode/
    ├── prompts/                 # Agent prompts
    ├── command/                 # Commands
    └── instructions/
        └── skills/              # Skills
```

## Safety Features

- **Non-destructive**: Never deletes original files
- **No overwrites**: Creates numbered output directories if target exists
- **Full traceability**: Manifest tracks every generated file back to its source
- **Clear reporting**: Migration report documents all decisions and required follow-ups

## Requirements

- Python 3.8+
- Claude Code CLI with subagent support

## Files

- `migrate_claude_project.py` - Core migration script
- `migrate_project.md` - Agent definition
- `migrate.md` - Command shortcut
