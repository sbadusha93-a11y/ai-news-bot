param(
    [int]$MaxRestarts = 5,
    [int]$RestartDelay = 10
)

$ErrorActionPreference = "Continue"
$restartCount = 0
$logFile = Join-Path -Path $PSScriptRoot -ChildPath "logs\bot_launcher.log"
$null = New-Item -ItemType Directory -Path (Split-Path $logFile -Parent) -Force -ErrorAction SilentlyContinue

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp | $Message" | Out-File -FilePath $logFile -Append -Encoding UTF8
    Write-Host "$timestamp | $Message"
}

Write-Log "=== CoinDCX Bot Launcher Started ==="
Write-Log "Max restarts: $MaxRestarts | Restart delay: ${RestartDelay}s"

while ($restartCount -le $MaxRestarts) {
    if ($restartCount -gt 0) {
        Write-Log "Restart #$restartCount after ${RestartDelay}s delay..."
        Start-Sleep -Seconds $RestartDelay
    }
    $restartCount++

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $stdoutLog = Join-Path -Path $PSScriptRoot -ChildPath "logs\bot_stdout_$timestamp.log"
    $stderrLog = Join-Path -Path $PSScriptRoot -ChildPath "logs\bot_stderr_$timestamp.log"

    Write-Log "Starting bot (attempt #$restartCount)..."

    $env:PYTHONPATH = "$PSScriptRoot;$env:PYTHONPATH"
    $process = Start-Process -FilePath "py" -ArgumentList @("-3.13", "-m", "src.main") `
        -WorkingDirectory $PSScriptRoot `
        -NoNewWindow `
        -RedirectStandardOutput $stdoutLog `
        -RedirectStandardError $stderrLog `
        -PassThru

    Write-Log "Bot started with PID $($process.Id)"

    $exitCode = $process.WaitForExit()

    $errorContent = ""
    if (Test-Path $stderrLog) {
        $errorContent = Get-Content $stderrLog -Raw -ErrorAction SilentlyContinue
    }

    $shouldRestart = $true
    $reason = "Unknown exit (code: $exitCode)"

    if ($errorContent -match "getaddrinfo failed|Name or service not known|Connection refused|Connection timed out") {
        $reason = "Network error - will retry"
        $RestartDelay = 15
    } elseif ($errorContent -match "KeyboardInterrupt") {
        $reason = "Manual shutdown"
        $shouldRestart = $false
    } elseif ($errorContent -match "503|502|500") {
        $reason = "API server error - will retry"
    } elseif ($errorContent -match "ModuleNotFoundError|ImportError") {
        $reason = "Missing module - stopping"
        $shouldRestart = $false
    } elseif ($exitCode -eq 0) {
        $reason = "Graceful shutdown"
        $shouldRestart = $false
    } elseif ($errorContent -match "Address already in use|Port already in use") {
        $reason = "Port conflict - stopping"
        $shouldRestart = $false
    }

    if ($shouldRestart) {
        Write-Log "Bot stopped: $reason"
        Write-Log "Restarting in ${RestartDelay}s..."
    } else {
        Write-Log "Bot stopped: $reason - NOT restarting"
        break
    }
}

if ($restartCount -gt $MaxRestarts) {
    Write-Log "FATAL: Max restarts ($MaxRestarts) reached. Giving up."
}
Write-Log "=== CoinDCX Bot Launcher Finished ==="