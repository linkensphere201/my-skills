param(
    [Parameter(Mandatory = $true)]
    [string]$TargetPath
)

if (-not (Test-Path $TargetPath)) {
    New-Item -ItemType Directory -Path $TargetPath | Out-Null
}

$dirs = @(
    "context",
    "tasks",
    "prompts",
    "logs"
)

foreach ($dir in $dirs) {
    $full = Join-Path $TargetPath $dir
    if (-not (Test-Path $full)) {
        New-Item -ItemType Directory -Path $full | Out-Null
    }
}

Write-Output "Initialized exploratory project structure at $TargetPath"
