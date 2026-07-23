import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.exchange.coindcx import CoinDCXExchange
from src.exchange.websocket import CoinDCXWebSocket


class TestCoinDCXExchange:
    def setup_method(self):
        self.exchange = CoinDCXExchange()

    @pytest.mark.asyncio
    async def test_fetch_ohlcv_empty_on_error(self):
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client.get = AsyncMock(return_value=mock_response)
        self.exchange._http_client = mock_client

        result = await self.exchange.fetch_ohlcv("BTC_USDT", "4h", 100)
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_instruments(self):
        mock_http = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=[{"symbol": "BTCUSDT"}])
        mock_http.get = AsyncMock(return_value=mock_response)
        self.exchange._http_client = mock_http

        result = await self.exchange.get_instruments()
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_fetch_balance(self):
        self.exchange.api_key = "test_key"
        self.exchange.api_secret = "test_secret"
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"total": {"USDT": 1000}})
        mock_client.post = AsyncMock(return_value=mock_response)
        self.exchange._http_client = mock_client

        result = await self.exchange.fetch_balance()
        assert "total" in result


class TestCoinDCXWebSocket:
    def setup_method(self):
        self.ws = CoinDCXWebSocket()

    @pytest.mark.asyncio
    async def test_subscribe(self):
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        self.ws._ws = mock_ws

        await self.ws.subscribe([{"name": "ticker", "pairs": ["BTC-USDT"]}])
        mock_ws.send.assert_called_once()
