---
name: task-summary-table
description: Generate a unified table-style status summary for one documented task. Use when the user asks for `任务总表 task-name`, asks to summarize a task into findings/follow-ups/completed/active tables, or needs one merged status view from `atlas-ai-docs/tasks/...` documents.
---

# Task Summary Table

Generate a single normalized status summary for one task from the Atlas AI documentation area.
Prefer the task directory under `atlas-ai-docs/tasks/YYYY-MM-DD-<task-name>/` and merge information across the task `README.md` plus sibling topic docs.

## Inputs

Accept one task name, alias, or task path.

Resolve the target in this order:

1. Match an exact task directory name under `atlas-ai-docs/tasks/`.
2. Match an alias or task-name fragment from `atlas-ai-docs/tasks.md`.
3. If the user gave a path, use that path directly.

If multiple candidates match, stop and ask the user which task they want.

## Default Sources

Read the minimum set of files needed:

- task `README.md`
- `findings/`
- `plan/`
- `implement/`
- `test/`
- other sibling docs only if they clearly affect status

Also check `atlas-ai-docs/tasks.md` when it helps map a short task name to a concrete task directory.

## Output Contract

Always produce these sections in this order:

1. `Findings 总表`
2. `Follow-ups / Todos 总表`
3. `已完成事项`
4. `当前 active 线`

Use a table for each section with these columns:

- `编号`
- `主题`
- `优先级`
- `当前状态`
- `摘要/说明`

If one section has no items, keep the section and state that no items are currently documented.

## Normalization Rules

Normalize item state into one of:

- `active`
- `done`
- `open`
- `deferred`
- `unknown`

Do not preserve every source wording literally when the intent is clear.
If the same item appears in multiple docs, merge it into one row instead of duplicating it.

## Drift Handling

If code reality and DOC appear inconsistent, mention the drift before the tables.
Keep the drift note short and concrete.

## Extraction Heuristics

Treat these as likely signals:

- `finding`, `risk`, `issue`, `problem`, `bug`, `review`
- `todo`, `follow-up`, `next`, `open`, `pending`
- `done`, `completed`, `landed`, `implemented`, `verified`
- `active`, `in progress`, `current line`, `ongoing`

Prefer the most recent or most specific wording when merging duplicate items.
When priority is not explicit, infer conservatively as `unknown`.

## Atlas-Specific Notes

The canonical rule for this operation is recorded in `atlas-ai-docs/decisions.md` under `Standard operation: 任务总表 <task-name>`.
Follow that rule when workspace documents disagree on presentation.

## Working Style

Keep the response compact and scan-friendly.
Lead with the tables, not a long narrative.
If source coverage is thin, say so briefly after the tables.
