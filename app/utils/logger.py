from loguru import logger
import sys
from app.config import settings

# Remove default handler
logger.remove()

# Add custom handler with format
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True
)

# Add file handler for production
if settings.environment == "production":
    logger.add(
        "logs/app.log",
        rotation="500 MB",
        retention="10 days",
        level="INFO"
    )

# Export logger
__all__ = ["logger"]