import sys
from pathlib import Path

from loguru import logger

from src.config import settings


def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )

    logger.add(
        log_dir / "bot_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
    )

    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
    )

    logger.add(
        log_dir / "trades_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="90 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
        level="INFO",
        filter=lambda record: "TRADE" in record["extra"],
    )

    logger.info("Logger initialized")
    return logger
