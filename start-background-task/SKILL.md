---
name: start-background-task
description: 通过 tmux 启动和管理后台任务。适用于用户要求“起后台任务”“后台跑”“用 tmux 跑”“长时间执行不要占当前终端”等场景，尤其适合本地长跑测试、压测、构建、数据处理或持续日志采集。
---

# 起后台任务

当用户希望把一个命令放到后台长期运行时，优先使用 `tmux`，不要依赖普通 `nohup`。
在这个工作区里，直接 `nohup ... &` 可能会被当前执行器回收；`tmux` 更稳定。

## 适用场景

- 长时间测试，如 `run_validate_trials.sh 300`
- 长时间构建或批处理任务
- 需要后续 `attach` 查看中间输出的任务
- 需要在后台持续保留的本地服务或脚本

## Workflow

1. 先确定执行目录、命令、日志文件路径、tmux session 名。
2. 优先把输出同时写到日志文件，方便用户后续 `tail -f`。
3. 使用 `tmux new-session -d -s <session>` 启动，不要只给用户一个 `nohup`。
4. 启动后立刻验证：
   - `tmux ls`
   - 必要时 `pgrep -af <关键命令>`
   - `tail` 日志前几行
5. 把下面信息返回给用户：
   - tmux session 名
   - 日志文件路径
   - 查看进度命令
   - attach 命令
   - detach 方法：`Ctrl-b d`

## Command Pattern

通用模板：

```bash
tmux new-session -d -s <session-name> \
  'cd <workdir> && mkdir -p <log-dir> && <command> 2>&1 | tee <log-file>'
```

验证模板：

```bash
tmux ls
tail -n 40 <log-file>
```

## Naming

- `session-name` 要短、稳定、可读，比如：
  - `greenlight300`
  - `atlas-build`
  - `import-job`
- 日志文件建议带时间戳，避免覆盖：
  - `logs/nohup/run-300-tmux-$(date +%Y%m%d-%H%M%S).log`

## Rules

- 默认优先 `tmux`，不要优先选 `nohup`。
- 如果用户明确要求后台执行，启动后一定要做一次存活校验。
- 如果命令需要访问本地 Atlas 服务、端口或受 sandbox 影响，按工作区规则使用提权执行。
- 不要只告诉用户命令而不验证是否真的跑起来。
- 若已存在同名 tmux session，先检查是否是旧任务；不要静默覆盖。

## Output Contract

结果至少包含：

- 后台任务已启动/未启动
- `tmux` session 名
- 日志路径
- `tail -f` 命令
- `tmux attach -t <session>` 命令

示例：

```text
tmux 会话：greenlight300
日志：.../logs/nohup/run-300-tmux-20260424-013528.log

查看进度：
tail -f .../run-300-tmux-20260424-013528.log

进入会话：
tmux attach -t greenlight300

退出 attach 不停任务：
Ctrl-b d
```
