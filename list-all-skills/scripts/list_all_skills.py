#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List project-local skills and local Codex skills."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing skills/ (default: current directory).",
    )
    parser.add_argument(
        "--source",
        help="Override the project skills directory. Defaults to <project-root>/skills.",
    )
    parser.add_argument(
        "--target",
        default=str(Path("~/.codex/skills").expanduser()),
        help="Local Codex skills directory (default: ~/.codex/skills).",
    )
    return parser.parse_args()


def list_skills(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    return sorted(
        entry.name
        for entry in root.iterdir()
        if entry.is_dir()
        and not entry.name.startswith(".")
        and (entry / "SKILL.md").is_file()
    )


def print_section(title: str, names: list[str]) -> None:
    print(f"{title} ({len(names)})")
    if not names:
        print("- (none)")
        return
    for name in names:
        print(f"- {name}")


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source_dir = Path(args.source).resolve() if args.source else project_root / "skills"
    target_dir = Path(args.target).expanduser().resolve()

    project_skills = list_skills(source_dir)
    local_skills = list_skills(target_dir)

    project_set = set(project_skills)
    local_set = set(local_skills)

    shared = sorted(project_set & local_set)
    project_only = sorted(project_set - local_set)
    local_only = sorted(local_set - project_set)

    print("Paths")
    print(f"- project source: {source_dir}")
    print(f"- local target: {target_dir}")
    print()
    print_section("Project skills", project_skills)
    print()
    print_section("Local skills", local_skills)
    print()
    print_section("Shared", shared)
    print()
    print_section("Project-only", project_only)
    print()
    print_section("Local-only", local_only)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
