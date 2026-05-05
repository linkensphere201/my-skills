param(
    [Parameter(Mandatory = $true)]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [string]$Command,

    [string]$ArgumentList = "",

    [Parameter(Mandatory = $true)]
    [string]$WorkingDirectory,

    [string]$RunDirectory = ".tmp\bg-tasks"
)

$ErrorActionPreference = "Stop"

$resolvedWorkingDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
if ([System.IO.Path]::IsPathRooted($RunDirectory)) {
    $rootRunDirectory = $RunDirectory
} else {
    $rootRunDirectory = Join-Path $resolvedWorkingDirectory $RunDirectory
}

$safeName = $Name -replace '[^A-Za-z0-9_.-]', '-'
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$taskDirectory = Join-Path $rootRunDirectory "$timestamp-$safeName"
New-Item -ItemType Directory -Force -Path $taskDirectory | Out-Null

$stdoutPath = Join-Path $taskDirectory "stdout.log"
$stderrPath = Join-Path $taskDirectory "stderr.log"
$metadataPath = Join-Path $taskDirectory "metadata.json"
$runnerConfigPath = Join-Path $taskDirectory "runner-config.json"
$runnerPath = Join-Path $taskDirectory "runner.ps1"
$exitCodePath = Join-Path $taskDirectory "exit-code.txt"

$runnerConfig = [ordered]@{
    command = $Command
    argument_list = $ArgumentList
    working_directory = $resolvedWorkingDirectory
    stdout_log = $stdoutPath
    stderr_log = $stderrPath
    exit_code_path = $exitCodePath
}
$runnerConfig | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $runnerConfigPath -Encoding UTF8

@'
$ErrorActionPreference = "Stop"
$configPath = Join-Path $PSScriptRoot "runner-config.json"
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
try {
    $child = Start-Process `
        -FilePath $config.command `
        -ArgumentList $config.argument_list `
        -WorkingDirectory $config.working_directory `
        -RedirectStandardOutput $config.stdout_log `
        -RedirectStandardError $config.stderr_log `
        -PassThru `
        -Wait
    Set-Content -LiteralPath $config.exit_code_path -Value $child.ExitCode -Encoding UTF8
    exit $child.ExitCode
} catch {
    $_ | Out-String | Set-Content -LiteralPath $config.stderr_log -Encoding UTF8
    Set-Content -LiteralPath $config.exit_code_path -Value 1 -Encoding UTF8
    exit 1
}
'@ | Set-Content -LiteralPath $runnerPath -Encoding UTF8

$runnerArguments = "-NoProfile -ExecutionPolicy Bypass -File `"$runnerPath`""
$process = Start-Process `
    -FilePath "powershell" `
    -ArgumentList $runnerArguments `
    -WorkingDirectory $resolvedWorkingDirectory `
    -WindowStyle Hidden `
    -PassThru

$metadata = [ordered]@{
    name = $Name
    pid = $process.Id
    pid_type = "runner"
    command = $Command
    argument_list = $ArgumentList
    working_directory = $resolvedWorkingDirectory
    task_directory = $taskDirectory
    stdout_log = $stdoutPath
    stderr_log = $stderrPath
    runner_config = $runnerConfigPath
    runner_script = $runnerPath
    exit_code = $exitCodePath
    started_at = (Get-Date).ToString("o")
}

$metadata | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $metadataPath -Encoding UTF8

[ordered]@{
    pid = $process.Id
    task_directory = $taskDirectory
    stdout_log = $stdoutPath
    stderr_log = $stderrPath
    metadata = $metadataPath
    exit_code = $exitCodePath
} | ConvertTo-Json -Depth 4
