# Project Task Rules

Source of truth:

- root `AGENTS.md`
- root `README.md`
- root `WORKSPACE-STRUCTURE.md`
- `project-template/`

## Required Behavior

- Create new project/task directories at the workspace root.
- Use the directory name shape `YYYY-MM-DD-<project-name>/`.
- Start from `project-template/`.
- Keep each project self-contained.
- Classify each project as simple or complex in `tasks/milestones.md`.
- For complex projects, define the complete known `M1` through `Mn` sequence before implementation begins.
- Use immutable hierarchical task IDs and reference them in all progress records.
- Update root `README.md` and `WORKSPACE-STRUCTURE.md`.
- Keep AI-maintained project documents in English unless the user explicitly asks for another language.

## Expected Project Layout

```text
YYYY-MM-DD-project-name/
  AGENTS.md
  README.md
  context/
    architecture.md
    glossary.md
    project-overview.md
    research-notes.md
  tasks/
    active.md
    backlog.md
    decisions.md
    milestones.md
  prompts/
    reusable-prompts.md
  logs/
    worklog.md
```

## Document Expectations

- `README.md`: concise product/task positioning, current goals, scope, non-goals, directory guide.
- `context/project-overview.md`: background, goals, non-goals, key questions.
- `context/research-notes.md`: early observations, candidate sources or approaches, open questions.
- `context/architecture.md`: initial system or workflow concept.
- `context/glossary.md`: terms that future collaborators should read consistently.
- `tasks/active.md`: one active task with owner and next step.
- `tasks/backlog.md`: prioritized follow-up tasks.
- `tasks/decisions.md`: decision log with date, reason, and impact.
- `tasks/milestones.md`: complexity classification, milestone register, acceptance targets, and hierarchical decomposition.
- `logs/worklog.md`: chronological work notes.
- `prompts/reusable-prompts.md`: only prompts likely to be reused.

## Index Entry Shape

Root `README.md` should include one concise bullet in the current subdirectory section.

Root `WORKSPACE-STRUCTURE.md` should include one concise row in the ordinary project directories table.

Keep entries short and avoid duplicating full project details in the root files.

## Numbering And Progress Index

- Milestone: `M1`, `M2`, ..., `Mn`.
- Subgoal/work package: `M1.1`, `M1.2`, ... .
- Executable task: `M1.1.1`, `M1.1.2`, ... .
- Optional final decomposition: `M1.1.1.1` only when necessary.
- Assign numbers sequentially within the parent ID.
- Never renumber or reuse IDs once implementation or progress reporting begins.
- Retain cancelled and superseded IDs with their terminal status.
- Every active-status, decision, implementation, test, and work-log record must cite at least one applicable ID.

## Complex-Task Planning Gate

Before implementation, a complex task must have:

1. Complexity set to `Complex`.
2. The complete known milestone sequence `M1` through `Mn`.
3. A goal and acceptance target for each milestone.
4. Numbered subgoals for the current milestone.
5. Numbered executable tasks for the active subgoal.
6. Recorded dependencies, unresolved decisions, and stop conditions.
