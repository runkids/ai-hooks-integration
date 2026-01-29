# Claude Code Hook Reference

Source: https://code.claude.com/docs/en/hooks

## Event Overview

| Event | Matcher | Timing | Use Case |
|-------|---------|--------|----------|
| PreToolUse | ✓ | Before tool execution | Validate params, block ops |
| PostToolUse | ✓ | After tool execution | Format, test, log |
| UserPromptSubmit | ✗ | Before prompt sent | Add context |
| PermissionRequest | ✓ | Permission dialog | Auto-allow/deny |
| Stop | ✗ | Agent completes | Notify, cleanup |
| SubagentStop | ✗ | Subagent completes | Track subtasks |
| SessionStart | ✗ | Session begins | Setup |
| SessionEnd | ✗ | Session ends | Log, cleanup |
| PreCompact | ✗ | Before context compaction | Save context |
| Notification | ✓ | Notifications | Custom handling |

## Hook Types

**Command-based** (deterministic):
```json
{"type": "command", "command": "/path/to/script --flag", "timeout": 30000}
```

**Prompt-based** (LLM decides):
```json
{"type": "prompt", "prompt": "Check if this operation is safe"}
```

## Config Shapes

**User settings** (`~/.claude/settings.json`):
```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "..."}]}
    ]
  }
}
```

**Plugin hooks.json** (wrapper object):
```json
{
  "hooks": {
    "PreToolUse": [...]
  }
}
```

## PreToolUse Output

Allow:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Approved by policy"
  }
}
```

Deny:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked by policy"
  },
  "continue": false
}
```

Ask user:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask"
  }
}
```

Input mutation:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "modifiedToolInput": {"command": "modified command"}
  }
}
```

## Standard Output Fields

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "Message to show agent"
}
```

- `continue`: false stops execution
- `suppressOutput`: hide hook output
- `systemMessage`: inject context to agent

## Exit Codes

- `0`: Success, continue
- Non-zero: Error (may block depending on hook config)

## Environment Variables

- `CLAUDE_PLUGIN_ROOT`: Plugin directory path
- `CLAUDE_ENV_FILE`: Path to env file

## Hook Input (stdin)

```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "ls -la"},
  "cwd": "/path/to/project",
  "session_id": "...",
  "timestamp": "..."
}
```

## Matcher Patterns

- `"Bash"` - Exact match
- `"Write|Edit"` - OR match
- `"*"` - Match all tools

## Common Patterns

**Auto-format on Write/Edit**:
```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Write|Edit",
      "hooks": [{"type": "command", "command": "prettier --write $FILE"}]
    }]
  }
}
```

**Block dangerous Bash commands**:
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "/path/to/security-check.sh"}]
    }]
  }
}
```

**Notify on Stop**:
```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{"type": "command", "command": "osascript -e 'display notification \"Done\"'"}]
    }]
  }
}
```
