import asyncio
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.config import settings


def safe_json(obj):
    """Recursively convert non-serializable values (inf, nan) to null/0."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0
        return obj
    if isinstance(obj, dict):
        return {k: safe_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [safe_json(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(safe_json(v) for v in obj)
    return obj

app = FastAPI(
    title="CoinDCX Pro Bot API",
    description="REST API for CoinDCX Pro Trading Bot",
    version="2.0.0",
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


@app.get("/api/v1/status")
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


@app.get("/api/v1/positions")
async def get_positions():
    global bot_instance
    if not bot_instance:
        return {"positions": []}
    return {"positions": bot_instance.trade_executor.get_active_positions()}


@app.get("/api/v1/portfolio")
async def get_portfolio():
    global bot_instance
    if not bot_instance:
        return {"balance": 0, "total_pnl": 0, "open_positions": 0}

    metrics = bot_instance.risk_manager.get_metrics()
    return {
        "balance": 10000 + metrics["total_pnl"],
        "initial_balance": 10000,
        "total_pnl": metrics["total_pnl"],
        "daily_pnl": metrics["daily_pnl"],
        "weekly_pnl": metrics["weekly_pnl"],
        "open_positions": bot_instance.trade_executor.get_position_count(),
        "metrics": metrics,
    }


@app.post("/api/v1/trade")
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


@app.post("/api/v1/close/{symbol}")
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


@app.post("/api/v1/close_all")
async def close_all_positions():
    global bot_instance
    if not bot_instance:
        raise HTTPException(400, "Bot not initialized")

    results = await bot_instance.trade_executor.close_all_positions("api_emergency")
    return {"success": True, "closed": len(results), "trades": results}


@app.post("/api/v1/control")
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


def set_bot_instance(bot):
    global bot_instance
    bot_instance = bot
