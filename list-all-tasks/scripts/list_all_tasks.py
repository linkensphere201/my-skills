#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


ENTRY_RE = re.compile(
    r"^- \[(?P<label>[^\]]+)\]\((?P<path>[^)]+)\)\n"
    r"(?:  - Status: (?P<status>.+)\n)"
    r"(?:(?:  - Alias: (?P<alias>.+)\n))?"
    r"(?:  - Summary: (?P<summary>.+)\n)",
    re.MULTILINE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List documented tasks in a compact markdown table."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing atlas-ai-docs/tasks.md.",
    )
    parser.add_argument(
        "--index",
        help="Override task index path. Defaults to <project-root>/atlas-ai-docs/tasks.md.",
    )
    parser.add_argument(
        "--format",
        default="markdown",
        choices=["markdown"],
        help="Output format.",
    )
    return parser.parse_args()


def normalize_whitespace(text: str) -> str:
    return " ".join(text.strip().split())


def strip_code_quotes(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("`") and stripped.endswith("`") and len(stripped) >= 2:
        return stripped[1:-1]
    return stripped


def display_status(status: str) -> str:
    mapping = {
        "active": "进行中",
        "completed": "已完成",
        "done": "已完成",
        "planned": "已规划",
        "blocked": "阻塞",
        "active-review": "评审中",
        "implemented-under-review": "已实现待评审",
    }
    normalized = status.strip().lower()
    return mapping.get(normalized, status)


def truncate(text: str, limit: int = 140) -> str:
    text = normalize_whitespace(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def is_completed(status: str) -> bool:
    return status.strip().lower() in {"completed", "done"}


def parse_tasks(index_path: Path) -> list[dict[str, str]]:
    content = index_path.read_text(encoding="utf-8")
    tasks = []
    for match in ENTRY_RE.finditer(content):
        task = {key: normalize_whitespace(value) for key, value in match.groupdict(default="").items()}
        tasks.append(task)
    return tasks


def sort_key(row: dict[str, str]) -> tuple[str, str]:
    task = row["task"]
    match = re.match(r"^(\d{4}-\d{2}-\d{2})-", task)
    date_prefix = match.group(1) if match else ""
    return (date_prefix, task)


def render_table(title: str, rows: list[dict[str, str]]) -> str:
    lines = [
        f"## {title}",
        "",
        "| 任务 | 状态 | 任务简述 |",
        "| --- | --- | --- |",
    ]
    if not rows:
        lines.append("| - | - | - |")
        return "\n".join(lines)

    for row in rows:
        values = [
            row["task"],
            row["status"],
            row["summary"],
        ]
        escaped = [value.replace("|", "\\|") for value in values]
        lines.append(f"| {' | '.join(escaped)} |")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    index_path = Path(args.index).resolve() if args.index else project_root / "atlas-ai-docs" / "tasks.md"

    tasks = parse_tasks(index_path)
    rows = []
    for task in tasks:
        readme_path = (index_path.parent / task["path"]).resolve()
        display_task_name = Path(task["path"]).parent.name
        raw_status = task["status"]
        rows.append(
            {
                "task": display_task_name,
                "status": display_status(raw_status),
                "is_completed": is_completed(raw_status),
                "summary": truncate(task["summary"], 120),
            }
        )

    open_rows = [row for row in rows if not row["is_completed"]]
    done_rows = [row for row in rows if row["is_completed"]]
    open_rows.sort(key=sort_key, reverse=True)
    done_rows.sort(key=sort_key, reverse=True)

    output = [
        render_table("未完成任务", open_rows),
        "",
        render_table("已完成任务", done_rows),
    ]
    print("\n".join(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
