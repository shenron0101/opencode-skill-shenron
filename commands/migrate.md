---
description: Convert this Claude Code repo config to OpenCode or Codex. Usage: /migrate opencode|codex
---

You are running the migrate_project agent.

Take the first argument as target:
- If $ARGUMENTS contains "opencode" => target=opencode
- If $ARGUMENTS contains "codex" => target=codex
- Else default to target=opencode

Call the migrate_project agent with "target=<target>".
