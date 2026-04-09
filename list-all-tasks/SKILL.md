---
name: list-all-tasks
description: 用中文列出所有已记录任务，并分成未完成和已完成两个紧凑表格展示状态和任务简述。适用于用户要求列出当前任务、查看任务进展概览、或汇总 atlas-ai-docs 任务状态时。
---

# 列出所有任务

从 `atlas-ai-docs/tasks.md` 读取已登记任务，并输出中文紧凑状态表。
结果分成“未完成任务”和“已完成任务”两个表格，只展示任务、状态和任务简述。
任务名保持原始的日期加英文 task 格式，不要翻译任务名本身，也不要用 alias 替代任务目录名。

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
3. 将 `Summary` 从原始文档语言直接翻译成自然中文。
4. 按任务目录名前缀日期从新到旧排序。
5. 先输出未完成任务表，再输出已完成任务表。

## Output Contract

使用两张紧凑表格，顺序为：

1. `未完成任务`
2. `已完成任务`

每张表的列为：

- `任务`
- `状态`
- `任务简述`

`状态` 优先显示中文归一化结果。
`任务简述` 使用读取到的原始 DOC 内容现场翻译成中文，不要依赖预置映射表。

## Rules

- 将 `completed` 和 `done` 视为已完成任务。
- 未完成任务只能出现在第一张表。
- 已完成任务只能出现在第二张表。
- 两张表内部都按任务日期从新到旧排序。
- 不要为任务摘要维护硬编码翻译字典。
- 直接根据当前 DOC 文本内容翻译，避免脚本内翻译映射与 DOC 漂移。
- 单元格内容尽量简短，优先单行展示。

## Script

使用 `scripts/list_all_tasks.py` 完成解析与表格输出。

常用命令：

```bash
python3 skills/list-all-tasks/scripts/list_all_tasks.py
python3 skills/list-all-tasks/scripts/list_all_tasks.py --project-root .
python3 skills/list-all-tasks/scripts/list_all_tasks.py --format markdown
```
