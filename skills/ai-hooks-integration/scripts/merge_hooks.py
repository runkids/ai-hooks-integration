#!/usr/bin/env python3
"""Merge/inject hooks into Claude/Gemini/Cursor JSON configs (and OpenCode plugin).

Usage:
  merge_hooks.py --tool claude  --path ~/.claude/settings.json --command "<hook-cmd> --claude"
  merge_hooks.py --tool gemini  --path ~/.gemini/settings.json --command "<hook-cmd> --gemini"
  merge_hooks.py --tool cursor  --path ~/.cursor/hooks.json     --command "<hook-cmd> --cursor"
  merge_hooks.py --tool opencode --path ~/.config/opencode/plugins/<name>.js

Behavior:
  - Creates missing parents
  - Avoids duplicates (command contains the provided command string)
  - Writes pretty JSON
  - OpenCode writes a generic ES module template
"""

import argparse
import json
from pathlib import Path

TOOL_CONFIG = {
    "claude": {
        "hook_key": "PreToolUse",
        "default_matcher": "Bash",
        "nested": True,  # hooks[].hooks[]
    },
    "gemini": {
        "hook_key": "BeforeTool",
        "default_matcher": "run_shell_command",
        "nested": True,
    },
    "cursor": {
        "hook_key": "beforeShellExecution",
        "default_matcher": None,
        "nested": False,  # hooks[].command
        "version": 1,
    },
    "opencode": {
        "plugin_template": "opencode_plugin",
    },
}


def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_json(path: Path, data: dict, dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def has_hook(hooks, nested: bool, command: str) -> bool:
    if not isinstance(hooks, list):
        return False
    for h in hooks:
        if nested:
            inner = h.get("hooks", []) if isinstance(h, dict) else []
            for ih in inner:
                cmd = ih.get("command", "") if isinstance(ih, dict) else ""
                if command in cmd:
                    return True
        else:
            cmd = h.get("command", "") if isinstance(h, dict) else ""
            if command in cmd:
                return True
    return False


OPENCODE_TEMPLATE = '''\
export const PluginHook = async () => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool !== "bash") return;
      const command = output?.args?.command ?? input?.args?.command ?? "";
      if (!command) return;
      // TODO: run your checker and throw to block
    }
  };
};
'''


def write_opencode_plugin(path: Path, force: bool, dry_run: bool) -> None:
    if path.exists() and not force:
        return
    if dry_run:
        print(f"[dry-run] write {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(OPENCODE_TEMPLATE)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", choices=TOOL_CONFIG.keys(), required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--command", help="Hook command to inject (not used for opencode)")
    ap.add_argument("--matcher", help="Override matcher for nested hooks")
    ap.add_argument("--force", action="store_true", help="Overwrite existing plugin file (opencode)")
    ap.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = ap.parse_args()

    path = Path(args.path).expanduser()

    if args.tool == "opencode":
        write_opencode_plugin(path, args.force, args.dry_run)
        return

    if not args.command:
        raise SystemExit("--command is required for claude/gemini/cursor")

    cfg = TOOL_CONFIG[args.tool]
    data = load_json(path)

    if args.tool == "cursor" and "version" not in data:
        data["version"] = cfg.get("version", 1)

    hooks = data.setdefault("hooks", {})
    hook_key = cfg["hook_key"]

    if hook_key not in hooks or not isinstance(hooks[hook_key], list):
        hooks[hook_key] = []

    if has_hook(hooks[hook_key], cfg["nested"], args.command):
        save_json(path, data, args.dry_run)
        return

    matcher = args.matcher if args.matcher is not None else cfg.get("default_matcher")

    if cfg["nested"]:
        hooks[hook_key].append(
            {
                "matcher": matcher,
                "hooks": [
                    {
                        "type": "command",
                        "command": args.command,
                    }
                ],
            }
        )
    else:
        hooks[hook_key].append({"command": args.command})

    save_json(path, data, args.dry_run)


if __name__ == "__main__":
    main()
