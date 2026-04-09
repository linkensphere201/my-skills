# 任务提取规则

数据源：`atlas-ai-docs/tasks.md`

## 必需行为

- 从 `atlas-ai-docs/tasks.md` 读取任务索引。
- 每个链接任务条目对应一行任务。
- 仅在需要提取未完成项时再读取对应任务 `README.md`。
- 保留索引中的 `Summary` 作为任务主简述。
- 将完成状态统一成 `是` 或 `否`。

## 未完成项优先级

1. First entry under `## Top todos`
2. Content under `## Next action`
3. `未知`

## 已完成任务

- 如果状态是 `completed` 或 `done`，则输出 `是否完成 = 是`。
- `未完成项` 显示为 `-`。
