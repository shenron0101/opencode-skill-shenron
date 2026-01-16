# Claude2OpenCode

A subagent-based migration toolkit for converting Claude Code project configurations to OpenCode format.

## Overview

This repository provides the files and instructions needed to set up a Claude Code subagent that can automatically migrate your Claude Code project configuration to OpenCode format. The migration handles:

- **CLAUDE.md / .claude/CLAUDE.md** → AGENTS.md (project rules)
- **Agents** (.claude/agents/) → OpenCode prompts
- **Commands** (.claude/commands/) → OpenCode commands
- **Skills** (.claude/skills/) → OpenCode instructions
- **MCP Servers** (settings.json, mcp*.json) → MCP.md with setup instructions

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude2opencode.git
   ```

2. Copy the files to your Claude Code configuration:
   ```bash
   # Copy the migration tool
   mkdir -p ~/.claude/tools
   cp tools/migrate_claude_project.py ~/.claude/tools/

   # Copy the agent definition
   mkdir -p ~/.claude/agents
   cp agents/migrate_project.md ~/.claude/agents/

   # Copy the command (optional)
   mkdir -p ~/.claude/commands
   cp commands/migrate.md ~/.claude/commands/
   ```

## Usage

### Using the Command (Recommended)

If you installed the command, simply run:

```
/migrate opencode
```

Or for Codex format:

```
/migrate codex
```

### Direct Agent Invocation

You can also invoke the agent directly:

```
Call the migrate_project agent with target=opencode
```

## Output

The migration creates files under `.migration_out/<target>/`:

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

## File Structure

```
claude2opencode/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── tools/
│   └── migrate_claude_project.py    # Core migration script
├── agents/
│   └── migrate_project.md       # Agent definition
└── commands/
    └── migrate.md               # Command shortcut
```

## How It Works

1. **Discovery**: The agent scans your `.claude/` directory for agents, skills, commands, and settings files.

2. **Parsing**: Files are parsed for YAML frontmatter metadata (name, description) and content.

3. **Transformation**: Content is converted to OpenCode-compatible format:
   - Agent prompts become `.opencode/prompts/<name>.txt`
   - Commands become `.opencode/command/<name>.md`
   - Skills become `.opencode/instructions/skills/<name>.md`

4. **MCP Extraction**: MCP server configurations are extracted from settings files and documented with setup instructions.

5. **Report Generation**: A detailed migration report is created with source inventory, mapping decisions, and manual follow-ups.

## Supported Targets

| Target | Description |
|--------|-------------|
| `opencode` | Full OpenCode format with `.opencode.jsonc` configuration |
| `codex` | Codex-friendly markdown bundle for manual integration |

## Safety Features

- **Non-destructive**: Never deletes original files
- **No overwrites**: Creates numbered output directories if target exists
- **Full traceability**: Manifest tracks every generated file back to its source
- **Clear reporting**: Migration report documents all decisions and required follow-ups

## Requirements

- Python 3.8+
- Claude Code CLI with subagent support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
