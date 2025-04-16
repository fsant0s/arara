"""
Enhanced logger for the NEURON framework with consistent formatting and contextual information.

This module provides an advanced logging system that extends the basic logging
capabilities with additional context, consistent formatting, and integration with
monitoring metrics.
"""

import inspect
import json
import logging
import os
import socket
import sys
import threading
import time
import traceback
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

# Configure standard logging
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ContextualLogger:
    """
    Enhanced logger that adds contextual information to log entries.

    This logger adds consistent context to each log entry, such as
    request IDs, operation IDs, neuron information, and performance metrics.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        Initialize a new ContextualLogger.

        Args:
            name: Logger name, typically the module name
            level: Initial logging level
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)
        self._context: Dict[str, Any] = {}
        self._request_id: Optional[str] = None
        self._thread_local = threading.local()

    def setup_file_handler(self, log_file: str, log_format: Optional[str] = None) -> None:
        """
        Set up a file handler for this logger.

        Args:
            log_file: Path to the log file
            log_format: Format string for log messages (optional)
        """
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def setup_console_handler(self, log_format: Optional[str] = None) -> None:
        """
        Set up a console handler for this logger.

        Args:
            log_format: Format string for log messages (optional)
        """
        handler = logging.StreamHandler()
        formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def set_level(self, level: int) -> None:
        """
        Set the logging level.

        Args:
            level: Logging level (e.g. logging.DEBUG, logging.INFO, etc.)
        """
        self._logger.setLevel(level)

    def start_request(self, request_id: Optional[str] = None) -> str:
        """
        Start a new request context.

        Args:
            request_id: Custom request ID (optional, will generate one if not provided)

        Returns:
            The request ID
        """
        self._thread_local.request_id = request_id or str(uuid4())
        self._thread_local.start_time = time.time()
        return self._thread_local.request_id

    def end_request(self) -> None:
        """End the current request context and log the total request time."""
        if hasattr(self._thread_local, "start_time") and hasattr(self._thread_local, "request_id"):
            elapsed_ms = (time.time() - self._thread_local.start_time) * 1000
            self.info(
                f"Request {self._thread_local.request_id} completed",
                extra={"elapsed_ms": elapsed_ms},
            )

            # Clean up
            delattr(self._thread_local, "request_id")
            delattr(self._thread_local, "start_time")

    def _add_default_context(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add default context information to the log entry.

        Args:
            extra: Extra information to include in the log

        Returns:
            Enhanced context dictionary
        """
        # Create a copy of the extra dict to avoid modifying the original
        ctx = {} if extra is None else extra.copy()

        # Add request ID if available
        if hasattr(self._thread_local, "request_id"):
            ctx["request_id"] = self._thread_local.request_id

        # Add hostname
        ctx["hostname"] = socket.gethostname()

        # Add timestamp
        ctx["timestamp"] = datetime.now().isoformat()

        # Add caller information
        caller_frame = inspect.currentframe().f_back.f_back
        if caller_frame:
            ctx["caller"] = {
                "file": os.path.basename(caller_frame.f_code.co_filename),
                "line": caller_frame.f_lineno,
                "function": caller_frame.f_code.co_name,
            }

        # Add global context
        ctx.update(self._context)

        return ctx

    def with_context(self, **kwargs) -> "ContextualLogger":
        """
        Create a new logger with additional context.

        Args:
            **kwargs: Context key-value pairs

        Returns:
            A new ContextualLogger with the combined context
        """
        new_logger = ContextualLogger(self._logger.name, self._logger.level)
        new_logger._context = {**self._context, **kwargs}
        return new_logger

    def debug(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log a debug message with context.

        Args:
            msg: The log message
            *args: Arguments for the message format string
            extra: Extra context to add to the log entry
            **kwargs: Additional context as keyword arguments
        """
        ctx = self._add_default_context(extra or {})
        ctx.update(kwargs)
        self._logger.debug(msg, *args, extra={"ctx": json.dumps(ctx)})

    def info(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log an info message with context.

        Args:
            msg: The log message
            *args: Arguments for the message format string
            extra: Extra context to add to the log entry
            **kwargs: Additional context as keyword arguments
        """
        ctx = self._add_default_context(extra or {})
        ctx.update(kwargs)
        self._logger.info(msg, *args, extra={"ctx": json.dumps(ctx)})

    def warning(self, msg: str, *args, extra: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """
        Log a warning message with context.

        Args:
            msg: The log message
            *args: Arguments for the message format string
            extra: Extra context to add to the log entry
            **kwargs: Additional context as keyword arguments
        """
        ctx = self._add_default_context(extra or {})
        ctx.update(kwargs)
        self._logger.warning(msg, *args, extra={"ctx": json.dumps(ctx)})

    def error(
        self,
        msg: str,
        *args,
        exc_info: bool = False,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """
        Log an error message with context.

        Args:
            msg: The log message
            *args: Arguments for the message format string
            exc_info: Whether to include exception info
            extra: Extra context to add to the log entry
            **kwargs: Additional context as keyword arguments
        """
        ctx = self._add_default_context(extra or {})
        ctx.update(kwargs)

        # Automatically add exception info for better debugging
        if exc_info:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_type is not None:
                ctx["exception"] = {
                    "type": exc_type.__name__,
                    "message": str(exc_value),
                    "traceback": traceback.format_exc(),
                }

        self._logger.error(msg, *args, exc_info=exc_info, extra={"ctx": json.dumps(ctx)})

    def critical(
        self,
        msg: str,
        *args,
        exc_info: bool = True,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """
        Log a critical message with context.

        Args:
            msg: The log message
            *args: Arguments for the message format string
            exc_info: Whether to include exception info (defaults to True for critical)
            extra: Extra context to add to the log entry
            **kwargs: Additional context as keyword arguments
        """
        ctx = self._add_default_context(extra or {})
        ctx.update(kwargs)

        # Always add exception info for critical errors if available
        if exc_info:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if exc_type is not None:
                ctx["exception"] = {
                    "type": exc_type.__name__,
                    "message": str(exc_value),
                    "traceback": traceback.format_exc(),
                }

        self._logger.critical(msg, *args, exc_info=exc_info, extra={"ctx": json.dumps(ctx)})


def log_operation(logger: ContextualLogger, level: int = logging.INFO):
    """
    Decorator to log function calls with execution time.

    Args:
        logger: ContextualLogger to use
        level: Logging level for the execution message

    Returns:
        Decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate a request ID for this operation
            request_id = logger.start_request()

            # Log the start of the operation
            arg_str = ", ".join([str(a) for a in args] + [f"{k}={v}" for k, v in kwargs.items()])
            if len(arg_str) > 200:  # Truncate if too long
                arg_str = arg_str[:197] + "..."

            logger.info(
                f"Started {func.__name__}({arg_str})",
                operation=func.__name__,
                request_id=request_id,
            )

            start_time = time.time()
            try:
                # Execute the function
                result = func(*args, **kwargs)

                # Log successful completion
                elapsed_ms = (time.time() - start_time) * 1000
                logger.info(
                    f"Completed {func.__name__} in {elapsed_ms:.2f}ms",
                    operation=func.__name__,
                    elapsed_ms=elapsed_ms,
                    request_id=request_id,
                )

                return result
            except Exception as e:
                # Log exception
                elapsed_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True,
                    operation=func.__name__,
                    elapsed_ms=elapsed_ms,
                    request_id=request_id,
                )
                raise
            finally:
                # End the request context
                logger.end_request()

        return wrapper

    return decorator


# Create a global logger manager
_loggers: Dict[str, ContextualLogger] = {}


def get_logger(name: str) -> ContextualLogger:
    """
    Get or create a ContextualLogger.

    Args:
        name: Logger name

    Returns:
        A ContextualLogger instance
    """
    if name not in _loggers:
        _loggers[name] = ContextualLogger(name)
    return _loggers[name]


def configure_all_loggers(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: Optional[str] = None,
) -> None:
    """
    Configure all loggers with the same settings.

    Args:
        level: Logging level
        log_file: Path to the log file (optional)
        console: Whether to log to console
        log_format: Format string for log messages (optional)
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add file handler if requested
    if log_file:
        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(log_format or DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # Update all existing contextual loggers
    for logger in _loggers.values():
        logger.set_level(level)


class ToolCallEvent:
    def __init__(
        self,
        *,
        tool_name: str,
        arguments: Dict[str, Any],
        result: str,
    ) -> None:
        """Used by subclasses of :class:`~autogen_core.tools.BaseTool` to log executions of tools.

        Args:
            tool_name (str): The name of the tool.
            arguments (Dict[str, Any]): The arguments of the tool. Must be json serializable.
            result (str): The result of the tool. Must be a string.

        Example:

            .. code-block:: python

                from autogen_core import EVENT_LOGGER_NAME
                from autogen_core.logging import ToolCallEvent

                logger = logging.getLogger(EVENT_LOGGER_NAME)
                logger.info(ToolCallEvent(tool_name="Tool1", call_id="123", arguments={"arg1": "value1"}))

        """
        self.kwargs: Dict[str, Any] = {}
        self.kwargs["type"] = "ToolCall"
        self.kwargs["tool_name"] = tool_name
        self.kwargs["arguments"] = arguments
        self.kwargs["result"] = result
        try:
            agent_id = MessageHandlerContext.agent_id()
        except RuntimeError:
            agent_id = None
        self.kwargs["agent_id"] = None if agent_id is None else str(agent_id)

    # This must output the event in a json serializable format
    def __str__(self) -> str:
        return json.dumps(self.kwargs)
