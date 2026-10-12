#!/usr/bin/env python3
"""Delegate project creation to the selected, versioned template checkout."""

from __future__ import annotations

import argparse
from pathlib import Path
import runpy
import sys


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--project-root", "--output-root", default=".")
    parser.add_argument("--template-dir")
    args, _ = parser.parse_known_args()
    template = Path(args.template_dir) if args.template_dir else Path(args.project_root) / "project-template"
    script = template.resolve() / "scripts" / "create_project.py"
    if not script.is_file():
        print(
            f"error: template generator not found: {script}\n"
            "Initialize the workspace submodule with git submodule update --init --recursive, "
            "or provide --template-dir pointing to a standalone checkout.",
            file=sys.stderr,
        )
        return 2
    generator = runpy.run_path(str(script))
    return generator["main"](sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
