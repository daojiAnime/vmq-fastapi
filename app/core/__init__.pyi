import structlog

from .config import Settings

logger: structlog.stdlib.BoundLogger[structlog.types.WrappedLogger, structlog.types.EventDict]

settings: Settings
