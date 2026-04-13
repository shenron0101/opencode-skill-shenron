---
name: opencode-migrator
description: "Convert Claude Code project configurations to OpenCode format. Use when the user wants to migrate, port, or switch a Claude Code project to OpenCode — including .claude directories, CLAUDE.md files, MCP server settings, agents, commands, and skills. Handles configuration migration of project settings into the OpenCode directory layout."
---

# Claude2OpenCode Migration

## Workflow

1. **Analyze existing configuration** — The agent scans the project root for Claude Code artifacts:

   ```bash
   # Identify all Claude Code config files in the current project
   ls -la .claude/ CLAUDE.md .claude/CLAUDE.md .claude/agents/ .claude/commands/ .claude/skills/ 2>/dev/null
   # Check for MCP server definitions
   cat .claude/settings.json 2>/dev/null | grep -A5 '"mcpServers"'
   ```

2. **Run migration** — Execute the migration script targeting the desired output format:

   ```bash
   # Migrate to OpenCode format (default)
   python3 ~/.claude/tools/migrate_claude_project.py --target opencode --project-root .

   # Or migrate to Codex-friendly markdown bundle
   python3 ~/.claude/tools/migrate_claude_project.py --target codex --project-root .
   ```

3. **Validate output** — Confirm the migration produced the expected directory structure:

   ```bash
   # Verify output directory was created
   ls -R .migration_out/opencode/

   # Check the OpenCode config is valid JSON
   python3 -c "import json; json.load(open('.migration_out/opencode/opencode.jsonc'))" 2>&1 || echo "WARN: jsonc may need manual review"

   # Confirm AGENTS.md was generated from CLAUDE.md
   head -20 .migration_out/opencode/AGENTS.md
   ```

4. **Review migration report** — Read the generated report for any items requiring manual follow-up:

   ```bash
   cat .migration_out/opencode/MIGRATION_REPORT.md
   ```

5. **Verify key files** — Spot-check that critical mappings transferred correctly:

   ```bash
   # Check manifest for complete file mapping
   python3 -c "
   import json
   m = json.load(open('.migration_out/opencode/manifest.json'))
   for src, dst in m.items():
       print(f'{src} → {dst}')
   "

   # Confirm MCP server instructions were captured
   head -30 .migration_out/opencode/MCP.md
   ```

## Migration Mapping

| Source (Claude Code) | Destination (OpenCode) |
|---|---|
| `CLAUDE.md` / `.claude/CLAUDE.md` | `AGENTS.md` (project rules) |
| `.claude/agents/` | `.opencode/prompts/` |
| `.claude/commands/` | `.opencode/command/` |
| `.claude/skills/` | `.opencode/instructions/skills/` |
| `settings.json` / `mcp*.json` | `MCP.md` (setup instructions) |

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

- **Non-destructive**: The migration never deletes or modifies original files.
- **No overwrites**: Numbered output directories are created if the target path already exists.
- **Full traceability**: The manifest tracks every generated file back to its source.
- **Clear reporting**: The migration report documents all decisions and required follow-ups.
