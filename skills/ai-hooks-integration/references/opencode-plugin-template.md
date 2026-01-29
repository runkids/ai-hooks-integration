# OpenCode Plugin Template

File: `~/.config/opencode/plugins/<name>.js`

## Critical: Plugin Must Export a Function

OpenCode plugins **must** export a function that returns a Hooks object, not an object directly.

```js
// ✅ CORRECT: Export a function
module.exports = async function MyPlugin(pluginInput) {
  return {
    "tool.execute.before": async (input, output) => { /* ... */ }
  };
};

// ❌ WRONG: Export object directly (causes "fn is not a function" error)
module.exports = {
  "tool.execute.before": async (input, output) => { /* ... */ }
};
```

## Complete Template

```js
/**
 * OpenCode Plugin Template
 *
 * Installation:
 *   cp my-plugin.js ~/.config/opencode/plugins/
 */

/**
 * Plugin function - receives PluginInput and returns Hooks
 *
 * @param {object} pluginInput - { app, directory, ... }
 * @returns {Promise<object>} Hooks object
 */
module.exports = async function MyPlugin(pluginInput) {
  // pluginInput contains:
  // - app: Application instance
  // - directory: Current working directory

  const cwd = pluginInput?.directory || process.cwd();

  return {
    /**
     * Called before tool execution
     * @param {object} input - { tool: string, sessionID: string, callID: string }
     * @param {object} output - { args: any }
     */
    "tool.execute.before": async function (input, output) {
      // input.tool is the tool name (string, e.g., "bash", "read", "write")
      // input.sessionID is the session identifier
      // input.callID is unique per tool call
      // output.args contains tool arguments

      // Example: Block dangerous commands
      if (input.tool === "bash") {
        const command = output?.args?.command || "";
        if (command.includes("rm -rf /")) {
          throw new Error("Dangerous command blocked");
        }
      }
    },

    /**
     * Called after tool execution
     * @param {object} input - { tool: string, sessionID: string, callID: string }
     * @param {object} output - { title: string, output: string, metadata: any }
     */
    "tool.execute.after": async function (input, output) {
      // output.title - Tool execution title
      // output.output - Tool output text
      // output.metadata - Additional metadata

      console.log(`Tool ${input.tool} completed: ${output.title}`);
    },
  };
};
```

## All Available Hooks

```js
module.exports = async function FullPlugin(pluginInput) {
  return {
    // Event hook - receives all events
    event: async ({ event }) => { },

    // Config hook - modify configuration
    config: async (config) => { },

    // Custom tool definitions
    tool: {
      myTool: {
        description: "My custom tool",
        args: { /* schema */ },
        async execute(args) { return "result"; }
      }
    },

    // Authentication hook
    auth: { /* auth config */ },

    // Chat hooks
    "chat.message": async (input, output) => { },
    "chat.params": async (input, output) => { },
    "chat.headers": async (input, output) => { },

    // Command/Tool hooks
    "command.execute.before": async (input, output) => { },
    "tool.execute.before": async (input, output) => { },
    "tool.execute.after": async (input, output) => { },

    // Permission hook
    "permission.ask": async (input, output) => { },

    // Experimental hooks
    "experimental.chat.messages.transform": async (input, output) => { },
    "experimental.chat.system.transform": async (input, output) => { },
    "experimental.session.compacting": async (input, output) => { },
    "experimental.text.complete": async (input, output) => { },
  };
};
```

## WebSocket Event Example

```js
const WEBSOCKET_URL = "ws://127.0.0.1:8765";

async function sendEvent(eventType, payload) {
  try {
    const WebSocket = (await import("ws")).default;
    const ws = new WebSocket(WEBSOCKET_URL);

    return new Promise((resolve) => {
      const timeout = setTimeout(() => { ws.close(); resolve(); }, 1000);

      ws.on("open", () => {
        ws.send(JSON.stringify({ type: eventType, payload }));
        clearTimeout(timeout);
        ws.close();
        resolve();
      });

      ws.on("error", () => { clearTimeout(timeout); resolve(); });
    });
  } catch { /* Silent fail */ }
}

module.exports = async function EventPlugin(pluginInput) {
  const cwd = pluginInput?.directory || process.cwd();

  return {
    "tool.execute.before": async (input, output) => {
      await sendEvent("PreToolUse", {
        source: "opencode",
        session_id: input.sessionID,
        tool_name: input.tool,
        cwd: cwd,
      });
    },
    "tool.execute.after": async (input, output) => {
      await sendEvent("PostToolUse", {
        source: "opencode",
        session_id: input.sessionID,
        tool_name: input.tool,
        cwd: cwd,
      });
    },
  };
};
```

## Notes

- OpenCode uses Bun runtime (supports both ESM and CommonJS)
- Plugin is loaded via dynamic import
- Each export must be a `Plugin` function (not an object)
- To block execution, throw an Error
- Hook parameters use `(input, output)` pattern - mutate `output` to modify behavior
- Field names: `sessionID` (not `session_id`), `callID` (not `call_id`)
