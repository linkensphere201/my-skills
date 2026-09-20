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
  worklog.md
  environment.md
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
7. For non-trivial design or optimization work, use a two-level design flow.
   - First freeze the architecture-level direction, boundaries, rollout phases, fallback strategy, and validation target.
   - Before implementing each item, perform a code-level design review against the current code.
   - The code-level review may refine, split, downgrade, replace, or overturn the earlier design when code evidence shows that is necessary.
   - Record the code-level review conclusion in the task DOC before coding.

8. Give every formal design point or decision option a stable task-local ID such as `D-001` when it enters the task document, including `proposed` items.
   - Keep a compact registry in `plan/README.md` or the primary design document.
   - Never renumber or reuse an ID.
   - Mark replaced decisions `superseded` and link the replacement instead of silently rewriting history.
9. Keep a tiered task history in `worklog.md` using stable IDs such as `W-001`.
   - Log architecture, protocol, lifecycle, persistence, compatibility, public API, safety/correctness, and major milestone changes individually.
   - Merge naming, formatting, error-message, small-refactor, and related test changes into one checkpoint entry when they serve the same objective.
   - Do not create a file-by-file activity stream.

## Code-level design review gate

Before implementing a non-trivial design item, add or update a section under `plan/` or `implement/` that records:

- Code entrypoints inspected
- Existing implementation shape
- Confirmed reuse points
- Rejected assumptions
- Final implementation boundary
- Test impact

Implementation should start only after this review conclusion is recorded.

## Decision status model

- `proposed`
- `confirmed`
- `superseded`
- `rejected`

## Worklog entry fields

- Date
- Importance: `material` or `checkpoint`
- Summary
- Scope or impact
- Related decisions
- Related commits, when available
- Verification

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
- [worklog.md](worklog.md)
  - stable material changes and grouped implementation checkpoints

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
