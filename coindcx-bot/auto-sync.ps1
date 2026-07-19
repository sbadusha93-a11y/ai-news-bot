$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "$PSScriptRoot"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::DirectoryName

$ignore = @('\.git', 'node_modules', '__pycache__', '.pyc', '.log', '.db', '.zip', '.png', '.yml', 'auto-sync.ps1')

$changed = @{}
$lock = [System.Threading.Mutex]::new()

$action = {
    $path = $Event.SourceEventArgs.FullPath
    foreach ($pattern in $ignore) {
        if ($path -match $pattern) { return }
    }
    $lock.WaitOne() | Out-Null
    $changed[$path] = (Get-Date)
    $lock.ReleaseMutex()
}

$timerAction = {
    $lock.WaitOne() | Out-Null
    $now = Get-Date
    $ready = @($changed.GetEnumerator() | Where-Object { ($now - $_.Value).TotalSeconds -gt 5 })
    if ($ready.Count -gt 0) {
        $changed.Clear()
        $lock.ReleaseMutex()
        Set-Location $using:PSScriptRoot
        git add -A 2>&1 | Out-Null
        $diff = git diff --cached --name-only 2>&1
        if ($diff) {
            git commit -m "auto-sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>&1 | Out-Null
            git push 2>&1 | Out-Null
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Auto-synced $(($diff -split "`n").Count) files to GitHub"
        }
    } else {
        $lock.ReleaseMutex()
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action | Out-Null
Register-ObjectEvent $watcher "Created" -Action $action | Out-Null
Register-ObjectEvent $watcher "Renamed" -Action $action | Out-Null

$timer = New-Object System.Timers.Timer
$timer.Interval = 10000
$timer.AutoReset = $true
Register-ObjectEvent $timer "Elapsed" -Action $timerAction | Out-Null
$timer.Start()

Write-Host "Auto-sync running. Watching for changes in: $PSScriptRoot"
Write-Host "Press Ctrl+C to stop."

while ($true) { Start-Sleep -Seconds 60 }
