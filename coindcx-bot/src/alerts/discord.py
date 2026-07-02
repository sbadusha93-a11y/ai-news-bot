from typing import Optional

import httpx
from loguru import logger

from src.config import settings


class DiscordAlert:
    def __init__(self):
        self.webhook_url = settings.discord_webhook_url
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=15)
        return self._http

    async def send_message(self, message: str) -> bool:
        if not self.webhook_url:
            logger.warning("Discord webhook not configured")
            return False

        try:
            http = await self._get_http()
            resp = await http.post(self.webhook_url, json={"content": message})
            return resp.status_code == 204
        except Exception as e:
            logger.error(f"Discord send failed: {e}")
            return False

    async def send_embed(self, title: str, description: str, color: int = 0x00FF00, fields: list = None):
        if not self.webhook_url:
            return False

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": None,
        }
        if fields:
            embed["fields"] = fields

        try:
            http = await self._get_http()
            resp = await http.post(self.webhook_url, json={"embeds": [embed]})
            return resp.status_code == 204
        except Exception as e:
            logger.error(f"Discord embed failed: {e}")
            return False

    async def send_trade_alert(self, trade: dict):
        color = 0x00FF00 if trade.get("side") == "long" else 0xFF0000
        fields = [
            {"name": "Symbol", "value": trade.get("symbol", "N/A"), "inline": True},
            {"name": "Direction", "value": trade.get("side", "").upper(), "inline": True},
            {"name": "Entry", "value": f"${trade.get('entry_price', 0):.4f}", "inline": True},
            {"name": "Stop Loss", "value": f"${trade.get('stop_loss', 0):.4f}", "inline": True},
            {"name": "Take Profit", "value": f"${trade.get('take_profit_1', 0):.4f}", "inline": True},
            {"name": "Confidence", "value": f"{trade.get('confidence_score', 0):.1f}%", "inline": True},
        ]
        if trade.get("pnl") is not None:
            fields.append({"name": "PnL", "value": f"${trade['pnl']:.2f}", "inline": True})
        await self.send_embed(
            f"Trade {trade.get('status', 'unknown').upper()}",
            trade.get("reason_entry", "No reason provided"),
            color,
            fields,
        )

    async def close(self):
        if self._http:
            await self._http.aclose()
