$ErrorActionPreference = "Stop"
$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
$env:PYTHONPATH = "$PSScriptRoot;$env:PYTHONPATH"

# Try Python launcher first, then fall back
$py = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "C:\Users\DELL\AppData\Local\Programs\Python\Launcher\py.exe" }
$pyArgs = @("-3.13", "-m", "streamlit", "run", "src/dashboard/app.py", "--server.port", "8501", "--server.headless", "true")

Write-Host "Starting dashboard with: $py $pyArgs"
"n`n" | & $py @pyArgs
