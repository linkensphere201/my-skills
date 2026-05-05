param(
    [Parameter(Mandatory = $true)]
    [string]$MetadataPath
)

$ErrorActionPreference = "Stop"

$resolvedMetadataPath = (Resolve-Path -LiteralPath $MetadataPath).Path
$metadata = Get-Content -LiteralPath $resolvedMetadataPath -Raw | ConvertFrom-Json

function Stop-TrackedProcess {
    param(
        [Parameter(Mandatory = $true)]
        [int]$ProcessId,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return [ordered]@{
            label = $Label
            pid = $ProcessId
            action = "already_exited"
        }
    }

    Stop-Process -Id $ProcessId -Force
    return [ordered]@{
        label = $Label
        pid = $ProcessId
        action = "stopped"
    }
}

$results = @()

$childPidPath = $metadata.child_pid
if ($childPidPath -and (Test-Path -LiteralPath $childPidPath)) {
    $childPidText = (Get-Content -LiteralPath $childPidPath -Raw).Trim()
    if ($childPidText -match '^\d+$') {
        $results += Stop-TrackedProcess -ProcessId ([int]$childPidText) -Label "child"
    }
} else {
    $results += [ordered]@{
        label = "child"
        pid = $null
        action = "pid_not_recorded"
    }
}

if ($metadata.pid) {
    $results += Stop-TrackedProcess -ProcessId ([int]$metadata.pid) -Label "runner"
}

$stopStatusPath = Join-Path $metadata.task_directory "stop-status.json"
[ordered]@{
    metadata = $resolvedMetadataPath
    stopped_at = (Get-Date).ToString("o")
    results = $results
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $stopStatusPath -Encoding UTF8

Get-Content -LiteralPath $stopStatusPath -Raw
