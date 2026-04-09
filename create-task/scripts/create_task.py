#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


README_TEMPLATE = """# Task: {title}

## Task summary

- Repository: {repository}
- Background:
- Current goal: {description}

## Current task status

- Status: planned
- Phase: planning

## Related commits

- Implementation range:
- Hardening or follow-up commits:
- Helper/tool/test commits:
- Baseline or compatibility commits:

## Topic documents

- [findings/README.md](findings/README.md)
  - finding-oriented notes index
- [plan/README.md](plan/README.md)
  - planning-oriented notes index
- [implement/README.md](implement/README.md)
  - implementation-oriented notes index
- [test/README.md](test/README.md)
  - test-oriented notes index

## Top findings

1. `P0` TODO
2. `P1` TODO

## Top todos

1. `P0` TODO
2. `P1` TODO

## Current checkpoints

- Local verification:
- E2E verification:

## Notes

- Keep this page short.
- Push detail into subdirectories.
"""


SUBDOC_TEMPLATES = {
    "findings/README.md": "# Task Findings\n\n## Scope\n\n- This directory tracks finding-oriented notes for the task.\n",
    "plan/README.md": "# Task Plans\n\n## Scope\n\n- This directory tracks planning-oriented notes for the task.\n",
    "implement/README.md": "# Task Implementation Notes\n\n## Scope\n\n- This directory tracks implementation-oriented notes for the task.\n",
    "test/README.md": "# Task Tests\n\n## Scope\n\n- This directory tracks verification and test notes for the task.\n",
    "test/atlas-test.md": "# Atlas-Test Notes\n\n## Scope\n\n- Record atlas-test execution notes for this task.\n",
    "test/blackbox.md": "# Blackbox Notes\n\n## Scope\n\n- Record blackbox verification notes for this task.\n",
    "environment.md": "# Task Environment\n\n## Scope\n\n- Record environment assumptions, revisions, binary paths, and dependency notes for this task.\n",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a new task doc scaffold.")
    parser.add_argument("task_name", help="Task name slug, for example investigate-foo.")
    parser.add_argument("--description", default="TODO", help="Optional one-line task description.")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing atlas-ai-docs/tasks and atlas-ai-docs/tasks.md.",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Date prefix in YYYY-MM-DD format. Defaults to today.",
    )
    return parser.parse_args()


def slugify(text: str) -> str:
    text = text.strip().lower().replace("_", "-").replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def titleize(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-") if part)


def append_index_entry(index_path: Path, dir_name: str, description: str) -> None:
    entry = (
        f"\n- [{dir_name}/README.md](tasks/{dir_name}/README.md)\n"
        f"  - Status: planned\n"
        f"  - Summary: {description}\n"
    )
    with index_path.open("a", encoding="utf-8") as handle:
        handle.write(entry)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    tasks_root = project_root / "atlas-ai-docs" / "tasks"
    index_path = project_root / "atlas-ai-docs" / "tasks.md"

    slug = slugify(args.task_name)
    if not slug:
        raise SystemExit("error: task name normalized to empty slug")

    dir_name = f"{args.date}-{slug}"
    task_dir = tasks_root / dir_name
    if task_dir.exists():
        raise SystemExit(f"error: task directory already exists: {task_dir}")

    task_dir.mkdir(parents=True, exist_ok=False)
    title = titleize(slug)
    (task_dir / "README.md").write_text(
        README_TEMPLATE.format(title=title, repository="atlas/", description=args.description),
        encoding="utf-8",
    )

    for rel_path, content in SUBDOC_TEMPLATES.items():
        path = task_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    append_index_entry(index_path, dir_name, args.description)

    print(f"created: {task_dir}")
    print("updated index: yes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
