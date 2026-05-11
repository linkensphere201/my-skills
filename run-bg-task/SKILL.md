---
name: run-bg-task
description: Start and monitor long-running Linux commands in the background with Python, stdout/stderr log files, PID tracking, and periodic status reporting. Use when a user asks Codex to run a long task without blocking the conversation, wants progress updates from a log file, or needs to resume monitoring an already-started background process.
---

# Run Background Task

Use this skill for long Linux commands that should keep running while Codex periodically reports progress.

## Workflow

1. Choose a stable run directory inside the relevant project, usually `.tmp/bg-tasks/<task-name>/` or `data/logs/<task-name>/`.
2. Start the command with `scripts/start_bg_task.py`, redirecting stdout and stderr to files.
3. Save process metadata, including runner PID, child PID path, command, working directory, start time, and log paths.
4. Periodically read the log tail and any durable status store the task maintains, then report concise progress to the user.
5. Before starting another copy of the same logical task, check whether a prior PID is still running.
6. To stop a task, use recorded metadata rather than guessing by process start time.

## Preferred Script

Use `scripts/start_bg_task.py` when possible. It creates the run directory, writes metadata, starts the command detached, and returns the runner PID, child PID path, runtime status path, and log paths.

Example:

```bash
python3 skills/run-bg-task/scripts/start_bg_task.py \
  --name market-daily-pull \
  --working-directory /dev-app-01/dev/project-manager/stock-picker \
  --run-directory .tmp/bg-tasks \
  -- python3 -m stock_picker.cli provider run-market-daily --config config/storage.yaml --run-id market_daily_1y_split_20260428 --max-tasks 500
```

The command to run must appear after `--`. Pass the executable and each argument as separate shell words so Python can track the process directly.

## Monitoring

Use normal shell commands to monitor:

```bash
ps -p <pid>
cat <child-pid.txt>
cat <runtime-status.json>
tail -n 40 <stdout.log>
tail -n 40 <stderr.log>
```

For commands that persist state in SQLite, Parquet, or another status store, prefer querying that source over relying only on logs.

Report progress with:

- Whether the PID is still running
- The child PID when `child-pid.txt` has been written
- Last log lines or a short summary
- Durable progress counters when available
- Any errors from stderr
- The next check interval or next recommended action

## Stopping

Use `scripts/stop_bg_task.py` with the recorded `metadata.json` path. It reads the child PID from `child-pid.txt`, stops the child first, then stops the runner PID.

```bash
python3 skills/run-bg-task/scripts/stop_bg_task.py \
  --metadata /dev-app-01/dev/project-manager/stock-picker/.tmp/bg-tasks/<task>/metadata.json
```

If `child-pid.txt` is not written yet, wait briefly and read `runtime-status.json` before deciding whether to stop only the runner.

## Safety

- Do not use this skill for destructive commands unless the user explicitly confirmed the dangerous action according to workspace rules.
- Do not print secrets. If the command needs credentials, load them into the environment without echoing values.
- Do not start duplicate jobs with the same logical run id if the old process is still active.
- Do not guess child processes by start time when metadata is available.
- Prefer project-local log directories and avoid writing logs into system locations.
