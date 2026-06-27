$taskName = "CoinDCXBot"
$botDir = "C:\Users\DELL\Desktop\playwright-demo\coindcx-bot"
$pyPath = "C:\Program Files\python.exe"

$action = New-ScheduledTaskAction -Execute $pyPath -Argument "coindcx_bot.py" -WorkingDirectory $botDir
$trigger = New-ScheduledTaskTrigger -AtStartup -RandomDelay (New-TimeSpan -Minutes 1)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -RunLevel Highest -LogonType S4U

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force
Write-Host "Task '$taskName' created successfully!"
