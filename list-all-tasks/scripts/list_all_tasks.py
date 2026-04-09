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


def extract_first_numbered_item(section_text: str) -> str | None:
    match = re.search(r"^\d+\.\s+(.*?)(?=\n\d+\. |\n## |\Z)", section_text, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    return normalize_whitespace(match.group(1))


def extract_bullet_text(section_text: str) -> str | None:
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return normalize_whitespace(stripped[2:])
        if stripped and not stripped.startswith("#"):
            return normalize_whitespace(stripped)
    return None


def section_text(content: str, heading: str) -> str | None:
    pattern = rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    return match.group("body").strip()


def extract_unfinished_item(readme_path: Path, status: str) -> str:
    if is_completed(status):
        return "-"
    if not readme_path.is_file():
        return "未知"

    content = readme_path.read_text(encoding="utf-8")

    todos = section_text(content, "Top todos")
    if todos:
        item = extract_first_numbered_item(todos)
        if item:
            return truncate(item)

    next_action = section_text(content, "Next action")
    if next_action:
        item = extract_bullet_text(next_action)
        if item:
            return truncate(item)

    return "未知"


def parse_tasks(index_path: Path) -> list[dict[str, str]]:
    content = index_path.read_text(encoding="utf-8")
    tasks = []
    for match in ENTRY_RE.finditer(content):
        task = {key: normalize_whitespace(value) for key, value in match.groupdict(default="").items()}
        tasks.append(task)
    return tasks


def render_markdown(rows: list[dict[str, str]]) -> str:
    lines = [
        "| 任务 | 状态 | 是否完成 | 任务简述 | 未完成项 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        values = [
            row["task"],
            row["status"],
            row["completed"],
            row["summary"],
            row["unfinished"],
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
        task_name = task["alias"] or Path(task["path"]).parent.name
        rows.append(
            {
                "task": task_name,
                "status": display_status(task["status"]),
                "completed": "是" if is_completed(task["status"]) else "否",
                "summary": truncate(task["summary"], 120),
                "unfinished": extract_unfinished_item(readme_path, task["status"]),
            }
        )

    print(render_markdown(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
