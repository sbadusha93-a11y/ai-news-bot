from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from src.config import settings


class Base(DeclarativeBase):
    pass


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    leverage = Column(Integer, default=1)
    stop_loss = Column(Float, nullable=True)
    take_profit_1 = Column(Float, nullable=True)
    take_profit_2 = Column(Float, nullable=True)
    take_profit_3 = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    trade_quality_score = Column(Float, nullable=True)
    buy_probability = Column(Float, nullable=True)
    sell_probability = Column(Float, nullable=True)
    reason_entry = Column(Text, nullable=True)
    reason_exit = Column(Text, nullable=True)
    ai_decision = Column(Text, nullable=True)
    status = Column(String(20), default="open")
    entry_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    exit_time = Column(DateTime, nullable=True)
    highest_price = Column(Float, nullable=True)
    lowest_price = Column(Float, nullable=True)
    trailing_stop_active = Column(Integer, default=0)
    break_even_active = Column(Integer, default=0)
    is_paper = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    event_type = Column(String(50))
    message = Column(Text)
    indicator_values = Column(Text, nullable=True)
    market_conditions = Column(Text, nullable=True)
    screenshot_path = Column(String(500), nullable=True)


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    daily_pnl = Column(Float, default=0.0)
    weekly_pnl = Column(Float, default=0.0)
    monthly_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    average_trade = Column(Float, default=0.0)
    average_win = Column(Float, default=0.0)
    average_loss = Column(Float, default=0.0)
    expectancy = Column(Float, default=0.0)


class Database:
    def __init__(self):
        self._engine = None
        self._session_maker = None

    async def initialize(self):
        db_url = (settings.database_url or "").strip()
        if not db_url:
            db_url = "sqlite+aiosqlite:///data/bot.db"
        if db_url.startswith("sqlite"):
            self._engine = create_async_engine(db_url, echo=False)
        else:
            self._engine = create_async_engine(db_url, echo=False, pool_size=20)

        self._session_maker = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> Optional[AsyncSession]:
        if self._session_maker is None:
            return None
        return self._session_maker()

    async def save_trade(self, trade_data: Dict) -> Optional[int]:
        valid_columns = {c.name for c in Trade.__table__.columns}
        filtered = {k: v for k, v in trade_data.items() if k in valid_columns}
        if "entry_time" in filtered and isinstance(filtered["entry_time"], str):
            filtered["entry_time"] = datetime.fromisoformat(filtered["entry_time"])
        try:
            session = await self.get_session()
            if session is None:
                logger.warning("Database not initialized, skipping save_trade")
                return None
            async with session.begin():
                trade = Trade(**filtered)
                session.add(trade)
                await session.flush()
                return trade.id
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
            return None

    async def update_trade(self, trade_id: int, update_data: Dict):
        session = await self.get_session()
        if session is None:
            return
        async with session.begin():
            result = await session.get(Trade, trade_id)
            if result:
                for key, value in update_data.items():
                    setattr(result, key, value)

    async def get_trades(
        self,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[Trade]:
        from sqlalchemy import select

        session = await self.get_session()
        if session is None:
            return []
        query = select(Trade).order_by(Trade.created_at.desc())
        if status:
            query = query.where(Trade.status == status)
        query = query.offset(offset).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_open_trades(self) -> List[Trade]:
        return await self.get_trades(status="open")

    async def log_trade_event(
        self, trade_id: int, event_type: str, message: str,
        indicator_values: Optional[str] = None,
        market_conditions: Optional[str] = None,
    ):
        session = await self.get_session()
        if session is None:
            return
        async with session.begin():
            log = TradeLog(
                trade_id=trade_id,
                event_type=event_type,
                message=message,
                indicator_values=indicator_values,
                market_conditions=market_conditions,
            )
            session.add(log)

    async def update_performance(self, metrics: Dict):
        session = await self.get_session()
        if session is None:
            return
        async with session.begin():
            pm = PerformanceMetric(**metrics)
            session.add(pm)

    async def clear_all_trades(self):
        session = await self.get_session()
        if session is None:
            return
        async with session.begin():
            from sqlalchemy import delete
            await session.execute(delete(TradeLog))
            await session.execute(delete(Trade))
            await session.execute(delete(PerformanceMetric))
            logger.info("All trades, logs, and metrics cleared")

    async def close_stale_trades(self):
        try:
            session = await self.get_session()
            if session is None:
                return
            async with session.begin():
                from sqlalchemy import update
                cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
                now = datetime.now(timezone.utc)
                query = (
                    update(Trade)
                    .where(Trade.status == "open")
                    .where(Trade.created_at < cutoff)
                    .values(status="closed", reason_exit="stale_timeout", exit_time=now)
                )
                result = await session.execute(query)
                if result.rowcount > 0:
                    logger.info(f"Closed {result.rowcount} stale trades older than 24h")
        except Exception as e:
            logger.error(f"Failed to close stale trades: {e}")

    async def close(self):
        if self._engine:
            await self._engine.dispose()
