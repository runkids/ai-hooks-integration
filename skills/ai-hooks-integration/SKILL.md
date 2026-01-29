---
name: ai-hooks-integration
description: |
  Integrate lifecycle hooks across AI coding tools (Claude Code, Gemini CLI, Cursor, OpenCode).
  Use when: (1) installing/removing hooks to settings.json/hooks.json, (2) creating OpenCode plugins,
  (3) setting up auto-formatting, testing, notifications, or security policies,
  (4) migrating hooks between tools.
  Triggers on: "add hook", "install hook", "wire up hooks", "hook integration", "PostToolUse",
  "PreToolUse", "afterFileEdit", "beforeShellExecution", "auto-format on save", "notify on complete".
  Note: Gemini IDE (VS Code/JetBrains) has no hooks API; use Gemini CLI for hooks.
---

# AI Hooks Integration

## Quick Commands

Install hooks for all tools:
```bash
scripts/install_all.py --command "/path/to/hook" --name my-hook
```

Remove hooks for all tools:
```bash
scripts/remove_all.py --command "/path/to/hook" --plugin ~/.config/opencode/plugins/my-hook.js
```

Add `--dry-run` to preview changes.

## Workflow

1. Run `scripts/install_all.py` with the hook command and plugin name
2. Restart each tool to load hooks
3. Test with a sample command

## Single-Tool Operations

```bash
# Add hook
scripts/merge_hooks.py --tool claude|gemini|cursor --path <config> --command "<hook>"

# Remove hook
scripts/remove_hooks.py --tool claude|gemini|cursor --path <config> --command "<hook>"

# OpenCode plugin
scripts/install_opencode_plugin.py --name my-hook --output ~/.config/opencode/plugins
scripts/remove_opencode_plugin.py --path ~/.config/opencode/plugins/my-hook.js
```

## References

| File | When to Read |
|------|--------------|
| `references/cli-hooks.md` | Need config paths, event lists, or JSON templates |
| `references/use-cases.md` | Need hook patterns (security, formatting, testing, notifications) |
| `references/hook-payload-examples.md` | Need stdin/stdout payload formats |
| `references/opencode-plugin-template.md` | Creating OpenCode plugins |
| `references/claude-code-hook-skill.md` | Need Claude Code hook event details |
| `references/schemas/` | Validating hook config JSON |
| `references/contracts/` | Checking input/output contracts |

## Tool Quick Reference

| Tool | Config | Common Events |
|------|--------|---------------|
| Claude | `~/.claude/settings.json` | PreToolUse, PostToolUse, Stop, SessionStart |
| Gemini CLI | `~/.gemini/settings.json` | BeforeTool, AfterTool, Stop |
| Cursor | `~/.cursor/hooks.json` | beforeShellExecution, afterFileEdit, stop |
| OpenCode | `~/.config/opencode/plugins/*.js` | tool.execute.before, tool.execute.after |

**Gemini IDE** (VS Code/JetBrains): No hooks API. Use Gemini CLI for automation.

## Key Behaviors

- **Idempotent**: Existing hooks preserved; duplicates skipped
- **Safe merge**: Only adds new entries; never overwrites
- **Cleanup**: Removing hooks also removes empty arrays/objects
