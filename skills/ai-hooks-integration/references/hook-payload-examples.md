# Hook Payload Examples

Stdin/stdout formats for each tool's hooks.

## Table of Contents

- [Claude Code](#claude-code)
- [Gemini CLI](#gemini-cli)
- [Cursor](#cursor)
- [OpenCode](#opencode)

---

## Claude Code

### PreToolUse

**Input (stdin)**:
```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "rm -rf test"},
  "cwd": "/path/to/project",
  "session_id": "abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Allow output**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Approved by policy"
  }
}
```

**Deny output**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked: dangerous command"
  },
  "continue": false
}
```

**Ask user**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask"
  }
}
```

**Modify input**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "modifiedToolInput": {"command": "rm -rf test --dry-run"}
  }
}
```

### PostToolUse

**Input (stdin)**:
```json
{
  "tool_name": "Write",
  "tool_input": {"file_path": "/path/to/file.ts", "content": "..."},
  "tool_output": {"success": true},
  "cwd": "/path/to/project",
  "session_id": "abc123"
}
```

**Output with message**:
```json
{
  "continue": true,
  "systemMessage": "Lint errors found:\n  line 10: unused variable"
}
```

### Stop / SessionEnd

**Input (stdin)**:
```json
{
  "event": "Stop",
  "session_id": "abc123",
  "cwd": "/path/to/project"
}
```

**Output**:
```json
{"continue": true}
```

### UserPromptSubmit

**Input (stdin)**:
```json
{
  "prompt": "Fix the bug in auth.ts",
  "session_id": "abc123",
  "cwd": "/path/to/project"
}
```

**Output with context**:
```json
{
  "continue": true,
  "systemMessage": "Current branch: feature/auth\nModified: src/auth.ts, tests/auth.test.ts"
}
```

---

## Gemini CLI

### BeforeTool

**Input (stdin)**:
```json
{
  "tool_name": "run_shell_command",
  "tool_input": {"command": "rm -rf test"},
  "session_id": "..."
}
```

**Allow output**:
```json
{"decision": "allow", "reason": "Approved by policy"}
```

**Deny output**:
```json
{
  "decision": "deny",
  "reason": "Blocked: dangerous command",
  "systemMessage": "Command blocked by security policy"
}
```

### AfterTool

**Input (stdin)**:
```json
{
  "tool_name": "run_shell_command",
  "tool_input": {"command": "npm test"},
  "tool_output": {"exit_code": 0, "stdout": "..."}
}
```

**Output**:
```json
{"continue": true, "systemMessage": "All tests passed"}
```

---

## Cursor

### beforeShellExecution

**Input (stdin)**:
```json
{
  "command": "rm -rf test",
  "cwd": "/path/to/project"
}
```

**Allow output**:
```json
{"continue": true, "permission": "allow"}
```

**Deny output**:
```json
{
  "continue": false,
  "permission": "deny",
  "user_message": "Command blocked by policy",
  "agent_message": "Blocked: dangerous command detected"
}
```

### afterFileEdit

**Input (stdin)**:
```json
{
  "file_path": "/path/to/file.ts",
  "cwd": "/path/to/project"
}
```

**Output**:
```json
{"continue": true}
```

### stop

**Input (stdin)**:
```json
{
  "cwd": "/path/to/project"
}
```

**Output**:
```json
{"continue": true}
```

---

## OpenCode

OpenCode plugins receive structured args (not stdin JSON).

### tool.execute.before

**Function signature**:
```js
"tool.execute.before": async (input, output) => {
  // input.tool - tool name (string, e.g., "bash", "read", "write")
  // input.sessionID - session identifier
  // input.callID - unique call identifier
  // output.args - tool arguments (mutable)
}
```

**Access command**:
```js
const command = output?.args?.command ?? "";
```

**Allow**: Return normally (don't throw)

**Block**: Throw an Error
```js
throw new Error("Blocked: dangerous command");
```

### tool.execute.after

**Function signature**:
```js
"tool.execute.after": async (input, output) => {
  // input.tool - tool name
  // input.sessionID - session identifier
  // input.callID - unique call identifier
  // output.title - execution title
  // output.output - tool output text
  // output.metadata - additional metadata
}
```

### permission.ask

**Function signature**:
```js
"permission.ask": async (input, output) => {
  // input.permission - permission object
  // output.decision - "allow" | "deny" | "ask"
}
```

**Auto-allow**:
```js
output.decision = "allow";
```

---

## Field Reference

### Common Input Fields

| Field | Claude | Gemini | Cursor | OpenCode |
|-------|--------|--------|--------|----------|
| Tool name | `tool_name` | `tool_name` | - | `input.tool` |
| Command | `tool_input.command` | `tool_input.command` | `command` | `output.args.command` |
| File path | `tool_input.file_path` | `tool_input.file_path` | `file_path` | `output.args.file_path` |
| CWD | `cwd` | - | `cwd` | `pluginInput.directory` |
| Session | `session_id` | `session_id` | - | `input.sessionID` |

### Output Fields

| Action | Claude | Gemini | Cursor | OpenCode |
|--------|--------|--------|--------|----------|
| Allow | `permissionDecision: "allow"` | `decision: "allow"` | `permission: "allow"` | return |
| Deny | `permissionDecision: "deny"` | `decision: "deny"` | `permission: "deny"` | throw Error |
| Continue | `continue: true/false` | - | `continue: true/false` | - |
| Message | `systemMessage` | `systemMessage` | `agent_message` | console.log |
