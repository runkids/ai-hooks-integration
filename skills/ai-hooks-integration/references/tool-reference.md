# Tool Reference

Complete reference for all supported tools: config paths, events, payloads, templates.

## Table of Contents

- [Quick Reference](#quick-reference)
- [Claude Code](#claude-code)
- [Gemini CLI](#gemini-cli)
- [Cursor](#cursor)
- [OpenCode](#opencode)
- [CLI Wrapper](#cli-wrapper)
- [Field Mapping](#field-mapping)

---

## Quick Reference

| Tool | Config | Pre-event | Post-event | Nesting |
|------|--------|-----------|------------|---------|
| Claude | `~/.claude/settings.json` | PreToolUse | PostToolUse | nested |
| Gemini | `~/.gemini/settings.json` | BeforeTool | AfterTool | nested |
| Cursor | `~/.cursor/hooks.json` | beforeShellExecution | afterFileEdit | flat |
| OpenCode | `~/.config/opencode/plugins/*.js` | tool.execute.before | tool.execute.after | plugin |

---

## Claude Code

### Events

| Event | Matcher | Description |
|-------|---------|-------------|
| PreToolUse | ✓ | Before tool execution |
| PostToolUse | ✓ | After tool execution |
| UserPromptSubmit | ✗ | Before prompt sent |
| PermissionRequest | ✓ | Permission dialog |
| Stop | ✗ | Agent completes |
| SessionStart | ✗ | Session begins |
| SessionEnd | ✗ | Session ends |

Matcher patterns: `"Bash"` (exact), `"Write|Edit"` (OR), `"*"` (all)

### Config Template

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash", "hooks": [{"type": "command", "command": "<hook>"}]}
    ]
  }
}
```

### PreToolUse I/O

**Input:**
```json
{"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "/project", "session_id": "..."}
```

**Allow:**
```json
{"hookSpecificOutput": {"permissionDecision": "allow"}}
```

**Deny:**
```json
{"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "Blocked"}, "continue": false}
```

**Modify:**
```json
{"hookSpecificOutput": {"permissionDecision": "allow", "modifiedToolInput": {"command": "ls -la"}}}
```

### PostToolUse I/O

**Input:**
```json
{"tool_name": "Write", "tool_input": {...}, "tool_output": {...}, "cwd": "/project"}
```

**Output:**
```json
{"continue": true, "systemMessage": "File formatted successfully"}
```

---

## Gemini CLI

### Events

| Event | Matcher | Description |
|-------|---------|-------------|
| BeforeTool | ✓ | Before tool execution |
| AfterTool | ✓ | After tool execution |
| Stop | ✗ | Agent completes |

### Config Template

```json
{
  "hooks": {
    "BeforeTool": [
      {"matcher": "run_shell_command", "hooks": [{"type": "command", "command": "<hook>"}]}
    ]
  }
}
```

### BeforeTool I/O

**Input:**
```json
{"tool_name": "run_shell_command", "tool_input": {"command": "ls"}, "session_id": "..."}
```

**Allow:**
```json
{"decision": "allow"}
```

**Deny:**
```json
{"decision": "deny", "reason": "Blocked", "systemMessage": "..."}
```

---

## Cursor

### Events

| Event | Description |
|-------|-------------|
| beforeShellExecution | Before shell command |
| afterFileEdit | After file modified |
| stop | Task completes |

### Config Template

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [{"command": "<hook>"}]
  }
}
```

### beforeShellExecution I/O

**Input:**
```json
{"command": "ls", "cwd": "/project"}
```

**Allow:**
```json
{"continue": true, "permission": "allow"}
```

**Deny:**
```json
{"continue": false, "permission": "deny", "agent_message": "Blocked"}
```

---

## OpenCode

**Critical**: Plugin must export a **function**, not an object.

### Events

| Event | Description |
|-------|-------------|
| tool.execute.before | Before tool execution |
| tool.execute.after | After tool execution |
| permission.ask | Permission requested |
| chat.message | Chat message sent |
| event | All events (passive) |

### Plugin Template

```js
module.exports = async function MyPlugin(pluginInput) {
  const cwd = pluginInput?.directory || process.cwd();

  return {
    "tool.execute.before": async (input, output) => {
      // input.tool, input.sessionID, input.callID
      // output.args (mutable)
      const cmd = output?.args?.command || "";
      if (cmd.includes("rm -rf /")) {
        throw new Error("Blocked");  // Block = throw
      }
    },

    "tool.execute.after": async (input, output) => {
      // output.title, output.output, output.metadata
      console.log(`Completed: ${input.tool}`);
    },
  };
};
```

### All Available Hooks

```js
{
  "tool.execute.before": async (input, output) => {},
  "tool.execute.after": async (input, output) => {},
  "command.execute.before": async (input, output) => {},
  "chat.message": async (input, output) => {},
  "chat.params": async (input, output) => {},
  "permission.ask": async (input, output) => {},
  "event": async ({ event }) => {},
}
```

---

## CLI Wrapper

For tools **without** hooks API (gh, aws, kubectl, docker).

### Flow

```
User → ~/.local/bin/gh (wrapper) → Pre-hook → /usr/bin/gh → Post-hook → Exit
```

### Install

```bash
scripts/install_cli_wrapper.py --cli gh --hook "/path/to/hook"
```

### Pre-hook I/O

**Input:**
```json
{"cli": "gh", "args": ["pr", "create"], "cwd": "/project", "phase": "pre"}
```

**Allow:** Exit 0 or `{"decision": "allow"}`

**Deny:**
```json
{"decision": "deny", "reason": "Blocked"}
```

### Post-hook I/O

**Input:**
```json
{"cli": "gh", "args": ["pr", "create"], "cwd": "/project", "phase": "post", "exit_code": 0}
```

### Templates

| Template | Dependencies | JSON I/O |
|----------|--------------|----------|
| bash | jq | Yes |
| python | None | Yes |
| minimal | None | No (CLI args) |

---

## Field Mapping

### Input Fields

| Field | Claude | Gemini | Cursor | OpenCode |
|-------|--------|--------|--------|----------|
| Tool name | `tool_name` | `tool_name` | - | `input.tool` |
| Command | `tool_input.command` | `tool_input.command` | `command` | `output.args.command` |
| CWD | `cwd` | - | `cwd` | `pluginInput.directory` |
| Session | `session_id` | `session_id` | - | `input.sessionID` |

### Output Fields

| Action | Claude | Gemini | Cursor | OpenCode |
|--------|--------|--------|--------|----------|
| Allow | `permissionDecision: "allow"` | `decision: "allow"` | `permission: "allow"` | return |
| Deny | `permissionDecision: "deny"` | `decision: "deny"` | `permission: "deny"` | throw |
| Message | `systemMessage` | `systemMessage` | `agent_message` | console.log |

---

## External Docs

- Claude: https://code.claude.com/docs/en/hooks
- Gemini: https://googlegemini.github.io/gemini-cli/docs/cli/customization#hooks
- Cursor: https://docs.cursor.com/agent/hooks
