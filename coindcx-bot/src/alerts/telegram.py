from typing import Optional

import httpx
from loguru import logger

from src.config import settings


class TelegramAlert:
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=15)
        return self._http

    async def send_message(self, message: str) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram not configured")
            return False

        try:
            http = await self._get_http()
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            resp = await http.post(url, json={
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML",
            })
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")
            return False

    async def send_trade_alert(self, trade: dict):
        emoji = "🟢" if trade.get("side") == "long" else "🔴"
        msg = (
            f"{emoji} <b>Trade {trade.get('status', 'unknown').upper()}</b>\n"
            f"Symbol: {trade.get('symbol')}\n"
            f"Direction: {trade.get('side', '').upper()}\n"
            f"Entry: ${trade.get('entry_price', 0):.4f}\n"
            f"Size: {trade.get('quantity', 0):.4f}\n"
            f"SL: ${trade.get('stop_loss', 0):.4f}\n"
            f"TP: ${trade.get('take_profit_1', 0):.4f}\n"
            f"Confidence: {trade.get('confidence_score', 0):.1f}%\n"
        )
        if trade.get("pnl") is not None:
            msg += f"PnL: ${trade['pnl']:.2f} ({trade.get('pnl_percent', 0):.2f}%)\n"
        msg += f"Reason: {trade.get('reason_entry', 'N/A')}"
        await self.send_message(msg)

    async def send_alert(self, title: str, message: str, level: str = "info"):
        emoji = {"info": "ℹ️", "warning": "⚠️", "error": "🚨", "success": "✅"}
        msg = f"{emoji.get(level, 'ℹ️')} <b>{title}</b>\n{message}"
        await self.send_message(msg)

    async def close(self):
        if self._http:
            await self._http.aclose()
