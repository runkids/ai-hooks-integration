#!/usr/bin/env python3
"""Remove hook entries from Claude/Gemini/Cursor JSON configs.

Usage:
  remove_hooks.py --tool claude  --path ~/.claude/settings.json --command "<hook-cmd>"
  remove_hooks.py --tool gemini  --path ~/.gemini/settings.json --command "<hook-cmd>"
  remove_hooks.py --tool cursor  --path ~/.cursor/hooks.json     --command "<hook-cmd>"

Behavior:
  - Removes entries whose command contains the provided command string
  - Cleans up empty hook arrays and hooks objects
"""

import argparse
import json
from pathlib import Path

TOOL_CONFIG = {
    "claude": {"hook_key": "PreToolUse", "nested": True},
    "gemini": {"hook_key": "BeforeTool", "nested": True},
    "cursor": {"hook_key": "beforeShellExecution", "nested": False},
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


def filter_hooks(hooks, nested: bool, command: str):
    if not isinstance(hooks, list):
        return []
    kept = []
    for h in hooks:
        if not isinstance(h, dict):
            kept.append(h)
            continue
        if nested:
            inner = h.get("hooks", []) if isinstance(h, dict) else []
            new_inner = []
            for ih in inner:
                cmd = ih.get("command", "") if isinstance(ih, dict) else ""
                if command not in cmd:
                    new_inner.append(ih)
            if new_inner:
                h = dict(h)
                h["hooks"] = new_inner
                kept.append(h)
        else:
            cmd = h.get("command", "") if isinstance(h, dict) else ""
            if command not in cmd:
                kept.append(h)
    return kept


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", choices=TOOL_CONFIG.keys(), required=True)
    ap.add_argument("--path", required=True)
    ap.add_argument("--command", required=True)
    ap.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = ap.parse_args()

    path = Path(args.path).expanduser()
    data = load_json(path)

    hooks = data.get("hooks", {})
    cfg = TOOL_CONFIG[args.tool]
    key = cfg["hook_key"]

    if key in hooks:
        hooks[key] = filter_hooks(hooks[key], cfg["nested"], args.command)
        if not hooks[key]:
            hooks.pop(key, None)

    if isinstance(hooks, dict) and not hooks:
        data.pop("hooks", None)

    save_json(path, data, args.dry_run)


if __name__ == "__main__":
    main()
