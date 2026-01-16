#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(".").resolve()

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "unnamed"

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")

def write_text(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def find_claude_md() -> Path | None:
    cands = [ROOT/"CLAUDE.md", ROOT/".claude"/"CLAUDE.md", ROOT/".claude"/"claude.md"]
    for p in cands:
        if p.exists():
            return p
    return None

def list_files(base: Path) -> List[Path]:
    if not base.exists():
        return []
    return [p for p in base.rglob("*") if p.is_file()]

def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1].strip()
    body = parts[2].strip()
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body

def infer_desc(md: str, fallback: str) -> str:
    for line in md.splitlines():
        if line.strip().startswith("#"):
            return line.lstrip("#").strip()
    for line in md.splitlines():
        if line.strip():
            return (line.strip()[:80] + "…") if len(line.strip()) > 80 else line.strip()
    return fallback

def extract_mcp_config(claude_dir: Path) -> List[Dict]:
    """Extract MCP server configurations from .claude settings files."""
    servers = []
    settings_files = [
        claude_dir / "settings.json",
        claude_dir / "settings.local.json",
        *claude_dir.glob("mcp*.json")
    ]
    for sf in settings_files:
        if not sf.exists():
            continue
        try:
            data = json.loads(read_text(sf))
            if "mcp" in data and "servers" in data["mcp"]:
                for name, cfg in data["mcp"]["servers"].items():
                    servers.append({"name": name, "config": cfg, "source": str(sf)})
        except (json.JSONDecodeError, KeyError):
            pass
    return servers

def convert(target: str) -> Path:
    out = ROOT / ".migration_out" / target
    if out.exists():
        # don't overwrite by default; create a new numbered folder
        i = 1
        while (ROOT / ".migration_out" / f"{target}_{i}").exists():
            i += 1
        out = ROOT / ".migration_out" / f"{target}_{i}"
    out.mkdir(parents=True, exist_ok=True)

    manifest: Dict[str, Dict] = {"target": target, "generated": {}}

    # Source inventory
    claude_dir = ROOT / ".claude"
    src_files = list_files(claude_dir)
    claude_md = find_claude_md()
    if claude_md:
        src_files.append(claude_md)

    # Rules
    if claude_md and claude_md.exists():
        rules = read_text(claude_md).strip()
        agents_md = "# Project Rules (migrated from CLAUDE.md)\n\n" + rules + "\n"
        write_text(out / "AGENTS.md", agents_md)
        manifest["generated"]["AGENTS.md"] = {"from": [str(claude_md)]}

    # Extract MCP config
    mcp_servers = extract_mcp_config(claude_dir)

    # Agents / Skills / Commands (best-effort by folder name)
    agents_src = claude_dir / "agents"
    skills_src = claude_dir / "skills"
    commands_src = claude_dir / "commands"

    agents = list_files(agents_src)
    skills = list_files(skills_src)
    commands = list_files(commands_src)

    # Parse agent metadata
    agent_metadata = []
    for p in agents:
        content = read_text(p)
        fm, body = parse_frontmatter(content)
        name = fm.get("name", p.stem)
        desc = fm.get("description", infer_desc(body, name))
        agent_metadata.append({"file": p, "name": name, "desc": desc, "body": body, "slug": slugify(name)})

    if target == "opencode":
        # MCP
        mcp_md = ["# MCP Migration\n"]
        if mcp_servers:
            mcp_md.append("## Detected MCP Servers\n")
            for srv in mcp_servers:
                mcp_md.append(f"### {srv['name']}\n")
                mcp_md.append(f"Source: `{srv['source']}`\n")
                mcp_md.append("```json\n" + json.dumps(srv['config'], indent=2) + "\n```\n")
                mcp_md.append("\nSuggested OpenCode command:\n```bash\n")
                mcp_md.append(f"opencode mcp add {srv['name']} --config <path-to-config>\n```\n")
        else:
            mcp_md.append("No MCP servers detected in .claude settings.\n")
        write_text(out / "MCP.md", "\n".join(mcp_md))
        manifest["generated"]["MCP.md"] = {"from": [s["source"] for s in mcp_servers]}

        # Prompts
        agent_configs = {}
        for am in agent_metadata:
            dst = out / ".opencode" / "prompts" / f"{am['slug']}.txt"
            write_text(dst, am['body'].strip() + "\n")
            manifest["generated"][str(dst.relative_to(out))] = {"from": [str(am['file'])]}
            agent_configs[am['slug']] = {
                "prompt": f"{{file:./.opencode/prompts/{am['slug']}.txt}}",
                "mode": "primary",
                "permissions": {"read": True, "write": False, "edit": False, "bash": False}
            }

        # Skills
        for p in skills:
            content = read_text(p)
            fm, body = parse_frontmatter(content)
            name = slugify(p.stem)
            dst = out / ".opencode" / "instructions" / "skills" / f"{name}.md"
            write_text(dst, f"# Skill: {p.stem}\n\n{body}\n")
            manifest["generated"][str(dst.relative_to(out))] = {"from": [str(p)]}

        # Commands
        for p in commands:
            content = read_text(p)
            fm, body = parse_frontmatter(content)
            name = slugify(p.stem)
            desc = fm.get("description", infer_desc(body, p.stem))
            agent = fm.get("agent", "plan")
            dst = out / ".opencode" / "command" / f"{name}.md"
            write_text(dst, f"---\ndescription: {desc}\nagent: {agent}\n---\n\n{body}\n")
            manifest["generated"][str(dst.relative_to(out))] = {"from": [str(p)]}

        # opencode.jsonc (minimal schema + instructions + optional MCP)
        cfg = {
            "$schema": "https://opencode.ai/schema/v1.json",
            "instructions": ["./AGENTS.md", "./.opencode/instructions/skills/"],
        }
        if mcp_servers:
            mcp_block = {}
            for srv in mcp_servers:
                name = srv.get("name")
                config = srv.get("config")
                if name and config:
                    mcp_block[name] = config
            if mcp_block:
                cfg["mcp"] = mcp_block

        write_text(out / "opencode.jsonc", json.dumps(cfg, indent=2) + "\n")
        manifest["generated"]["opencode.jsonc"] = {"from": []}

    else:
        # codex-friendly bundle
        for am in agent_metadata:
            dst = out / "agents" / f"{am['slug']}.md"
            write_text(dst, f"# {am['name']}\n\nName: {am['name']}\nDescription: {am['desc']}\nTools needed: TBD\n\n---\n\n{am['body']}\n")
            manifest["generated"][str(dst.relative_to(out))] = {"from": [str(am['file'])]}

        for p in skills:
            content = read_text(p)
            fm, body = parse_frontmatter(content)
            name = slugify(p.stem)
            dst = out / "skills" / f"{name}.md"
            write_text(dst, f"# Skill: {p.stem}\n\n{body}\n")
            manifest["generated"][str(dst.relative_to(out))] = {"from": [str(p)]}

        for p in commands:
            content = read_text(p)
            fm, body = parse_frontmatter(content)
            name = slugify(p.stem)
            desc = fm.get("description", infer_desc(body, p.stem))
            dst = out / "commands" / f"{name}.md"
            write_text(dst, f"# Command: {p.stem}\n\nDescription: {desc}\n\n---\n\n{body}\n")
            manifest["generated"][str(dst.relative_to(out))] = {"from": [str(p)]}

        # MCP
        mcp_md = ["# MCP Migration\n"]
        if mcp_servers:
            mcp_md.append("## Detected MCP Servers\n")
            for srv in mcp_servers:
                mcp_md.append(f"### {srv['name']}\n")
                mcp_md.append(f"Source: `{srv['source']}`\n")
                mcp_md.append("```json\n" + json.dumps(srv['config'], indent=2) + "\n```\n")
        else:
            mcp_md.append("No MCP servers detected in .claude settings.\n")
        write_text(out / "MCP.md", "\n".join(mcp_md))
        manifest["generated"]["MCP.md"] = {"from": [s["source"] for s in mcp_servers]}

    # Report
    notes = []
    if mcp_servers:
        notes.append(f"- Extracted {len(mcp_servers)} MCP server(s) from settings files.")
    else:
        notes.append("- No MCP servers found in .claude settings.")
    if agent_metadata:
        notes.append(f"- Parsed {len(agent_metadata)} agent(s) with frontmatter metadata.")
    
    report = [
        f"# Migration Report\n",
        f"Target: `{target}`\n",
        "## Source files discovered\n",
        *[f"- {str(p)}" for p in sorted(set(src_files))],
        "\n## Generated files\n",
        *[f"- {k}" for k in sorted(manifest["generated"].keys())],
        "\n## Notes\n",
        *notes,
        "\n## Manual follow-ups\n",
        "- Review generated opencode.jsonc and adjust as needed.\n",
        "- If MCP servers were found, follow the setup instructions in MCP.md.\n",
    ]
    write_text(out / "MIGRATION_REPORT.md", "\n".join(report))

    write_text(out / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    return out

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, choices=["opencode", "codex"])
    args = ap.parse_args()
    out = convert(args.target)
    print(str(out))

if __name__ == "__main__":
    main()
