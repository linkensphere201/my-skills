---
name: create-task
description: Create a new project task directory in the local project-manager workspace from project-template. Use when the user wants to create a new documented project/task under the workspace root using the YYYY-MM-DD-project-name layout, initialize README/context/tasks/prompts/logs docs, and update the root README plus WORKSPACE-STRUCTURE indexes.
---

# Create Task

Create a new project task directory in the local `project-manager` workspace.

This skill is for the workspace shape used by `e:\projects\project-manager`, not the older `atlas-ai-docs/tasks/` layout.

## Inputs

Accept:

- a project/task name such as `ai-log-analyzer`
- an optional one-line description
- an optional current goal or positioning sentence

The generated directory name should be:

- `YYYY-MM-DD-<project-name>/`

## Workflow

1. Read the workspace root `AGENTS.md`, `README.md`, and `WORKSPACE-STRUCTURE.md` when present.
2. Normalize the project name to lowercase hyphen-case.
3. Use the current date as the directory prefix unless the user gives a date.
4. Copy `project-template/` into the new project directory.
5. Initialize the project docs in English unless the user explicitly asks for another language:
   - `README.md`
   - `context/project-overview.md`
   - `context/research-notes.md`
   - `context/architecture.md`
   - `context/glossary.md`
   - `tasks/active.md`
   - `tasks/backlog.md`
   - `tasks/decisions.md`
   - `prompts/reusable-prompts.md`
   - `logs/worklog.md`
6. Update root `README.md` and `WORKSPACE-STRUCTURE.md` with a concise entry for the new project.
7. Report created paths and any assumptions.

## Rules

- Use `project-template/` as the structural source.
- Do not create `atlas-ai-docs/`.
- Do not overwrite an existing project directory.
- Do not treat `skills/` as a normal project folder.
- Keep AI-maintained project documents in English unless the user explicitly asks otherwise.
- Keep root index entries concise.
- Preserve unrelated working tree changes.

## Script

Use `scripts/create_task.py` for deterministic project creation.

Example:

```powershell
python skills\create-task\scripts\create_task.py ai-log-analyzer --description "AI-powered log diagnosis tool"
```

Windows PowerShell wrapper:

```powershell
.\skills\create-task\scripts\create_task.ps1 ai-log-analyzer --description "AI-powered log diagnosis tool"
```

Useful options:

```powershell
python skills\create-task\scripts\create_task.py info-collection-system --project-root .
python skills\create-task\scripts\create_task.py a-share-stock-picker --date 2026-04-20 --description "Medium-to-low-frequency A-share stock selection tool"
```

## Working Style

When you create a task, report:

- the created project directory
- that root indexes were updated
- the main active task that was initialized
- any assumptions used for the description or scope
