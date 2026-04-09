---
name: list-all-tasks
description: 用中文列出所有已记录任务，并以紧凑表格展示完成状态、任务简述和未完成项。适用于用户要求列出当前任务、查看任务进展概览、或汇总 atlas-ai-docs 任务状态时。
---

# 列出所有任务

从 `atlas-ai-docs/tasks.md` 读取已登记任务，并输出中文紧凑状态表。
表格展示每个任务是否完成、任务简述，以及未完成任务的主要待办项。

## Inputs

接受可选的项目根目录、任务索引路径或输出格式。

默认数据源：

- task index: `atlas-ai-docs/tasks.md`
- task details: `atlas-ai-docs/tasks/<task-name>/README.md`

## Workflow

1. 读取 `atlas-ai-docs/tasks.md`。
2. 提取每个任务条目的：
   - 任务名
   - 状态
   - 简述
   - 可选别名
3. 对未完成任务，读取对应的任务 `README.md`。
4. 按顺序提取主要未完成项：
   - `## Top todos`
   - 否则 `## Next action`
   - 否则标记为 `未知`
5. 输出紧凑小表格。

## Output Contract

使用一张紧凑表格，列为：

- `任务`
- `状态`
- `是否完成`
- `任务简述`
- `未完成项`

`状态` 优先显示中文归一化结果。
`是否完成` 统一为 `是` 或 `否`。

## Rules

- 将 `completed` 和 `done` 视为已完成任务。
- 已完成任务的 `未完成项` 显示为 `-`。
- 优先取 `Top todos` 的第一项作为未完成项摘要。
- 若没有 todo，则回退到 `Next action`。
- 单元格内容尽量简短，优先单行展示。

## Script

使用 `scripts/list_all_tasks.py` 完成解析与表格输出。

常用命令：

```bash
python3 skills/list-all-tasks/scripts/list_all_tasks.py
python3 skills/list-all-tasks/scripts/list_all_tasks.py --project-root .
python3 skills/list-all-tasks/scripts/list_all_tasks.py --format markdown
```
