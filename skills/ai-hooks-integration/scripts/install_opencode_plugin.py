#!/usr/bin/env python3
"""Install an OpenCode plugin into the plugins directory.

Usage:
  install_opencode_plugin.py --name my-plugin --output ~/.config/opencode/plugins
  install_opencode_plugin.py --name my-plugin --output ~/.config/opencode/plugins --force
  install_opencode_plugin.py --name my-plugin --output ~/.config/opencode/plugins --websocket

Notes:
  - Creates a plugin that exports a function (required by OpenCode)
  - Uses correct hook parameter names (sessionID, callID, tool)
  - Optional WebSocket event support for external integrations
"""

import argparse
from pathlib import Path

# Basic template - just hooks
TEMPLATE_BASIC = '''/**
 * {plugin_name} Plugin for OpenCode
 */

module.exports = async function {export_name}(pluginInput) {{
  const cwd = pluginInput?.directory || process.cwd();

  return {{
    "tool.execute.before": async function (input, output) {{
      // input.tool - Tool name (string)
      // input.sessionID - Session identifier
      // input.callID - Unique call ID
      // output.args - Tool arguments (mutable)

      // Example: Block dangerous commands
      if (input.tool === "bash") {{
        const command = output?.args?.command || "";
        if (command.includes("rm -rf /")) {{
          throw new Error("Dangerous command blocked");
        }}
      }}
    }},

    "tool.execute.after": async function (input, output) {{
      // output.title - Execution title
      // output.output - Tool output
      // output.metadata - Additional data

      console.log(`Tool ${{input.tool}} completed`);
    }},
  }};
}};
'''

# WebSocket template - sends events to external server
TEMPLATE_WEBSOCKET = '''/**
 * {plugin_name} Plugin for OpenCode
 *
 * Sends tool execution events to WebSocket server.
 */

const WEBSOCKET_URL = "ws://127.0.0.1:8765";

async function sendEvent(eventType, payload) {{
  try {{
    const WebSocket = (await import("ws")).default;
    const ws = new WebSocket(WEBSOCKET_URL);

    return new Promise((resolve) => {{
      const timeout = setTimeout(() => {{ ws.close(); resolve(); }}, 1000);

      ws.on("open", () => {{
        ws.send(JSON.stringify({{ type: eventType, payload }}));
        clearTimeout(timeout);
        ws.close();
        resolve();
      }});

      ws.on("error", () => {{ clearTimeout(timeout); resolve(); }});
    }});
  }} catch {{
    // Silent fail if ws module not available
  }}
}}

function normalizeToolName(name) {{
  const map = {{
    shell: "Bash", bash: "Bash",
    read: "Read", read_file: "Read",
    write: "Write", write_file: "Write",
    edit: "Edit", edit_file: "Edit",
    grep: "Grep", search_files: "Grep",
    glob: "Glob", list_files: "Glob",
  }};
  return map[(name || "").toLowerCase()] || name || "Unknown";
}}

module.exports = async function {export_name}(pluginInput) {{
  const cwd = pluginInput?.directory || process.cwd();

  return {{
    "tool.execute.before": async function (input, output) {{
      await sendEvent("PreToolUse", {{
        source: "opencode",
        session_id: input.sessionID,
        cwd: cwd,
        tool_name: normalizeToolName(input.tool),
      }});
    }},

    "tool.execute.after": async function (input, output) {{
      await sendEvent("PostToolUse", {{
        source: "opencode",
        session_id: input.sessionID,
        cwd: cwd,
        tool_name: normalizeToolName(input.tool),
      }});
    }},
  }};
}};
'''


def main() -> None:
    ap = argparse.ArgumentParser(description="Install OpenCode plugin")
    ap.add_argument("--name", required=True, help="Plugin file name without extension")
    ap.add_argument("--output", required=True, help="Plugins directory")
    ap.add_argument("--force", action="store_true", help="Overwrite existing file")
    ap.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    ap.add_argument("--export", dest="export_name", default="PluginHook", help="Exported function name")
    ap.add_argument("--websocket", action="store_true", help="Include WebSocket event sending")
    args = ap.parse_args()

    out_dir = Path(args.output).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    plugin_path = out_dir / f"{args.name}.js"
    if plugin_path.exists() and not args.force:
        raise SystemExit(f"File exists: {plugin_path} (use --force to overwrite)")

    template = TEMPLATE_WEBSOCKET if args.websocket else TEMPLATE_BASIC
    content = template.format(
        plugin_name=args.name.replace("-", " ").title(),
        export_name=args.export_name,
    )

    if args.dry_run:
        print(f"[dry-run] write {plugin_path}")
        print(content)
        return

    plugin_path.write_text(content)
    print(f"Created: {plugin_path}")


if __name__ == "__main__":
    main()
