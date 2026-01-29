# CLI Hooks Reference

## Table of Contents

- [Tool Overview](#tool-overview)
- [Event Comparison](#event-comparison)
- [Claude Code](#claude-code)
- [Cursor](#cursor)
- [OpenCode](#opencode)
- [Gemini CLI](#gemini-cli)
- [Gemini IDE (Code Assist)](#gemini-ide-code-assist)
- [Config Templates](#config-templates)
- [Docs](#docs)

---

## Tool Overview

| Tool       | Config File                      | Hook Key               | Matcher              |
|------------|----------------------------------|------------------------|----------------------|
| Claude     | `~/.claude/settings.json`        | `PreToolUse`           | `"Bash"` or `"*"`    |
| Gemini CLI | `~/.gemini/settings.json`        | `BeforeTool`           | `run_shell_command`  |
| Cursor     | `~/.cursor/hooks.json`           | `beforeShellExecution` | (none)               |
| OpenCode   | `~/.config/opencode/plugins/*.js`| ES module              | `tool.execute.before`|

**Note**: Gemini IDE (VS Code/JetBrains plugin) has no hooks JSON API.

---

## Event Comparison

| Event Type       | Claude Code       | Cursor             | OpenCode                  | Gemini CLI    |
|------------------|-------------------|--------------------|---------------------------|---------------|
| Before tool      | `PreToolUse`      | `beforeShellExecution` | `tool.execute.before` | `BeforeTool`  |
| After tool       | `PostToolUse`     | `afterFileEdit`    | `tool.execute.after`      | `AfterTool`   |
| Task complete    | `Stop`            | `stop`             | `event`                   | `Stop`        |
| Session start    | `SessionStart`    | -                  | `event`                   | -             |
| Session end      | `SessionEnd`      | -                  | `event`                   | -             |
| User prompt      | `UserPromptSubmit`| -                  | `chat.message`            | -             |
| Permission       | `PermissionRequest`| -                 | `permission.ask`          | -             |
| Notification     | `Notification`    | -                  | `event`                   | -             |

---

## Claude Code

Config: `~/.claude/settings.json` (global) or `.claude/settings.json` (project)

### Events

| Event | Matcher | Description | Common Use |
|-------|---------|-------------|------------|
| `PreToolUse` | ✓ | Before tool execution | Block dangerous ops, validate params |
| `PostToolUse` | ✓ | After tool execution | Run tests, format, log results |
| `UserPromptSubmit` | ✗ | Before prompt sent | Add context, inject instructions |
| `PermissionRequest` | ✓ | Permission dialog | Auto-allow/deny by policy |
| `Stop` | ✗ | Agent completes task | Notify, cleanup |
| `SubagentStop` | ✗ | Subagent completes | Track subtask completion |
| `SessionStart` | ✗ | Session begins | Setup environment |
| `SessionEnd` | ✗ | Session ends | Log session, cleanup |
| `PreCompact` | ✗ | Before context compaction | Save important context |
| `Notification` | ✓ | Notifications | Custom notification handling |

### Matcher Patterns

- `"Bash"` - match Bash tool only
- `"Write|Edit"` - match Write or Edit
- `"*"` - match all tools

### Hook Types

```json
// Command-based (deterministic)
{"type": "command", "command": "/path/to/script --flag"}

// Prompt-based (LLM decides)
{"type": "prompt", "prompt": "Check if this operation is safe"}
```

---

## Cursor

Config: `.cursor/hooks.json` (project)

### Events

| Event | Description | Common Use |
|-------|-------------|------------|
| `beforeShellExecution` | Before shell command | Block dangerous commands |
| `afterFileEdit` | After file modified | Lint, format, test |
| `stop` | Task completes | Desktop notification |

### Config Structure

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [...],
    "afterFileEdit": [...],
    "stop": [...]
  }
}
```

---

## OpenCode

Config: `~/.config/opencode/plugins/<name>.js`

**Critical**: Plugin must export a **function**, not an object.

### Events

| Event | Description | Common Use |
|-------|-------------|------------|
| `tool.execute.before` | Before tool execution | Block dangerous ops |
| `tool.execute.after` | After tool execution | Log, notify |
| `command.execute.before` | Before command execution | Validate commands |
| `chat.message` | Chat message sent | Add context |
| `chat.params` | Before API call | Modify model params |
| `permission.ask` | Permission requested | Auto-allow/deny |
| `event` | All events (passive) | Logging, analytics |

### Blocking Behavior

```js
// Allow: return normally
"tool.execute.before": async (input, output) => {
  // nothing thrown = allow
}

// Block: throw Error
"tool.execute.before": async (input, output) => {
  throw new Error("Blocked: reason");
}
```

See `opencode-plugin-template.md` for complete template.

---

## Gemini CLI

Config: `~/.gemini/settings.json`

### Events

| Event | Matcher | Description | Common Use |
|-------|---------|-------------|------------|
| `BeforeTool` | ✓ | Before tool execution | Validate params, add context |
| `AfterTool` | ✓ | After tool execution | Log results, run tests |
| `Stop` | ✗ | Agent completes | Notify, cleanup |

### Common Uses

- Add context (e.g., git history before operations)
- Validate tool parameters
- Enforce security/compliance policies
- Log usage and outputs
- Dynamically adjust available tools

### Config Structure

```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "run_shell_command",
        "hooks": [{"type": "command", "command": "<hook>"}]
      }
    ]
  }
}
```

---

## Gemini IDE (Code Assist)

**VS Code / JetBrains plugin - No hooks API**

Gemini Code Assist in IDEs does NOT have a hooks JSON API like Claude/Cursor/OpenCode.

Available interactions (manual, not automated):

- Chat suggestions
- Inline completions
- Quick Pick commands (`/simplify`, `/doc this function`)
- Diff view for changes
- Manual accept/reject suggestions

If you need hooks with Gemini, use **Gemini CLI**, not the IDE plugin.

---

## Config Templates

### Claude Code (`~/.claude/settings.json`)

**PreToolUse** (with matcher):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "<hook> --claude"}]
      }
    ]
  }
}
```

**Events without matcher** (SessionStart, Stop, etc.):
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [{"type": "command", "command": "<hook> --claude"}]
      }
    ]
  }
}
```

### Gemini CLI (`~/.gemini/settings.json`)
```json
{
  "hooks": {
    "BeforeTool": [
      {
        "matcher": "run_shell_command",
        "hooks": [{"type": "command", "command": "<hook> --gemini"}]
      }
    ]
  }
}
```

### Cursor (`~/.cursor/hooks.json`)
```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [{"command": "<hook> --cursor"}]
  }
}
```

### OpenCode (`~/.config/opencode/plugins/<name>.js`)

```js
module.exports = async function MyPlugin(pluginInput) {
  return {
    "tool.execute.before": async (input, output) => {
      // input.tool - tool name (string)
      // input.sessionID - session identifier
      // output.args - tool arguments
    },
    "tool.execute.after": async (input, output) => {
      // output.title, output.output, output.metadata
    },
  };
};
```

---

## Docs

- Claude: https://code.claude.com/docs/en/hooks
- Gemini CLI: https://googlegemini.github.io/gemini-cli/docs/cli/customization#hooks
- Cursor: https://docs.cursor.com/agent/hooks
- OpenCode: Check `~/.config/opencode/` for plugin examples
