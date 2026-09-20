---
name: create-task
description: Create a new Atlas AI task document scaffold under atlas-ai-docs/tasks using the workspace task layout rules. Use when the user wants to create a new task from a task name plus an optional task description, initialize a task README plus subdirectories, or start a large multi-step task with the standard template.
---

# Create Task

Create a new task document directory under `atlas-ai-docs/tasks/` using the standard project layout.
Keep the old shared template file untouched; this skill carries its own template copy for future reuse.

## Inputs

Accept:

- a task name such as `investigate-foo`
- an optional task description

The generated directory name should be:

- `atlas-ai-docs/tasks/YYYY-MM-DD-<task-name>/`

## Workflow

1. Normalize the task name to lowercase hyphen-case.
2. Use the current date as the task directory prefix.
3. Create the standard directory layout for every task, regardless of size:
   - `README.md`
   - `findings/README.md`
   - `plan/README.md`
   - `implement/README.md`
   - `test/README.md`
   - `test/atlas-test.md`
   - `test/blackbox.md`
   - `environment.md`
   - `worklog.md`
4. Fill the files using the bundled task template structure.
5. Append a concise entry to `atlas-ai-docs/tasks.md`.

## Rules

- Use the task directory under `atlas-ai-docs/tasks/` as the canonical location.
- Always create a dedicated task directory, even for small tasks.
- Use `README.md` as the main control page.
- Keep `tasks.md` concise when updating the index.
- Do not overwrite an existing task directory.
- Match the bundled template layout rather than creating a reduced scaffold.
- Initialize a decision registry in `plan/README.md`. Every formal design point or decision option receives a stable task-local ID such as `D-001` when it enters the task document, including `proposed` items; never renumber or reuse IDs. Mark replaced decisions `superseded` and link the replacement.
- Initialize `worklog.md`. Material architecture, protocol, lifecycle, persistence, compatibility, public API, safety/correctness, and milestone changes receive individual `W-NNN` entries.
- Merge minor related edits into one checkpoint worklog entry when they serve the same objective; do not log each file edit separately.
- Each worklog entry records date, importance, summary, scope or impact, related decisions, related commits when available, and verification status.

## Template Source

Use `assets/complex-task-doc-template.md` as the bundled template reference.
Use `scripts/create_task.py` for deterministic scaffold creation.

## Working Style

When you create a task, report:

- the created task path
- that `tasks.md` was updated
- any assumptions used for the task description
