# Sync Rules

Source of truth: `skills/`

## Required behavior

- Sync only project skills that exist under `skills/`.
- Copy only new or changed files into `~/.codex/skills/`.
- Do not delete any local skill directories.
- Do not delete any local files during sync.
- Ignore directories without `SKILL.md`.

## Reporting

- Report `created` when a skill is copied into the local target for the first time.
- Report `updated` when one or more files changed in an existing local skill.
- Report `unchanged` when the local skill already matches the project copy.
- Report `skipped` when the requested skill does not exist in the project source.
