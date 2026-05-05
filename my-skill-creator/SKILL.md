---
name: my-skill-creator
description: Use when the user wants to create or update a Codex skill using the standard skill-creator workflow, but also wants the result kept in the personal my-skills repository. This skill should invoke or follow skill-creator first, then ensure a copy exists under the project `skills/` repository and, when useful, the local Codex skills directory.
---

# My Skill Creator

## Overview

Use this skill as the user's personal wrapper around the system `skill-creator` workflow. The key difference is storage discipline: new or updated skills must be preserved in the personal my-skills repository, not only in `~/.codex/skills`.

## Repository Preference

Use this order unless the user says otherwise:

1. Create or update the canonical copy in the workspace skills repository: `e:\projects\project-manager\skills\<skill-name>\`.
2. Validate the skill there.
3. Sync or mirror it into the local Codex skills directory: `C:\Users\hp\.codex\skills\<skill-name>\`, when the user wants the skill available immediately.

Do not delete local-only skills or unrelated untracked skill directories.

## Workflow

### 1. Invoke Skill Creator

Use the system `skill-creator` skill first:

- Read its `SKILL.md` when needed.
- Follow its naming, frontmatter, validation, and progressive disclosure rules.
- Use `init_skill.py` for new skills whenever practical.
- Keep the generated skill concise and focused.

### 2. Confirm Skill Intent

Before creating or changing files, identify:

- skill name
- purpose
- triggering description
- expected workflow
- whether scripts, references, or assets are actually needed
- whether to sync to local Codex skills immediately

If the user already supplied enough information, proceed without extra questions.

### 3. Create In My-Skills

Create the canonical skill under the workspace `skills/` repository. Prefer:

```powershell
python C:\Users\hp\.codex\skills\.system\skill-creator\scripts\init_skill.py <skill-name> --path e:\projects\project-manager\skills
```

Then edit `SKILL.md` and `agents/openai.yaml` as needed.

### 4. Validate

Run `quick_validate.py` on the repository copy. If the system Python lacks dependencies, use the project virtual environment when available.

```powershell
e:\projects\project-manager\stock-picker\.venv\Scripts\python.exe C:\Users\hp\.codex\skills\.system\skill-creator\scripts\quick_validate.py e:\projects\project-manager\skills\<skill-name>
```

### 5. Sync Local Copy

When immediate local availability is requested, mirror the final repository copy into `C:\Users\hp\.codex\skills\<skill-name>\`.

Preserve the repository copy as canonical. If both copies already exist, compare before overwriting and avoid touching unrelated local skills.

### 6. Report

Finish with:

- repository skill path
- local Codex skill path, if synced
- validation result
- any existing unrelated dirty or untracked skill directories left untouched
