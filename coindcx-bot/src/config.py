import json
import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    coin_dcx_api_key: str = ""
    coin_dcx_api_secret: str = ""
    database_url: str = "sqlite+aiosqlite:///data/bot.db"
    redis_url: str = "redis://localhost:6379/0"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    discord_webhook_url: str = ""
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    alert_email: str = ""
    dashboard_username: str = "admin"
    dashboard_password: str = "admin"
    newsapi_key: str = ""
    twitter_bearer_token: str = ""
    ml_training_enabled: bool = True
    ml_model_path: str = "data/models"
    bot_mode: str = "paper"
    log_level: str = "INFO"
    max_positions: int = 3
    max_risk_per_trade: float = 1.0

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

CONFIG_PATH = Path(__file__).parent.parent / "config"


def load_config() -> dict:
    config_file = CONFIG_PATH / "config.json"
    with open(config_file) as f:
        return json.load(f)


def load_weights() -> dict:
    weights_file = CONFIG_PATH / "weights.json"
    with open(weights_file) as f:
        return json.load(f)


bot_config = load_config()
indicator_weights = load_weights()
