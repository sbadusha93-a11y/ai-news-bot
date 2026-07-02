param(
    [switch]$Uninstall
)

$taskName = "CoinDCXBot"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ps1Path = Join-Path $scriptDir "run_dashboard.ps1"
$logDir = Join-Path $scriptDir "logs"
$null = New-Item -ItemType Directory -Path $logDir -Force
$logFile = Join-Path $logDir "service.log"

if ($Uninstall) {
    Write-Host "Stopping and removing scheduled task..."
    Stop-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Scheduled task '$taskName' removed."
    return
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument @"
-NoProfile -WindowStyle Hidden -Command "
`$logFile = '$logFile';
try {
    `$date = Get-Date -Format 'yyyy-MM-dd HH:mm:ss';
    '`$date Starting bot...' | Out-File -FilePath `$logFile -Append;
    Set-Location '$scriptDir';
    `$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = 'false';
    'n' | & 'C:\Users\DELL\AppData\Local\Programs\Python\Launcher\py.exe' -3.13 -m streamlit run src/dashboard/app.py --server.port 8501 --server.headless true 2>&1 | Out-File -FilePath `$logFile -Append;
} catch {
    `$date = Get-Date -Format 'yyyy-MM-dd HH:mm:ss';
    '`$date ERROR: ' + `$_ | Out-File -FilePath `$logFile -Append;
}
"
"@

$trigger = @(
    (New-ScheduledTaskTrigger -AtStartup),
    (New-ScheduledTaskTrigger -Daily -At "06:00" -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365))
)

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 2)

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
    Write-Host "Scheduled task '$taskName' registered successfully."
    Write-Host "Bot will start automatically on Windows boot and every 15 minutes."
    Write-Host ""
    Write-Host "Manual commands:"
    Write-Host "  Start:    Start-ScheduledTask -TaskName '$taskName'"
    Write-Host "  Stop:     Stop-ScheduledTask -TaskName '$taskName'"
    Write-Host "  Status:   Get-ScheduledTask -TaskName '$taskName'"
    Write-Host "  Logs:     Get-Content '$logFile' -Tail 20"
    Write-Host "  Uninstall: .\install-service.ps1 -Uninstall"
} catch {
    Write-Error "Failed to register task: $_"
}
