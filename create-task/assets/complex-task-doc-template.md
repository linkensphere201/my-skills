# Project Task Doc Template

Use this asset as a content reference for project-manager task directories.

## Directory Layout

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

## README.md Shape

```md
# <Project Title>

This project is for <one-line purpose>.

## Current Goals

- <goal>

## Initial Scope

- <scope>

## Non-Goals

- <non-goal>

## Directory Guide

- `context/`: project background, system assumptions, glossary, architecture, and research notes.
- `tasks/`: active work, backlog items, and key decisions.
- `prompts/`: reusable prompts.
- `logs/`: chronological project work notes.
```

## active.md Shape

```md
# Active Tasks

## In Progress

- [ ] Task: <active task>
  Owner: hp + Codex
  Next step: <next step>

## Blocked

- None

## Recently Completed

- [x] Initialized the <project> project directory
```

## decisions.md Shape

```md
# Decisions

## Decision Log

### YYYY-MM-DD

- Decision: Manage <project> as a separate project.
- Reason: <why this needs its own directory>
- Impact: Related materials will be maintained under `<directory>/`.
```
