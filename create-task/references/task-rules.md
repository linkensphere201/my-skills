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
- `logs/worklog.md`: chronological work notes.
- `prompts/reusable-prompts.md`: only prompts likely to be reused.

## Index Entry Shape

Root `README.md` should include one concise bullet in the current subdirectory section.

Root `WORKSPACE-STRUCTURE.md` should include one concise row in the ordinary project directories table.

Keep entries short and avoid duplicating full project details in the root files.
