import asyncio
import json
import math
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

from src.config import settings


class SafeJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        cleaned = safe_json(content)
        return json.dumps(
            cleaned,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")


API_KEY = os.getenv("BOT_API_KEY", "")
security = HTTPBearer(auto_error=False)


async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not API_KEY:
        return True
    if credentials is None or credentials.credentials != API_KEY:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True


def safe_json(obj):
    if isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return type(obj)(safe_json(v) for v in obj)
    try:
        if hasattr(obj, '__float__'):
            f = float(obj)
            if math.isnan(f) or math.isinf(f):
                return 0
            return f
    except (TypeError, ValueError):
        pass
    return obj


app = FastAPI(
    title="CoinDCX Pro Bot API",
    description="REST API for CoinDCX Pro Trading Bot",
    version="2.0.0",
    default_response_class=SafeJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot_instance = None


class TradeRequest(BaseModel):
    symbol: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: float
    leverage: int = 1


class BotControl(BaseModel):
    action: str


@app.get("/")
async def root():
    return {
        "name": "CoinDCX Pro Bot API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/v1/status", dependencies=[Depends(verify_api_key)])
async def get_status():
    global bot_instance
    if not bot_instance:
        return {"status": "not_initialized"}

    uptime_secs = bot_instance.watchdog.health_status.get("uptime", 0)
    uptime_h = int(uptime_secs // 3600)
    uptime_m = int((uptime_secs % 3600) // 60)
    return {
        "status": "running",
        "mode": settings.bot_mode,
        "positions": bot_instance.trade_executor.get_position_count(),
        "uptime": f"{uptime_h}h {uptime_m}m",
        "health": bot_instance.watchdog.get_status() if hasattr(bot_instance, "watchdog") else {},
    }


@app.get("/api/v1/positions", dependencies=[Depends(verify_api_key)])
async def get_positions():
    global bot_instance
    if not bot_instance:
        return {"positions": []}
    return {"positions": bot_instance.trade_executor.get_active_positions()}


@app.get("/api/v1/portfolio", dependencies=[Depends(verify_api_key)])
async def get_portfolio():
    global bot_instance
    if not bot_instance:
        return {"balance": 0, "total_pnl": 0, "open_positions": 0}

    metrics = bot_instance.risk_manager.get_metrics()
    init_bal = bot_instance.risk_manager.initial_balance
    return {
        "balance": init_bal + metrics["total_pnl"],
        "initial_balance": init_bal,
        "total_pnl": metrics["total_pnl"],
        "daily_pnl": metrics["daily_pnl"],
        "weekly_pnl": metrics["weekly_pnl"],
        "open_positions": bot_instance.trade_executor.get_position_count(),
        "metrics": metrics,
    }


@app.post("/api/v1/trade", dependencies=[Depends(verify_api_key)])
async def execute_trade(request: TradeRequest):
    global bot_instance
    if not bot_instance:
        raise HTTPException(400, "Bot not initialized")

    result = await bot_instance.trade_executor.execute_trade(
        symbol=request.symbol,
        direction=request.direction,
        entry_price=request.entry_price,
        confidence=90.0,
        quality_score=85.0,
        reason="API request",
    )
    if not result:
        raise HTTPException(400, "Trade execution failed")
    return {"success": True, "trade": result}


@app.post("/api/v1/close/{symbol}", dependencies=[Depends(verify_api_key)])
async def close_position(symbol: str):
    global bot_instance
    if not bot_instance:
        raise HTTPException(400, "Bot not initialized")

    ticker = await bot_instance.exchange.fetch_ticker(symbol)
    exit_price = ticker.get("last", 0) if ticker else 0
    result = await bot_instance.trade_executor.close_trade(symbol, exit_price, "api_request")
    if not result:
        raise HTTPException(404, f"No position found for {symbol}")
    return {"success": True, "trade": result}


@app.post("/api/v1/close_all", dependencies=[Depends(verify_api_key)])
async def close_all_positions():
    global bot_instance
    if not bot_instance:
        raise HTTPException(400, "Bot not initialized")

    results = await bot_instance.trade_executor.close_all_positions("api_emergency")
    return {"success": True, "closed": len(results), "trades": results}


@app.post("/api/v1/control", dependencies=[Depends(verify_api_key)])
async def control_bot(control: BotControl):
    global bot_instance
    if not bot_instance:
        raise HTTPException(400, "Bot not initialized")

    action = control.action.lower()
    if action == "start":
        asyncio.create_task(bot_instance.start())
        return {"success": True, "message": "Bot started"}
    elif action == "stop":
        await bot_instance.stop()
        return {"success": True, "message": "Bot stopped"}
    elif action == "pause":
        bot_instance.risk_manager.pause_trading()
        return {"success": True, "message": "Trading paused"}
    elif action == "resume":
        bot_instance.risk_manager.resume_trading()
        return {"success": True, "message": "Trading resumed"}
    else:
        raise HTTPException(400, f"Unknown action: {action}")


@app.post("/api/v1/clear_history", dependencies=[Depends(verify_api_key)])
async def clear_history():
    global bot_instance
    if bot_instance and hasattr(bot_instance, "database"):
        await bot_instance.database.clear_all_trades()
        return {"success": True, "message": "All trades cleared"}
    return {"success": False, "message": "Bot not initialized"}


@app.get("/api/v1/performance")
async def get_performance():
    global bot_instance
    if not bot_instance:
        return {"metrics": {}}
    return {"metrics": bot_instance.risk_manager.get_metrics()}


@app.get("/api/v1/market_scan")
async def scan_market():
    global bot_instance
    if not bot_instance:
        return {"opportunities": []}

    opportunities = bot_instance.market_analyzer.select_top_opportunities(
        bot_instance.last_ranked if hasattr(bot_instance, "last_ranked") else [],
        top_n=10,
    )
    return {"opportunities": opportunities}


@app.post("/api/v1/trigger_scan", dependencies=[Depends(verify_api_key)])
async def trigger_scan():
    global bot_instance
    if not bot_instance:
        return {"status": "error", "message": "Bot not initialized"}
    if getattr(bot_instance, "_scan_in_progress", False):
        return {"status": "running", "message": "Scan already in progress"}
    bot_instance._scan_in_progress = True

    async def _run():
        try:
            await bot_instance.scan_market()
        finally:
            bot_instance._scan_in_progress = False

    asyncio.create_task(_run())
    return {"status": "started", "message": "Scan started in background"}


@app.get("/api/v1/tickers")
async def get_tickers():
    global bot_instance
    if not bot_instance:
        return {"tickers": {}}
    try:
        all_tickers = await bot_instance.exchange.fetch_all_tickers()
        if all_tickers:
            return {"tickers": all_tickers}
        keys = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "BNB_USDT", "XRP_USDT"]
        result = {}
        for k in keys:
            ticker = await bot_instance.exchange.fetch_ticker(k)
            if ticker:
                result[k] = ticker
        return {"tickers": result}
    except Exception:
        return {"tickers": {}}


@app.get("/api/v1/live_prices")
async def live_prices(symbols: str = Query("BTC_USDT,ETH_USDT")):
    global bot_instance
    if not bot_instance:
        return {"prices": {}}
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        all_tickers = await bot_instance.exchange.fetch_all_tickers()
        if all_tickers:
            return {"prices": {s: all_tickers.get(s, {}) for s in sym_list}}
        result = {}
        for sym in sym_list:
            ticker = await bot_instance.exchange.fetch_ticker(sym)
            if ticker:
                result[sym] = ticker
        return {"prices": result}
    except Exception:
        return {"prices": {}}


def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot
