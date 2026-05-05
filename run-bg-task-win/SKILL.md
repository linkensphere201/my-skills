---
name: run-bg-task-win
description: Start and monitor long-running Windows commands in the background with PowerShell Start-Process, stdout/stderr redirection to log files, PID tracking, and periodic status reporting. Use when a user asks Codex to run a long task on Windows without blocking the conversation, wants progress updates from a log file, or needs to resume monitoring an already-started background process.
---

# Run Background Task On Windows

Use this skill for long Windows commands that should keep running while Codex periodically reports progress.

## Workflow

1. Choose a stable run directory inside the relevant project, usually `.tmp/bg-tasks/<task-name>/` or `data/logs/<task-name>/`.
2. Start the command with PowerShell `Start-Process`, redirecting stdout and stderr to files.
3. Save process metadata, including PID, command, working directory, start time, and log paths.
4. Periodically read the log tail and any durable status store the task maintains, then report concise progress to the user.
5. Before starting another copy of the same logical task, check whether a prior PID is still running.

## Preferred Script

Use `scripts/start_bg_task.ps1` when possible. It creates the run directory, writes metadata, starts the command hidden, and returns the PID and log paths.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File skills\run-bg-task-win\scripts\start_bg_task.ps1 `
  -Name market-daily-pull `
  -Command ".\.venv\Scripts\python.exe" `
  -ArgumentList "-m stock_picker.cli provider run-market-daily --config config/storage.yaml --run-id market_daily_1y_split_20260428 --max-tasks 500" `
  -WorkingDirectory "E:\projects\project-manager\stock-picker" `
  -RunDirectory "E:\projects\project-manager\stock-picker\.tmp\bg-tasks"
```

## Monitoring

Use normal shell commands to monitor:

```powershell
Get-Process -Id <pid> -ErrorAction SilentlyContinue
Get-Content <stdout.log> -Tail 40
Get-Content <stderr.log> -Tail 40
```

For commands that persist state in SQLite, Parquet, or another status store, prefer querying that source over relying only on logs.

Report progress with:

- Whether the PID is still running
- Last log lines or a short summary
- Durable progress counters when available
- Any errors from stderr
- The next check interval or next recommended action

## Safety

- Do not use this skill for destructive commands unless the user explicitly confirmed the dangerous action according to workspace rules.
- Do not print secrets. If the command needs credentials, load them into the environment without echoing values.
- Do not start duplicate jobs with the same logical run id if the old process is still active.
- Prefer project-local log directories and avoid writing logs into system locations.
