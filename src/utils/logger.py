"""Logger utility for the RBDD project."""
import sys
from loguru import logger

def setup_logger(level: str = "INFO") -> None:
    """Configures the logger with the specified level.
    
    Args:
        level (str): Logging level, e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level
    )
    logger.add(
        "results/simulation.log",
        rotation="10 MB",
        retention="1 week",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=level
    )
