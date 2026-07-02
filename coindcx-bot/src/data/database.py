from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine,
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
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50))
    message = Column(Text)
    indicator_values = Column(Text, nullable=True)
    market_conditions = Column(Text, nullable=True)
    screenshot_path = Column(String(500), nullable=True)


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.utcnow)
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
        db_url = settings.database_url
        if db_url.startswith("sqlite"):
            self._engine = create_async_engine(db_url, echo=False)
        else:
            self._engine = create_async_engine(db_url, echo=False, pool_size=20)

        self._session_maker = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        return self._session_maker()

    async def save_trade(self, trade_data: Dict) -> int:
        async with await self.get_session() as session:
            async with session.begin():
                trade = Trade(**trade_data)
                session.add(trade)
                await session.flush()
                return trade.id

    async def update_trade(self, trade_id: int, update_data: Dict):
        async with await self.get_session() as session:
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

        async with await self.get_session() as session:
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
        async with await self.get_session() as session:
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
        async with await self.get_session() as session:
            async with session.begin():
                pm = PerformanceMetric(**metrics)
                session.add(pm)

    async def close(self):
        if self._engine:
            await self._engine.dispose()
