---
name: create-task
description: Create a numbered project task directory in the local project-manager workspace from project-template. Use when the user wants a new documented project/task with YYYY-MM-DD naming, strict M1-to-Mn milestone planning for complex work, hierarchical task IDs, initialized README/context/tasks/prompts/logs docs, and updated workspace indexes.
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
4. Classify the work as simple or complex from its scope, dependencies, duration, and number of independently acceptable deliveries.
5. For complex work, discuss and define the complete known milestone sequence `M1` through `Mn` before implementation begins.
6. Copy `project-template/` into the new project directory.
7. Initialize the project docs in English unless the user explicitly asks for another language:
   - `README.md`
   - `context/project-overview.md`
   - `context/research-notes.md`
   - `context/architecture.md`
   - `context/glossary.md`
   - `tasks/active.md`
   - `tasks/backlog.md`
   - `tasks/decisions.md`
   - `tasks/milestones.md`
   - `prompts/reusable-prompts.md`
   - `logs/worklog.md`
8. Use strict hierarchical IDs in milestone and task documents.
9. Update root `README.md` and `WORKSPACE-STRUCTURE.md` with a concise entry for the new project.
10. Report created paths, complexity classification, milestone planning status, and assumptions.

## Numbering Contract

- Use `M<n>` for milestones.
- Use `M<n>.<s>` for stable subgoals or work packages.
- Use `M<n>.<s>.<t>` for executable tasks.
- Add a fourth numeric level only when an executable task requires further decomposition.
- Assign IDs sequentially within their parent.
- Never renumber or reuse an ID after implementation or progress reporting begins.
- Keep cancelled or superseded IDs and mark their final state.
- Require active status, backlog, decisions, implementation notes, tests, and work-log entries to reference the most specific applicable ID.

## Complex-Task Gate

Do not start implementation for a complex task until:

- `tasks/milestones.md` classifies the project as complex;
- the known `M1` through `Mn` sequence is defined;
- every milestone has a goal and acceptance target;
- the current milestone is decomposed into numbered subgoals and executable tasks;
- dependencies and open decisions that block implementation are recorded.

## Rules

- Use `project-template/` as the structural source.
- Do not create `atlas-ai-docs/`.
- Do not overwrite an existing project directory.
- Do not treat `skills/` as a normal project folder.
- Keep AI-maintained project documents in English unless the user explicitly asks otherwise.
- Treat milestone and task IDs as stable cross-document indexes.
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
- the initial milestone/task IDs and whether the complex-task gate is approved
- any assumptions used for the description or scope
