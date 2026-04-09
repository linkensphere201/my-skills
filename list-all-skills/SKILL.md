---
name: list-all-skills
description: List project-local skills and locally installed Codex skills, and show which skills exist only in one location. Use when the user asks to list all skills, compare project skills with local Codex skills, or inspect sync status for skills.
---

# List All Skills

List skills from the project `skills/` directory and the local Codex skills directory, then summarize overlap and drift.

## Inputs

Accept an optional project root, source path, or target path.

Default paths:

- project skills source: `skills/`
- local target: `~/.codex/skills/` on Unix-like systems, or the expanded user profile path on Windows

## Workflow

1. Resolve the project root.
2. Read skill directories under the project `skills/` directory.
3. Read skill directories under the local Codex skills directory.
4. Report:
   - project skills
   - local skills
   - shared skills
   - project-only skills
   - local-only skills

## Rules

- Treat only directories containing `SKILL.md` as valid skills.
- Ignore hidden directories.
- Do not modify any files.
- Keep the output compact and easy to scan.

## Script

Use `scripts/list_all_skills.py` for the actual comparison.

Helpful commands:

```bash
python skills/list-all-skills/scripts/list_all_skills.py
python skills/list-all-skills/scripts/list_all_skills.py --project-root .
python skills/list-all-skills/scripts/list_all_skills.py --target ~/.codex/skills
```

## Working Style

Lead with the project and local paths.
Then report counts and grouped skill names.
If one side is empty, state that explicitly.
