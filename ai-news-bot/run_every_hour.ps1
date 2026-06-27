param(
    [int]$IntervalMinutes = 60,
    [string]$Privacy = "public",
    [switch]$Shorts = $true
)

$scriptDir = Split-Path -Parent $PSCommandPath
$logDir = Join-Path $scriptDir "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    Write-Host $line -ForegroundColor Cyan
    Add-Content -Path (Join-Path $logDir "scheduler.log") -Value $line
}

Write-Host "==================================================" -ForegroundColor Green
Write-Host "  AI News Bot - Hourly Upload Scheduler" -ForegroundColor Green
Write-Host "  Every $IntervalMinutes minute(s) | Privacy: $Privacy | Shorts: $Shorts" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop"
Write-Host ""

$runCount = 0

while ($true) {
    $runCount++
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile = Join-Path $logDir "run_${ts}.log"

    Write-Log "=== Run #$runCount ==="

    $argsList = @(
        "ai_news_bot.py", "--upload", "--privacy", $Privacy
    )
    if ($Shorts) {
        $argsList += "--shorts"
    }

    Write-Log "Starting video generation + upload..."

    $output = py -3 $argsList 2>&1
    $output | Out-File -FilePath $logFile -Encoding utf8

    $success = $output -match "SUCCESS"
    if ($success) {
        $url = ($output | Select-String "https://youtu.be/").Line.Trim()
        Write-Log "SUCCESS: $url"
    } else {
        Write-Log "FAILED or no upload. Check logs/run_${ts}.log"
    }

    Write-Log "Next run in $IntervalMinutes minute(s)..."
    Write-Log ""

    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
