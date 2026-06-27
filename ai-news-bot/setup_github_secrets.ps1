Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AI News Bot - GitHub Secrets Setup" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$botDir = Split-Path -Parent $PSCommandPath
$envPath = Join-Path $botDir ".env"

# Read API keys from .env
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    $newsKey = ($envContent | Select-String "NEWSAPI_KEY=(.+)").Matches.Groups[1].Value
    $pexelsKey = ($envContent | Select-String "PEXELS_API_KEY=(.+)").Matches.Groups[1].Value
}

# Encode client_secret.json
$csPath = Join-Path $botDir "client_secret.json"
if (Test-Path $csPath) {
    $csContent = Get-Content $csPath -Raw
    Write-Host "[1] client_secret.json - COPY THIS AS SECRET 'CLIENT_SECRET_JSON':" -ForegroundColor Yellow
    Write-Host $csContent -ForegroundColor White
} else {
    Write-Host "[!] client_secret.json not found" -ForegroundColor Red
    Write-Host "    Run the bot locally once (py ai_news_bot.py) to generate it via OAuth."
}

Write-Host ""

# Encode youtube_token.pickle
$tkPath = Join-Path $botDir "youtube_token.pickle"
if (Test-Path $tkPath) {
    $tkBytes = [System.IO.File]::ReadAllBytes($tkPath)
    $tkB64 = [System.Convert]::ToBase64String($tkBytes)
    Write-Host "[2] youtube_token.pickle - COPY THIS AS SECRET 'YOUTUBE_TOKEN_B64':" -ForegroundColor Yellow
    Write-Host $tkB64 -ForegroundColor White
} else {
    Write-Host "[!] youtube_token.pickle not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ADD THESE 4 SECRETS TO YOUR GITHUB REPO:" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Go to: GitHub Repo -> Settings -> Secrets and variables -> Actions"
Write-Host ""
Write-Host "Add these repository secrets:" -ForegroundColor Yellow
Write-Host "  $(if ($newsKey) { '✓' } else { '✗' }) NEWSAPI_KEY    = $($newsKey ? $newsKey : '(from your .env file)')"
Write-Host "  $(if ($pexelsKey) { '✓' } else { '✗' }) PEXELS_API_KEY = $($pexelsKey ? $pexelsKey : '(from your .env file)')"
Write-Host "  $(if (Test-Path $csPath) { '✓' } else { '✗' }) CLIENT_SECRET_JSON = (paste JSON from step 1 - all on one line)"
Write-Host "  $(if (Test-Path $tkPath) { '✓' } else { '✗' }) YOUTUBE_TOKEN_B64  = (paste base64 from step 2)"
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  PUSH TO GITHUB" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   git init"
Write-Host "   git add ."
Write-Host '   git commit -m "Add AI News Bot with GitHub Actions"'
Write-Host "   git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  WORKFLOW WILL RUN AUTOMATICALLY" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Schedule: Every 2 hours (24/7)"
Write-Host "  Manual:   Actions tab -> 'AI News Bot' -> 'Run workflow'"
Write-Host "  Logs:     Actions tab -> click any workflow run"
Write-Host ""
Write-Host "  NOTE: The first run may take ~10 min (installing deps)."
Write-Host "  YouTube token is cached between runs and auto-refreshed."
