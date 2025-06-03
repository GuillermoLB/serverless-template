from typing import ClassVar

from pydantic import BaseModel

from app.core.config import settings, Settings
from app.dependencies import SettingsDep


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    # Annotate settings as ClassVar since it's a class-level variable
    settings: ClassVar[Settings] = settings
    LOG_FORMAT: str = "%(levelprefix)s %(asctime)s [%(name)s:%(lineno)d] %(message)s"
    LOG_LEVEL: str = settings.LOG_LEVEL

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = settings.DISABLE_LOGGERS
    formatters: dict = {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
    }
    # Root logger is configurable. Other verbose loggers are set to INFO always
    loggers: dict = {
        "app": {"handlers": ["default"], "level": settings.LOG_LEVEL},
        "botocore.parsers": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        }
    }
