# CoinDCX Pro Bot

Institutional-grade AI-powered crypto trading bot for CoinDCX exchange.

## Features

- **24×7 Automated Trading** - Runs continuously with self-recovery
- **CoinDCX API Integration** - Full exchange connectivity
- **Multi-Timeframe Analysis** - 4H primary, 1D/1H/15M confirmation
- **50+ Technical Indicators** - RSI, MACD, EMA, Bollinger, SuperTrend, Ichimoku, etc.
- **Smart Money Concepts (SMC)** - BOS, CHOCH, Order Blocks, FVG, Liquidity zones
- **Price Action Patterns** - Engulfing, Hammer, Star patterns, Double Top/Bottom, H&S
- **Volume Analysis** - OBV, CMF, MFI, Volume Profile, Whale detection
- **Sentiment Analysis** - Fear & Greed, BTC Dominance, News sentiment
- **AI Decision Engine** - Weighted scoring with configurable weights
- **Machine Learning** - XGBoost, LightGBM, Random Forest, CatBoost ensemble
- **Risk Management** - Dynamic sizing, ATR stops, trailing, break-even
- **Backtesting Engine** - 1Y/3Y/5Y/10Y backtesting with full metrics
- **Strategy Optimizer** - Parameter optimization
- **Dashboard** - Streamlit real-time dashboard
- **Alerts** - Telegram, Discord, Email, Desktop notifications
- **REST API** - FastAPI-based control interface
- **Docker Support** - Easy deployment with docker-compose
- **Security** - Encrypted keys, rate limiting, retry logic

## Project Structure

```
coindcx-bot/
├── config/             # Configuration files
│   ├── config.json     # Bot configuration
│   └── weights.json    # Indicator weights
├── data/
│   ├── historical/     # Historical market data
│   └── models/         # Trained ML models
├── logs/               # Log files
├── src/
│   ├── main.py         # Entry point
│   ├── config.py       # Settings management
│   ├── api/            # FastAPI REST server
│   ├── exchange/       # CoinDCX API & WebSocket
│   ├── data/           # Data fetching, caching, database
│   ├── indicators/     # Technical, SMC, Volume, PA, Sentiment
│   ├── strategy/       # Engine, Scorer, Analyzer
│   ├── ml/             # ML training & prediction
│   ├── risk/           # Risk manager, position sizing
│   ├── trading/        # Trade execution, monitoring, portfolio
│   ├── backtest/       # Backtesting & optimization
│   ├── alerts/         # Telegram, Discord, Email
│   ├── dashboard/      # Streamlit dashboard
│   └── utils/          # Logger, Watchdog, Helpers
├── tests/              # Unit tests
├── Dockerfile          # Docker build
├── docker-compose.yml  # Multi-service deployment
└── requirements.txt    # Python dependencies
```

## Installation

### Prerequisites

- Python 3.12+
- PostgreSQL 16+ (optional, SQLite fallback)
- Redis 7+ (optional, local cache fallback)
- TA-Lib (optional, built-in fallback)

### Local Setup

```bash
# Clone the repository
cd coindcx-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the bot
python src/main.py
```

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f bot
```

### Cloud/VPS Deployment

```bash
# Copy to server
scp -r coindcx-bot user@vps:/opt/

# SSH into server and run
ssh user@vps
cd /opt/coindcx-bot
docker-compose up -d
```

## Configuration

### Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| COINDCX_API_KEY | CoinDCX API Key | - |
| COINDCX_API_SECRET | CoinDCX API Secret | - |
| BOT_MODE | Trading mode (paper/live) | paper |
| LOG_LEVEL | Logging level | INFO |
| TELEGRAM_BOT_TOKEN | Telegram bot token | - |
| DISCORD_WEBHOOK_URL | Discord webhook URL | - |

### Bot Config (config/config.json)

- `bot.mode`: Trading mode (paper/live)
- `bot.min_confidence`: Minimum confidence to trade (default: 90%)
- `bot.min_rr`: Minimum risk/reward ratio (default: 3.0)
- `risk.*`: Risk management parameters
- `strategy_weights.*`: Scoring weights for each category
- `indicator_settings.*`: Technical indicator parameters

## Usage

### Start Bot

```bash
python src/main.py
```

### Start with API Server

```bash
python src/main.py --api
```

### API Endpoints

- `GET /api/v1/status` - Bot status
- `GET /api/v1/positions` - Active positions
- `GET /api/v1/portfolio` - Portfolio metrics
- `POST /api/v1/trade` - Execute trade
- `POST /api/v1/close/{symbol}` - Close position
- `POST /api/v1/close_all` - Close all positions
- `POST /api/v1/control` - Start/Stop/Pause/Resume
- `GET /api/v1/performance` - Performance metrics
- `GET /api/v1/market_scan` - Scan market for opportunities

### Dashboard

```bash
streamlit run src/dashboard/app.py
```

## Backtesting

```python
from src.backtest.engine import BacktestEngine
from src.data.fetcher import DataFetcher

engine = BacktestEngine(initial_balance=10000)
result = await engine.run(df)
print(f"Win Rate: {result['win_rate']}%")
print(f"Sharpe: {result['sharpe_ratio']}")
print(f"Net Profit: ${result['net_profit']}")
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Security

- API keys stored in environment variables
- Rate limiting on all exchange requests
- Retry logic with exponential backoff
- Automatic reconnection on network failure
- Watchdog for health monitoring
- Crash recovery and auto-restart

## Performance

- Async I/O for non-blocking operations
- Multi-threading for CPU-intensive tasks
- Redis caching for frequent data
- Memory optimization for large datasets
- GPU support for ML training (optional)

## License

MIT License
