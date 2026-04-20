# Project Task Extraction Rules

Data source: root-level `YYYY-MM-DD-*` project directories in the `project-manager` workspace.

## Required Behavior

- Scan only direct child directories of the project root.
- Include directories matching `YYYY-MM-DD-*`.
- Exclude shared or tooling directories such as `skills/`, `project-template/`, `.git/`, and `.vscode/`.
- Read `README.md` and `tasks/active.md` when present.
- Do not fail if a project is missing optional files; show `-` for unknown fields.
- Split output into unfinished and completed groups.
- Sort groups by date prefix from newest to oldest.

## Status Heuristic

- If `tasks/active.md` contains a checked item under `Recently Completed` and no unchecked active task under `In Progress`, treat as completed.
- If `In Progress` contains `None`, `暂无`, or no unchecked task, treat as no active task.
- If there is an unchecked task under `In Progress`, treat as in progress.
- If `Blocked` contains content other than `None`, `暂无`, or `-`, mark status as blocked only when no active task is found.

## Output Fields

- `项目`: project directory name.
- `状态`: Chinese normalized status.
- `当前任务`: active task text, or summary when completed.
- `下一步`: next step line from `tasks/active.md`, or `-`.
