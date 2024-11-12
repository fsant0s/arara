import sqlite3

from unittest.mock import patch, MagicMock
from neuron.runtime_logging import (
    start,
    log_chat_completion,
    log_new_agent,
    log_event,
    log_new_wrapper,
    stop,
    get_connection,
    logging_enabled,
    log_new_client,
)


@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_log_chat_completion(mock_get_logger):
    # Configura um mock para retornar uma conexão de banco de dados simulada
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_logger.start.return_value = "mock_session_id"
    mock_logger.get_connection.return_value = MagicMock(sqlite3.Connection)
    
    # Given
    start()
    
    # When
    log_chat_completion(
        invocation_id=1,
        client_id=2,
        wrapper_id=3,
        agent="agent",
        request={"request": "request"},
        response="response",
        is_cached=4,
        cost=5.0,
        start_time="start_time",
    )
    
    # Then
    assert logging_enabled() == True
    assert get_connection() is not None

def test_should_log_chat_completion_with_none_logger():
    # Given
    stop()
    from neuron import runtime_logging
    runtime_logging.neuron_logger = None  # Redefine explicitamente para garantir que está None

    # When
    log_chat_completion(
        invocation_id=1,
        client_id=2,
        wrapper_id=3,
        agent="agent",
        request={"request": "request"},
        response="response",
        is_cached=4,
        cost=5.0,
        start_time="start_time",
    )

    # Then
    assert logging_enabled() == False
    assert get_connection() is None

@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_log_new_agent(mock_get_logger):
    # Configura um mock para o logger com uma conexão de banco de dados simulada
    mock_logger = MagicMock()
    mock_logger.get_connection.return_value = MagicMock(sqlite3.Connection)
    mock_get_logger.return_value = mock_logger  # Retorna o mock quando get_logger é chamado
    
    # Given
    start()  # Isso agora deve usar o mock de get_logger
    
    # When
    log_new_agent(agent="agent", init_args={"init_args": "init_args"})
    
    # Then
    assert logging_enabled() == True
    assert get_connection() is not None  # Verifica se get_connection retorna a conexão mockada

@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_log_event_with_logger(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    start()
    log_event(source="source", name="event_name", detail="some_detail")

    mock_logger.log_event.assert_called_once_with("source", "event_name", detail="some_detail")


def test_should_log_event_without_logger(caplog):
    # Configura o ambiente para garantir que neuron_logger seja None
    stop()
    from neuron import runtime_logging
    import logging

    runtime_logging.neuron_logger = None  # Certifica-se de que neuron_logger está definido como None

    # Define o nível de log para ERROR e especifica o logger correto para captura
    with caplog.at_level(logging.ERROR, logger="neuron.runtime_logging"):
        log_event(source="source", name="event_name")

    # Verifica se a mensagem de log esperada está presente no caplog
    assert "[runtime logging] log_event: neuron logger is None" in caplog.text


""" @patch("neuron.runtime_logging.LoggerFactory.get_logger", side_effect=Exception("Logger error"))
def test_should_start_with_error(mock_get_logger, caplog):
    # Define o nível de log para ERROR no logger "neuron.runtime_logging"
    import logging
    logger = logging.getLogger("neuron.runtime_logging")
    logger.setLevel(logging.ERROR)

    session_id = None
    with caplog.at_level(logging.ERROR, logger="neuron.runtime_logging"):
        try:
            session_id = start()
        except Exception:
            pass  # Captura a exceção para permitir que o log seja verificado

        # Verificações
        assert session_id is None
        assert "[runtime logging] Failed to start logging: Logger error" in caplog.text """

@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_log_new_agent(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    start()
    log_new_agent(agent="agent", init_args={"init_args": "init_args"})

    mock_logger.log_new_agent.assert_called_once_with("agent", {"init_args": "init_args"})


def test_should_log_new_agent_without_logger(caplog):
    stop()
    log_new_agent(agent="agent", init_args={"init_args": "init_args"})

    assert "[runtime logging] log_new_agent: neuron logger is None" in caplog.text

 
@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_log_new_wrapper_with_logger(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    start()
    wrapper = MagicMock()
    init_args = {"init_arg": "value"}
    log_new_wrapper(wrapper, init_args)

    mock_logger.log_new_wrapper.assert_called_once_with(wrapper, init_args)


def test_should_log_new_wrapper_without_logger(caplog):
    import logging
    # Garanta que neuron_logger esteja None
    stop()
    from neuron import runtime_logging
    runtime_logging.neuron_logger = None  # Certifica-se de que neuron_logger é None

    # Configura o logger para capturar erros
    with caplog.at_level(logging.ERROR, logger="neuron.runtime_logging"):
        log_new_wrapper(wrapper="wrapper", init_args={"init_arg": "value"})

    # Verifique se a mensagem de log está no caplog
    assert "[runtime logging] log_new_wrapper: neuron logger is None" in caplog.text



@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_log_new_client_with_logger(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    start()
    client = MagicMock()
    wrapper = MagicMock()
    init_args = {"init_arg": "value"}
    log_new_client(client, wrapper, init_args)

    mock_logger.log_new_client.assert_called_once_with(client, wrapper, init_args)


def test_should_log_new_client_without_logger(caplog):
    import logging

    # Garante que neuron_logger esteja None
    stop()
    from neuron import runtime_logging
    runtime_logging.neuron_logger = None  # Certifique-se de que neuron_logger é None

    # Configura o logger para capturar mensagens de erro
    with caplog.at_level(logging.ERROR, logger="neuron.runtime_logging"):
        log_new_client(client="client", wrapper="wrapper", init_args={"init_arg": "value"})

    # Verifica se a mensagem de log está presente no caplog
    assert "[runtime logging] log_new_client: neuron logger is None" in caplog.text



@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_stop_with_logger(mock_get_logger):
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger

    start()
    assert logging_enabled() == True

    stop()
    assert logging_enabled() == False
    mock_logger.stop.assert_called_once()


def test_should_stop_without_logger():
    stop()
    assert logging_enabled() == False


def test_should_get_connection_without_logger(caplog):
    import logging
    # Garante que neuron_logger esteja None
    stop()
    from neuron import runtime_logging
    runtime_logging.neuron_logger = None  # Certifique-se de que neuron_logger é None

    # Configura o logger para capturar mensagens de erro
    with caplog.at_level(logging.ERROR, logger="neuron.runtime_logging"):
        # Verifica a conexão quando neuron_logger é None
        assert get_connection() is None

    # Verifica se a mensagem de erro esperada está presente no caplog
    assert "[runtime logging] get_connection: neuron logger is None" in caplog.text


@patch("neuron.runtime_logging.LoggerFactory.get_logger")
def test_should_return_logging_enabled_status(mock_get_logger):
    start()
    assert logging_enabled() == True

    stop()
    assert logging_enabled() == False

def test_should_return_logging_disabled_status():
    stop()
    assert logging_enabled() == False

def test_should_return_logging_disabled_status_with_neuron_logger_none():
    from neuron import runtime_logging
    runtime_logging.neuron_logger = None
    assert logging_enabled() == False