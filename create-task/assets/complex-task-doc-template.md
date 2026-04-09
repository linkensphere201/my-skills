# Complex Task AI Doc Template

## When to use

- Use this template for a task that is:
  - multi-step
  - likely to span multiple sessions
  - likely to need code reading, review conclusions, implementation notes, and test tracking

## Recommended directory layout

```text
tasks/YYYY-MM-DD-<task-name>/
  README.md
  plan/
    README.md
  findings/
    README.md
    <topic-a>.md
    <topic-b>.md
  implement/
    README.md
  test/
    README.md
    atlas-test.md
    blackbox.md
```

Optional additions:

```text
  environment.md
  usage/
    README.md
```

## Design rules

1. Keep `README.md` short.
   - It is the control page, not the full knowledge base.
2. Split by information type.
   - `plan/` for staged approach, decision options, rollout order, and active next steps
   - `findings/` for conclusions, risks, open issues
   - `implement/` for how the current code works
   - `test/` for coverage, execution, expected results
3. Keep one document focused on one primary purpose.
4. Move detail out early.
   - If a page starts mixing code reading, findings, todo items, and tests, split it.
5. For complex review topics, prefer a stable review lens.
   - A useful default is:
     - `correctness`
     - `compatibility`
     - `background`
     - `performance`
6. When calling out key code, prefer line-numbered references.

## Recommended status model

- `planned`
- `active`
- `active-review`
- `implemented-under-review`
- `blocked`
- `done`

## `README.md` template

```md
# Task: <task title>

## Task summary

- Repository:
- Background:
- Current goal:

## Current task status

- Status:
- Phase:

## Related commits

- Implementation range:
- Hardening or follow-up commits:
- Helper/tool/test commits:
- Baseline or compatibility commits:

## Topic documents

- [findings/README.md](findings/README.md)
  - finding-oriented notes index
- [plan/README.md](plan/README.md)
  - planning-oriented notes index
- [environment.md](environment.md)
  - environment assumptions, repo revisions, binary inputs, and dependency notes
- [implement/README.md](implement/README.md)
  - implementation-oriented notes index
- [test/README.md](test/README.md)
  - test-oriented notes index

## Top findings

1. `P0` <one-line finding>
2. `P0` <one-line finding>
3. `P1` <one-line finding>

## Top todos

1. `P0` <one-line todo>
2. `P0` <one-line todo>
3. `P1` <one-line todo>

## Current checkpoints

- Local verification:
- E2E verification:

## Notes

- Keep this page short.
- Push detail into subdirectories.
```
