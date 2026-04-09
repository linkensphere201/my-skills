# Atlas Task Summary Rule

Source of truth: `atlas-ai-docs/decisions.md`

Standard operation: `任务总表 <task-name>`

Required behavior:

- Generate one unified table-style status summary for a task.
- Cover all currently known findings, follow-ups, todos, and completed items.
- Read from the matching task `README.md` and sibling topic documents such as `findings/`, `plan/`, `implement/`, and `test/`.

Required sections:

1. `Findings 总表`
2. `Follow-ups / Todos 总表`
3. `已完成事项`
4. `当前 active 线`

Required columns:

- `编号`
- `主题`
- `优先级`
- `当前状态`
- `摘要/说明`

Status normalization:

- `active`
- `done`
- `open`
- `deferred`
- `unknown`

Merge rule:

- Merge duplicate items across documents into one row.

Drift rule:

- If code reality and DOC appear inconsistent, mention the drift before presenting the summary.
