---
name: list-all-tasks
description: List all documented project-manager workspace tasks in compact Chinese tables by scanning YYYY-MM-DD-* project directories. Use when the user asks to show current tasks, list local projects, summarize project status, or review active/completed work in the project-manager workspace.
---

# List All Tasks

List project/task status for the local `project-manager` workspace.

This skill scans root-level `YYYY-MM-DD-*` project directories. It does not read the older `atlas-ai-docs/tasks.md` index.

## Inputs

Accept optional values:

- project root path
- output format, currently `markdown`
- include/exclude completed-only grouping behavior through script options if added later

Default project root:

- current working directory

## Workflow

1. Scan direct child directories whose names match `YYYY-MM-DD-*`.
2. Ignore non-project directories such as `.git`, `.vscode`, `skills`, and `project-template`.
3. For each project directory, read:
   - `README.md`
   - `tasks/active.md`
4. Extract:
   - project directory name
   - project title
   - current status
   - current active task
   - next step
   - short summary
5. Split output into unfinished and completed project tables.
6. Sort both tables by project directory date from newest to oldest.
7. Output concise Chinese markdown tables for conversation use.

## Output Contract

Use two compact tables in this order:

1. `未完成任务`
2. `已完成任务`

Columns:

- `项目`
- `状态`
- `当前任务`
- `下一步`

## Rules

- Keep project directory names unchanged.
- Use Chinese status labels in output.
- Treat a project as completed only when `tasks/active.md` has no active checkbox task and the completed section contains completed items.
- If a field is missing, output `-` rather than failing.
- Do not modify any project files.

## Script

Use `scripts/list_all_tasks.py`.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File skills\list-all-tasks\scripts\list_all_tasks.ps1 --project-root .
```

Python directly:

```powershell
python skills\list-all-tasks\scripts\list_all_tasks.py --project-root .
```
