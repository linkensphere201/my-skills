# Project Skills

## Scope

- This directory stores project-level skill sources that belong to this workspace.
- These skills are versioned with the repository so the team can review and evolve them together.

## Loading model

- Treat this directory as the source-of-truth for project skills.
- User-level Codex skill discovery may still require installation or sync into `~/.codex/skills/`.
- Keep the project copy and any installed copy aligned when the skill changes.

## Available skills

- [task-summary-table/SKILL.md](task-summary-table/SKILL.md)
  - generate the standard `任务总表 <task-name>` output from Atlas AI task documents
- [sync-project-skills/SKILL.md](sync-project-skills/SKILL.md)
  - sync new or changed project skills into `~/.codex/skills/` without deleting local-only skills
- [list-all-skills/SKILL.md](list-all-skills/SKILL.md)
  - list project-local skills and local Codex skills, then show shared, project-only, and local-only skills
- [list-all-tasks/SKILL.md](list-all-tasks/SKILL.md)
  - list all documented tasks with status, summary, and unfinished items in one compact table

## Recommended structure

```text
skills/<skill-name>/
  SKILL.md
  agents/
    openai.yaml
  references/
    <reference>.md
```

Add `scripts/` or `assets/` only when the skill really needs them.
