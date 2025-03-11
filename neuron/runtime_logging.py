from __future__ import annotations

import logging
import sqlite3
import uuid
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Optional, TypeVar, Union

from openai.types.chat import ChatCompletion

from neuron.logger.base_logger import BaseLogger, LLMConfig
from neuron.logger.logger_factory import LoggerFactory

if TYPE_CHECKING:
    from .clients import ClientFactory
    from .clients.cloud_based import GroqClient
    from .neurons import Neuron

logger = logging.getLogger(__name__)

neuron_logger = None
is_logging = False

F = TypeVar("F", bound=Callable[..., Any])


def start(
    logger: Optional[BaseLogger] = None,
    logger_type: Literal["file"] = "file",
    config: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Start logging for the runtime.
    Args:
        logger (BaseLogger):    A logger instance
        logger_type (str):      The type of logger to use (default: sqlite)
        config (dict):          Configuration for the logger
    Returns:
        session_id (str(uuid.uuid4)):       a unique id for the logging session
    """
    global neuron_logger
    global is_logging

    if logger:
        neuron_logger = logger
    else:
        neuron_logger = LoggerFactory.get_logger(logger_type=logger_type, config=config)

    session_id = None  # Initialize session_id with a default value
    try:
        session_id = neuron_logger.start()
        is_logging = True
    except Exception as e:
        # Use the Python logger instead of the neuron_logger here
        logger_msg = f"[runtime logging] Failed to start logging: {e}"
        if hasattr(logger, "error"):
            logger.error(logger_msg)
        else:
            # Use the module logger instead
            logger.error(logger_msg)

    return session_id


# SUGESTÃO DE IMPLEMENTAÇÃO PARA CAPTURAR A EXCEÇÃO DE INICILIZAR COM ERRO DENTRO DE START
""" def start(
    logger: Optional[BaseLogger] = None,
    logger_type: Literal["file"] = "file",
    config: Optional[Dict[str, Any]] = None,
) -> Optional[str]:  # Atualizado para retornar None em caso de erro
    global neuron_logger
    global is_logging

    if logger:
        neuron_logger = logger
    else:
        try:
            neuron_logger = LoggerFactory.get_logger(logger_type=logger_type, config=config)
        except Exception as e:
            logger = logging.getLogger("neuron.runtime_logging")
            logger.error(f"[runtime logging] Failed to start logging: {e}")
            return None  # Retorna None em caso de erro, sem propagar a exceção

    try:
        session_id = neuron_logger.start()
        is_logging = True
    except Exception as e:
        logger = logging.getLogger("neuron.runtime_logging")
        logger.error(f"[runtime logging] Failed to start logging: {e}")
        return None
    return session_id """


def log_chat_completion(
    invocation_id: uuid.UUID,
    client_id: int,
    wrapper_id: int,
    neuron: Union[str, Neuron],
    request: Dict[str, Union[float, str, List[Dict[str, str]]]],
    response: Union[str, ChatCompletion],
    is_cached: int,
    cost: float,
    start_time: str,
) -> None:
    if neuron_logger is None:
        logger.error("[runtime logging] log_chat_completion: neuron logger is None")
        return

    neuron_logger.log_chat_completion(
        invocation_id,
        client_id,
        wrapper_id,
        neuron,
        request,
        response,
        is_cached,
        cost,
        start_time,
    )


def log_new_neuron(neuron: Neuron, init_args: Dict[str, Any]) -> None:
    if neuron_logger is None:
        logger.error("[runtime logging] log_new_neuron: neuron logger is None")
        return
    neuron_logger.log_new_neuron(neuron, init_args)


def log_event(source: Union[str, Neuron], name: str, **kwargs: Dict[str, Any]) -> None:
    if neuron_logger is None:
        logger.error("[runtime logging] log_event: neuron logger is None")
        return
    neuron_logger.log_event(source, name, **kwargs)


def log_new_wrapper(
    wrapper: ClientFactory, init_args: Dict[str, Union[LLMConfig, List[LLMConfig]]]
) -> None:
    if neuron_logger is None:
        logger.error("[runtime logging] log_new_wrapper: neuron logger is None")
        return

    neuron_logger.log_new_wrapper(wrapper, init_args)


def stop() -> bool:
    """
    Stop logging for the runtime.
    Returns:
        result (bool): Whether the operation was successful
    """
    global neuron_logger
    global is_logging

    if not is_logging:
        logger.warning("[runtime logging] stop() called but logging is not active")
        return False

    try:
        if neuron_logger:
            neuron_logger.stop()
        is_logging = False
        return True
    except Exception as e:
        logger.error(f"[runtime logging] Failed to stop logging: {e}")
        return False


def get_connection() -> Union[None, sqlite3.Connection]:
    if neuron_logger is None:
        logger.error("[runtime logging] get_connection: neuron logger is None")
        return None

    return neuron_logger.get_connection()


def logging_enabled() -> bool:
    return is_logging


def log_new_client(
    client: Union[
        GroqClient
        # TODO: AzureOpenAI, OpenAI, GeminiClient, AnthropicClient, MistralAIClient, TogetherClient, GroqClient, CohereClient
    ],
    wrapper: ClientFactory,
    init_args: Dict[str, Any],
) -> None:
    if neuron_logger is None:
        logger.error("[runtime logging] log_new_client: neuron logger is None")
        return

    neuron_logger.log_new_client(client, wrapper, init_args)
