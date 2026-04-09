---
name: sync-project-skills
description: Sync project-local skills into the user's ~/.codex/skills directory without deleting local-only skills. Use when the user asks to sync skills from the root skills directory, install updated project skills locally, or keep local Codex skills aligned with this repository.
---

# Sync Project Skills

Sync new or changed skills from `skills/` into the user's Codex skills directory.
Never delete local skills or extra local files during sync.

## Inputs

Accept an optional project root, source path, or one or more skill names.

Default paths:

- project skills source: `skills/`
- local target: `~/.codex/skills/` on Unix-like systems, or the expanded user profile path on Windows

## Workflow

1. Resolve the project root.
2. Read the project skill source directory.
3. Select all project skills or the named subset.
4. Copy only new or changed files into the local Codex skills directory.
5. Preserve any local-only skills and any extra local files.

## Rules

- Treat the project copy under `skills/` as the source of truth.
- Sync only directories that contain `SKILL.md`.
- Do not delete target skill directories that are absent from the project.
- Do not delete target files that are absent from the project.
- Report which skills were created, updated, unchanged, or skipped.

## Script

Use `scripts/sync_project_skills.py` for the actual file sync.

Helpful commands:

```bash
python skills/sync-project-skills/scripts/sync_project_skills.py --dry-run
python skills/sync-project-skills/scripts/sync_project_skills.py
python skills/sync-project-skills/scripts/sync_project_skills.py task-summary-table
```

## Working Style

Keep the response concise.
State the source path, target path, and whether the run was a dry-run.
If nothing changed, say that explicitly.
