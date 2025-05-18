from typing import Any, Dict, Literal, Optional

from src.logger.base_logger import BaseLogger
from src.logger.file_logger import FileLogger

__all__ = ("LoggerFactory",)


class LoggerFactory:
    @staticmethod
    def get_logger(
        logger_type: Literal["file"] = "file", config: Optional[Dict[str, Any]] = None
    ) -> BaseLogger:
        if config is None:
            config = {}

        if logger_type == "file":
            return FileLogger(config)
        else:
            raise ValueError(f"[logger_factory] Unknown logger type: {logger_type}")
