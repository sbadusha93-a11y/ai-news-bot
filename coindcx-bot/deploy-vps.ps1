param(
    [Parameter(Mandatory=$true)]
    [string]$Vps,
    [string]$ApiKey = "",
    [string]$ApiSecret = "",
    [string]$DashboardUser = "admin",
    [string]$DashboardPass = "admin"
)

<#
  Deploys the CoinDCX bot to a VPS for 24/7 operation.

  Prerequisites on the VPS:
    - Docker installed: curl -fsSL https://get.docker.com | sh
    - SSH access with key authentication

  Cheapest VPS options (2026):
    Hetzner CX22   €3.29/mo  — https://hetzner.com
    DigitalOcean   $6/mo     — https://digitalocean.com
    Linode         $5/mo     — https://linode.com
    Oracle Cloud   FREE      — https://oracle.com/cloud/free
#>

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Resolve-Path (Join-Path $scriptDir "..")
$archive = Join-Path $env:TEMP "coindcx-bot-deploy.tar.gz"

Write-Host "=== Packaging bot ==="
Set-Location $projectDir
if (Test-Path $archive) { Remove-Item $archive }
& tar czf $archive --exclude='.git' --exclude='__pycache__' --exclude='logs' --exclude='.env' "coindcx-bot"

Write-Host "=== Copying to VPS ($Vps) ==="
& scp $archive "${Vps}:/tmp/"
& ssh $Vps "sudo tar xzf /tmp/coindcx-bot-deploy.tar.gz -C /opt && rm /tmp/coindcx-bot-deploy.tar.gz"

Write-Host "=== Setting up .env ==="
ssh $Vps @"sudo tee /opt/coindcx-bot/.env > nul << 'ENVEOF'
COIN_DCX_API_KEY=$ApiKey
COIN_DCX_API_SECRET=$ApiSecret
DASHBOARD_USERNAME=$DashboardUser
DASHBOARD_PASSWORD=$DashboardPass
BOT_MODE=paper
ENVEOF
"@

Write-Host "=== Starting bot via Docker ==="
ssh $Vps "cd /opt/coindcx-bot && sudo docker-compose up -d --build"

Write-Host ""
Write-Host "=== Done ==="
Write-Host "Dashboard:  http://$Vps`:8501"
Write-Host "Logs:       ssh $Vps 'sudo docker logs -f coindcx-bot_dashboard_1'"
Write-Host "Bot logs:   ssh $Vps 'sudo docker logs -f coindcx-bot_bot_1'"
Write-Host ""
Write-Host "For live trading:"
Write-Host "  1. ssh $Vps"
Write-Host "  2. sudo nano /opt/coindcx-bot/config/config.json  # set auto_trade: true"
Write-Host "  3. Set API keys in /opt/coindcx-bot/.env"
Write-Host "  4. sudo docker-compose restart"
