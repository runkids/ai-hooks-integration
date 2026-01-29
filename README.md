# AI Hooks Integration Skill

Reusable skill for integrating CLI hooks across multiple AI coding tools. Safe, idempotent configuration merges with tool-specific templates.

## Supported Tools

| Tool | Config | Hooks Support |
|------|--------|---------------|
| Claude Code | `~/.claude/settings.json` | ✅ Full |
| Gemini CLI | `~/.gemini/settings.json` | ✅ Full |
| Cursor | `~/.cursor/hooks.json` | ✅ Full |
| OpenCode | `~/.config/opencode/plugins/*.js` | ✅ Full |
| Gemini IDE | VS Code / JetBrains | ❌ No hooks API |

> **Note**: Gemini Code Assist (IDE plugin) does not have a hooks JSON API. Use Gemini CLI for automation.

## Installation

### Using [skillshare](https://github.com/runkids/skillshare)

```bash
skillshare install github.com/runkids/ai-hooks-integration
skillshare sync
```

### Using [add-skill](https://github.com/vercel-labs/skills)

```bash
npx skills add runkids/ai-hooks-integration
```

Install to specific agents:

```bash
npx skills add runkids/ai-hooks-integration -a claude-code -a cursor
```

### Manual

Clone to your skills directory:

```bash
git clone https://github.com/runkids/ai-hooks-integration.git \
  ~/.config/skillshare/skills/ai-hooks-integration
```

## Requirements

- Python 3.9+

## Usage

Install hooks for all tools:

```bash
scripts/install_all.py --command "/path/to/hook" --name my-hook
```

Remove hooks:

```bash
scripts/remove_all.py --command "/path/to/hook" --plugin ~/.config/opencode/plugins/my-hook.js
```

Add `--dry-run` to preview changes without writing.

## Structure

```
skills/ai-hooks-integration/
├── SKILL.md                              # Skill entry point
├── scripts/
│   ├── install_all.py                    # One-shot install
│   ├── remove_all.py                     # One-shot removal
│   ├── merge_hooks.py                    # Single-tool merge
│   ├── remove_hooks.py                   # Single-tool removal
│   ├── install_opencode_plugin.py        # OpenCode plugin installer
│   └── remove_opencode_plugin.py         # OpenCode plugin removal
└── references/
    ├── cli-hooks.md                      # Config paths & event lists
    ├── use-cases.md                      # Hook patterns by use case
    ├── hook-payload-examples.md          # Stdin/stdout formats
    ├── opencode-plugin-template.md       # OpenCode plugin template
    ├── claude-code-hook-skill.md         # Claude Code specifics
    ├── schemas/                          # JSON Schema per tool
    └── contracts/                        # I/O contracts (YAML)
```

## What It Provides

- **Cross-tool event mapping** - PreToolUse ↔ beforeShellExecution ↔ tool.execute.before ↔ BeforeTool
- **Use case patterns** - Security, auto-formatting, testing, notifications, logging, CI/CD
- **Safe JSON merge** - Idempotent, preserves existing hooks
- **Hook templates** - Ready-to-use configs per tool
- **Payload examples** - Stdin/stdout formats with field reference
- **OpenCode plugin template** - ES module format with all hooks

## License

MIT License
