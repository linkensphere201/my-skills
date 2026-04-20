#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


PROJECT_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-.+")
CHECKBOX_RE = re.compile(r"^- \[(?P<mark>[ xX])\]\s*(?P<text>.+)$")
TASK_PREFIX_RE = re.compile(r"^Task:\s*", re.IGNORECASE)
IGNORED_DIRS = {".git", ".vscode", "skills", "project-template"}
EMPTY_MARKERS = {"", "none", "暂无", "-", "n/a"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List project-manager workspace tasks in compact markdown tables.")
    parser.add_argument("--project-root", default=".", help="Workspace root containing YYYY-MM-DD-* project directories.")
    parser.add_argument("--format", default="markdown", choices=["markdown"], help="Output format.")
    return parser.parse_args()


def normalize_whitespace(text: str) -> str:
    return " ".join(text.strip().split())


def truncate(text: str, limit: int = 120) -> str:
    text = normalize_whitespace(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return ""


def first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return normalize_whitespace(line[2:])
    return ""


def first_paragraph(markdown: str) -> str:
    in_heading_block = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            in_heading_block = True
            continue
        if in_heading_block and stripped.startswith(("- ", "|", "```")):
            continue
        return normalize_whitespace(stripped)
    return ""


def section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    start = None
    heading_markers = {f"## {heading}", f"### {heading}"}
    for index, line in enumerate(lines):
        if line.strip() in heading_markers:
            start = index + 1
            break
    if start is None:
        return ""
    collected = []
    for line in lines[start:]:
        if line.startswith("## ") or line.startswith("### "):
            break
        collected.append(line)
    return "\n".join(collected).strip()


def clean_task_text(text: str) -> str:
    text = normalize_whitespace(text)
    text = TASK_PREFIX_RE.sub("", text)
    return text


def active_task(active_md: str) -> tuple[str, bool]:
    in_progress = section(active_md, "In Progress")
    for line in in_progress.splitlines():
        match = CHECKBOX_RE.match(line.strip())
        if match and match.group("mark") == " ":
            return clean_task_text(match.group("text")), True
    for line in in_progress.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower() in EMPTY_MARKERS:
            continue
        if stripped.startswith("-"):
            value = stripped.lstrip("- ").strip()
            if value.lower() not in EMPTY_MARKERS:
                return clean_task_text(value), False
    return "", False


def completed_summary(active_md: str) -> str:
    completed = section(active_md, "Recently Completed")
    for line in completed.splitlines():
        match = CHECKBOX_RE.match(line.strip())
        if match and match.group("mark").lower() == "x":
            return clean_task_text(match.group("text"))
        stripped = line.strip()
        if stripped.startswith("-"):
            value = stripped.lstrip("- ").strip()
            if value.lower() not in EMPTY_MARKERS:
                return clean_task_text(value)
    return ""


def next_step(active_md: str) -> str:
    for line in active_md.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("next step:"):
            return normalize_whitespace(stripped.split(":", 1)[1]) or "-"
    return "-"


def blocked(active_md: str) -> bool:
    blocked_text = section(active_md, "Blocked")
    for line in blocked_text.splitlines():
        value = line.strip().lstrip("- ").strip()
        if value.lower() not in EMPTY_MARKERS:
            return True
    return False


def project_dirs(project_root: Path) -> list[Path]:
    dirs = []
    for child in project_root.iterdir():
        if not child.is_dir():
            continue
        if child.name in IGNORED_DIRS:
            continue
        if PROJECT_DIR_RE.match(child.name):
            dirs.append(child)
    return dirs


def parse_project(project_dir: Path) -> dict[str, object]:
    readme = read_text(project_dir / "README.md")
    active_md = read_text(project_dir / "tasks" / "active.md")
    title = first_heading(readme) or project_dir.name
    summary = first_paragraph(readme) or "-"
    task, has_active_checkbox = active_task(active_md)
    done = completed_summary(active_md)
    is_blocked = blocked(active_md)

    if has_active_checkbox:
        status = "进行中"
        current = task
        is_completed = False
    elif is_blocked:
        status = "阻塞"
        current = task or summary
        is_completed = False
    elif done:
        status = "已完成"
        current = done
        is_completed = True
    else:
        status = "已规划"
        current = task or summary
        is_completed = False

    return {
        "project": project_dir.name,
        "title": title,
        "status": status,
        "current": truncate(current or "-"),
        "next_step": truncate(next_step(active_md), 100),
        "is_completed": is_completed,
    }


def sort_key(row: dict[str, object]) -> tuple[str, str]:
    project = str(row["project"])
    match = re.match(r"^(\d{4}-\d{2}-\d{2})-", project)
    date_prefix = match.group(1) if match else ""
    return (date_prefix, project)


def escape_cell(value: object) -> str:
    text = str(value) if value is not None else "-"
    text = text or "-"
    return text.replace("|", "\\|")


def render_table(title: str, rows: list[dict[str, object]]) -> str:
    lines = [
        f"## {title}",
        "",
        "| 项目 | 状态 | 当前任务 | 下一步 |",
        "| --- | --- | --- | --- |",
    ]
    if not rows:
        lines.append("| - | - | - | - |")
        return "\n".join(lines)
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    escape_cell(row["project"]),
                    escape_cell(row["status"]),
                    escape_cell(row["current"]),
                    escape_cell(row["next_step"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        raise SystemExit(f"error: project root does not exist: {project_root}")

    rows = [parse_project(path) for path in project_dirs(project_root)]
    open_rows = [row for row in rows if not row["is_completed"]]
    done_rows = [row for row in rows if row["is_completed"]]
    open_rows.sort(key=sort_key, reverse=True)
    done_rows.sort(key=sort_key, reverse=True)

    print(render_table("未完成任务", open_rows))
    print()
    print(render_table("已完成任务", done_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
