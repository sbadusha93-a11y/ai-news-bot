import asyncio
from typing import Optional

from loguru import logger


class DesktopNotification:
    def __init__(self):
        self._enabled = False
        self._queue = asyncio.Queue()

    async def send_notification(self, title: str, message: str, urgency: str = "normal"):
        try:
            import plyer
            plyer.notification.notify(
                title=title,
                message=message,
                app_name="CoinDCX Bot",
                timeout=10,
            )
            return True
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Desktop notification failed: {e}")

        try:
            import subprocess
            subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f'New-BaloonTip -Title "{title}" -Message "{message}"',
                ],
                capture_output=True,
                timeout=5,
            )
            return True
        except Exception:
            return False

    async def send_trade_alert(self, trade: dict):
        title = f"Trade {trade.get('status', 'unknown').upper()}: {trade.get('symbol', 'N/A')}"
        message = (
            f"{trade.get('side', '').upper()} @ ${trade.get('entry_price', 0):.4f} | "
            f"Confidence: {trade.get('confidence_score', 0):.1f}%"
        )
        await self.send_notification(title, message)
