$botDir = "C:\Users\DELL\Desktop\playwright-demo\coindcx-bot"
$python = "C:\Program Files\python.exe"
$log = "$botDir\logs\bot_autorestart.log"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $log -Value "[$timestamp] Starting bot..."
    
    $process = Start-Process -FilePath $python -ArgumentList "-m src.main --api" -WorkingDirectory $botDir -NoNewWindow -PassThru
    $process.WaitForExit()
    
    $exitCode = $process.ExitCode
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $log -Value "[$timestamp] Bot exited with code $exitCode. Restarting in 5s..."
    Start-Sleep -Seconds 5
}
