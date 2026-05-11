#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a lightweight exploratory project directory.")
    parser.add_argument("target_path", help="Directory to create or update with standard exploratory subdirectories.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_path = Path(args.target_path).expanduser().resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    for name in ("context", "tasks", "prompts", "logs"):
        (target_path / name).mkdir(exist_ok=True)

    print(f"Initialized exploratory project structure at {target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
