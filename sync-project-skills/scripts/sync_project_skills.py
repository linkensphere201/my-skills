#!/usr/bin/env python3

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync project-local skills into ~/.codex/skills without deleting local files."
    )
    parser.add_argument(
        "skills",
        nargs="*",
        help="Optional skill names to sync. Defaults to all project skills.",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing skills/ (default: current directory).",
    )
    parser.add_argument(
        "--source",
        help="Override the source skills directory. Defaults to <project-root>/skills.",
    )
    parser.add_argument(
        "--target",
        default=str(Path("~/.codex/skills").expanduser()),
        help="Target skill directory (default: ~/.codex/skills).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without copying files.",
    )
    return parser.parse_args()


def is_skill_dir(path: Path) -> bool:
    return path.is_dir() and (path / "SKILL.md").is_file()


def list_source_skills(source_dir: Path) -> dict[str, Path]:
    return {
        entry.name: entry
        for entry in sorted(source_dir.iterdir())
        if not entry.name.startswith(".") and is_skill_dir(entry)
    }


def ensure_parent(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_if_changed(src: Path, dst: Path, dry_run: bool) -> bool:
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        return False

    ensure_parent(dst, dry_run)
    if not dry_run:
        shutil.copy2(src, dst)
    return True


def sync_skill(src_dir: Path, dst_dir: Path, dry_run: bool) -> tuple[str, int]:
    changed_files = 0
    created = not dst_dir.exists()

    for src_path in sorted(src_dir.rglob("*")):
        if src_path.is_dir():
            continue
        rel_path = src_path.relative_to(src_dir)
        dst_path = dst_dir / rel_path
        if copy_if_changed(src_path, dst_path, dry_run):
            changed_files += 1

    if changed_files == 0:
        return "unchanged", 0
    if created:
        return "created", changed_files
    return "updated", changed_files


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    source_dir = Path(args.source).resolve() if args.source else project_root / "skills"
    target_dir = Path(args.target).expanduser().resolve()

    if not source_dir.is_dir():
        print(f"error: source directory not found: {source_dir}")
        return 1

    source_skills = list_source_skills(source_dir)
    if not source_skills:
        print(f"error: no project skills found in {source_dir}")
        return 1

    selected_names = args.skills or list(source_skills.keys())
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"source: {source_dir}")
    print(f"target: {target_dir}")
    print(f"dry-run: {'yes' if args.dry_run else 'no'}")

    skipped = []
    results = []
    for name in selected_names:
        src_dir = source_skills.get(name)
        if src_dir is None:
            skipped.append(name)
            continue
        status, changed_files = sync_skill(src_dir, target_dir / name, args.dry_run)
        results.append((name, status, changed_files))

    for name, status, changed_files in results:
        print(f"{name}: {status} ({changed_files} file(s))")

    for name in skipped:
        print(f"{name}: skipped (not found in project skills)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
