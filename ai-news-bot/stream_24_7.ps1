param(
    [Parameter(Mandatory=$true)]
    [string]$StreamKey,
    [string]$VideoPath = "AI_News_20260627_v3.mp4",
    [string]$RtmpUrl = "rtmp://a.rtmp.youtube.com/live2"
)

$ErrorActionPreference = "Stop"
$scriptPath = Split-Path -Parent $PSCommandPath
$videoFullPath = Join-Path $scriptPath $VideoPath

if (-not (Test-Path $videoFullPath)) {
    Write-Host "[!] Video not found: $videoFullPath" -ForegroundColor Red
    exit 1
}

$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Host "[!] FFmpeg is required. Install it:" -ForegroundColor Yellow
    Write-Host "    winget install ffmpeg" -ForegroundColor Cyan
    Write-Host "    Or download from: https://ffmpeg.org/download.html" -ForegroundColor Cyan
    exit 1
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "  24/7 YouTube Live Stream - AI News Bot" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Video: $VideoPath"
Write-Host "Streaming to YouTube..."
Write-Host "Press Ctrl+C to stop"
Write-Host "==============================================" -ForegroundColor Cyan

$ffmpegArgs = @(
    "-stream_loop", "-1"
    "-re", "-i", $videoFullPath
    "-c:v", "libx264"
    "-preset", "veryfast"
    "-b:v", "3000k"
    "-maxrate", "3000k"
    "-bufsize", "6000k"
    "-pix_fmt", "yuv420p"
    "-g", "60"
    "-c:a", "aac"
    "-b:a", "128k"
    "-ar", "44100"
    "-f", "flv"
    "${RtmpUrl}/${StreamKey}"
)

& $ffmpeg $ffmpegArgs
