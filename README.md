# Shenron's OpenCode Skills

A personal collection of OpenCode skills for AI-assisted development workflows.

## Overview

This repository contains custom skills I use with OpenCode to enhance my development workflow. Each skill is self-contained in its own folder with a `SKILL.md` file describing its purpose and usage.

## Skills

### [claude2opencode-skill](./claude2opencode-skill/)

Migrate Claude Code project configurations to OpenCode format.

**Use case**: When switching from Claude Code to OpenCode, convert existing project configurations including agents, commands, skills, and MCP settings.

[View skill →](./claude2opencode-skill/SKILL.md)

### [pdf-study-qa-skill](./pdf-study-qa-skill/)

Study and ask questions about PDF documents using AI-powered analysis.

**Use case**: Extract insights from research papers, documentation, books, or any PDF by asking natural language questions.

[View skill →](./pdf-study-qa-skill/SKILL.md)

## How to Use

### Loading a Skill

In OpenCode, load a skill using the `/skill` command:

```bash
/skill claude2opencode
```

Or reference the skill path directly:

```bash
/skill ./claude2opencode-skill/SKILL.md
```

### Listing Available Skills

To see all available skills in this repository:

```bash
ls -la ~/Desktop/Projects/opencode-skill-shenron/
```

Each folder ending in `-skill` contains a skill definition.

## Using with skills.sh

If you have a `skills.sh` script for managing OpenCode skills, add this repository to your skill path:

```bash
# In your skills.sh or shell configuration
export OPENCODE_SKILLS_PATH="$HOME/Desktop/Projects/opencode-skill-shenron:$OPENCODE_SKILLS_PATH"
```

Then you can list and load skills:

```bash
# List all available skills
skills.sh list

# Load a specific skill
skills.sh load claude2opencode

# Or directly with opencode
opencode --skill claude2encode
```

### Alternative: Symlink Method

If your OpenCode configuration supports skill directories:

```bash
# Link this repo to your OpenCode skills directory
ln -s ~/Desktop/Projects/opencode-skill-shenron ~/.config/opencode/skills/shenron
```

Then load skills by name:

```bash
opencode --skill shenron/claude2opencode
```

## Adding a New Skill

1. Create a new folder: `mkdir my-new-skill`
2. Add a `SKILL.md` file with:
   - Skill name and description
   - Usage instructions
   - Requirements
   - Examples
3. Add any supporting files (scripts, configs, etc.)
4. Update this README to include the new skill

## Skill Format

Each skill folder should contain:

```
skill-name/
├── SKILL.md          # Main skill definition (required)
├── README.md         # Optional: detailed documentation
├── scripts/          # Optional: supporting scripts
├── config/           # Optional: configuration files
└── examples/         # Optional: example usage
```

The `SKILL.md` file follows this structure:

```markdown
# Skill Name

Brief description.

## Description

Detailed explanation of what the skill does.

## Usage

How to use the skill.

## Features

Key features and capabilities.

## Requirements

Prerequisites and dependencies.
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

This is a personal skill repository, but feel free to fork and adapt for your own use!
