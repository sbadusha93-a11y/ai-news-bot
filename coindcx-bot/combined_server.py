"""Runs bot API + Streamlit dashboard behind a single-port TCP proxy.
Both services share one container — no BOT_API_URL env var needed.
WebSocket (Streamlit) and HTTP (bot API) are both handled transparently.
"""
import asyncio
import os
import signal
import subprocess
import sys
import time

PORT = int(os.getenv("PORT", "8080"))
API_PORT = 8081
DASH_PORT = 8501


async def pipe(reader, writer):
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        try:
            writer.close()
        except Exception:
            pass


async def handle_client(client_reader, client_writer):
    try:
        data = await client_reader.read(4096)
        if not data:
            return

        parts = data.decode("utf-8", errors="replace").split("\r\n")[0].split(" ")
        path = parts[1] if len(parts) >= 2 else "/"

        if path.startswith(("/api/v1/", "/docs", "/openapi.json", "/redoc")):
            target_port = API_PORT
        else:
            target_port = DASH_PORT

        target_reader, target_writer = await asyncio.open_connection("127.0.0.1", target_port)
        target_writer.write(data)
        await target_writer.drain()

        await asyncio.gather(
            pipe(client_reader, target_writer),
            pipe(target_reader, client_writer),
        )
    except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError, OSError) as e:
        try:
            body = f"<html><body><h1>503 Backend Unavailable</h1><p>{e}</p></body></html>"
            resp = (
                f"HTTP/1.1 503 Service Unavailable\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n\r\n{body}"
            )
            client_writer.write(resp.encode())
            await client_writer.drain()
        except Exception:
            pass
    finally:
        try:
            client_writer.close()
        except Exception:
            pass


async def start_proxy():
    server = await asyncio.start_server(handle_client, "0.0.0.0", PORT)
    print(f"[proxy] Listening on 0.0.0.0:{PORT}")
    async with server:
        await server.serve_forever()


def run_bot():
    env = os.environ.copy()
    env["PORT"] = str(API_PORT)
    proc = subprocess.Popen(
        [sys.executable, "-m", "src.main", "--api"],
        env=env,
    )
    return proc


def run_dashboard():
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "src/dashboard/app.py",
         f"--server.port={DASH_PORT}", "--server.address=0.0.0.0",
         "--server.headless=true", "--browser.gatherUsageStats=false"],
    )
    return proc


async def main():
    bot_proc = run_bot()
    dash_proc = run_dashboard()

    # Wait for both to start
    await asyncio.sleep(10)

    def shutdown(*args):
        bot_proc.terminate()
        dash_proc.terminate()
        bot_proc.wait()
        dash_proc.wait()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    await start_proxy()


if __name__ == "__main__":
    asyncio.run(main())
