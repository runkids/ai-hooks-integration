#!/usr/bin/env python3
"""Install the same hook command across Claude/Gemini/Cursor and write OpenCode plugin.

Usage:
  install_all.py --command "/abs/path/to/hook" --name my-hook

Notes:
  - Adds tool-specific suffixes: --claude/--gemini/--cursor
  - Writes OpenCode plugin to ~/.config/opencode/plugins/<name>.js
"""

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MERGE = ROOT / "merge_hooks.py"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--command", required=True, help="Base hook command, absolute path recommended")
    ap.add_argument("--name", required=True, help="OpenCode plugin filename without extension")
    ap.add_argument("--dry-run", action="store_true", help="Print actions without writing")
    args = ap.parse_args()

    cmd = args.command
    dry = ["--dry-run"] if args.dry_run else []

    run([
        str(MERGE),
        "--tool", "claude",
        "--path", str(Path("~/.claude/settings.json").expanduser()),
        "--command", f"{cmd} --claude",
    ] + dry)

    run([
        str(MERGE),
        "--tool", "gemini",
        "--path", str(Path("~/.gemini/settings.json").expanduser()),
        "--command", f"{cmd} --gemini",
    ] + dry)

    run([
        str(MERGE),
        "--tool", "cursor",
        "--path", str(Path("~/.cursor/hooks.json").expanduser()),
        "--command", f"{cmd} --cursor",
    ] + dry)

    run([
        str(MERGE),
        "--tool", "opencode",
        "--path", str(Path("~/.config/opencode/plugins").expanduser() / f"{args.name}.js"),
    ] + dry)


if __name__ == "__main__":
    main()
