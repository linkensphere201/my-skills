# Task Document Rules

Source of truth:

- `AGENTS.md`
- `atlas-ai-docs/tasks.md`

## Required behavior

- Create new large-task docs under `atlas-ai-docs/tasks/YYYY-MM-DD-<task-name>/`.
- Create new task docs under `atlas-ai-docs/tasks/YYYY-MM-DD-<task-name>/` for every task, regardless of size.
- Use `README.md` as the main control page.
- Keep `atlas-ai-docs/tasks.md` as a concise index only.
- Do not overwrite an existing task directory.

## Recommended layout

- `README.md`
- `findings/README.md`
- `plan/README.md`
- `implement/README.md`
- `test/README.md`
- `test/atlas-test.md`
- `test/blackbox.md`
- `environment.md`

## Topic sub-document structure

- Use this section order for topic-specific sub-documents:
  - `# Task: <main-task> / <topic>`
  - `## Scope`
  - `## Current conclusion`
  - `## Findings`
  - `## Open questions`
  - `## Todo / Next steps`
  - `## References`

## Section expectations

- `Scope`
  - define what is in scope and out of scope for the topic
- `Current conclusion`
  - summarize confirmed conclusions, unresolved points, and whether code changes are needed now
- `Findings`
  - use numbered findings
  - each finding should preferably include:
    - `Summary`
    - `Severity`
    - `Evidence`
    - `Impact`
    - `Current conclusion`
    - `Follow-up`
- `Open questions`
  - list unresolved design or verification questions
- `Todo / Next steps`
  - list topic-local next steps, preferably with priorities such as `P0` or `P1`
- `References`
  - include relevant commits, files, tests, and related notes or Jira references when available

## Index entry shape

- task link
- `Status`
- `Summary`

Keep the index entry brief.
