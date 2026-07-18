"""Runs bot API + Streamlit dashboard behind a single port proxy.
No BOT_API_URL env var needed — both services share one container.
"""
import asyncio
import os
import signal
import subprocess
import sys
import time

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

PORT = int(os.getenv("PORT", "8080"))
API_PORT = 8081
DASH_PORT = 8501

proxy = FastAPI()
proxy.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@proxy.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def proxy_handler(request: Request, path: str):
    if not path or path.startswith(("api/v1/", "docs", "openapi.json", "redoc")):
        target = f"http://127.0.0.1:{API_PORT}/{path}"
    else:
        qs = request.url.query
        target = f"http://127.0.0.1:{DASH_PORT}/{path}" + (f"?{qs}" if qs else "")
    async with httpx.AsyncClient(timeout=120) as client:
        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)
        resp = await client.request(
            request.method, target, headers=headers, content=body,
        )
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))


def run_bot():
    env = os.environ.copy()
    env["PORT"] = str(API_PORT)
    proc = subprocess.Popen(
        [sys.executable, "-m", "src.main", "--api"],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc


def run_dashboard():
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "src/dashboard/app.py",
         f"--server.port={DASH_PORT}", "--server.address=0.0.0.0",
         "--server.headless=true", "--browser.gatherUsageStats=false"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return proc


async def main():
    bot_proc = run_bot()
    dash_proc = run_dashboard()
    time.sleep(3)

    config = uvicorn.Config(proxy, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)

    def shutdown(*args):
        bot_proc.terminate()
        dash_proc.terminate()
        bot_proc.wait()
        dash_proc.wait()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
