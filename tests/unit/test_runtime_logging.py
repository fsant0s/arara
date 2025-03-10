"""
Unit tests for the runtime_logging module.

This module tests the functionality of the runtime logging system, including:
- Starting and stopping logging
- Logging chat completions
- Logging events and neuron creation
"""

import unittest
from unittest import mock
import uuid
import logging
from datetime import datetime

import neuron.runtime_logging as runtime_logging
from neuron.logger.base_logger import BaseLogger, LLMConfig


class MockLogger(BaseLogger):
    """Mock logger for testing."""

    def __init__(self):
        self.logs = []
        self.started = False
        self.session_id = str(uuid.uuid4())

    def start(self):
        self.started = True
        return self.session_id

    def stop(self):
        self.started = False
        return True

    def log_chat_completion(self, *args, **kwargs):
        self.logs.append(("chat_completion", args, kwargs))

    def log_new_neuron(self, *args, **kwargs):
        self.logs.append(("new_neuron", args, kwargs))

    def log_event(self, *args, **kwargs):
        self.logs.append(("event", args, kwargs))

    def log_new_wrapper(self, *args, **kwargs):
        self.logs.append(("new_wrapper", args, kwargs))

    def log_new_client(self, *args, **kwargs):
        self.logs.append(("new_client", args, kwargs))


class TestRuntimeLogging(unittest.TestCase):
    """Tests for the runtime_logging module."""

    def setUp(self):
        """Set up test environment."""
        # Reset global variables before each test
        runtime_logging.neuron_logger = None
        runtime_logging.is_logging = False
        self.mock_logger = MockLogger()

    def test_start_with_custom_logger(self):
        """Test starting logging with a custom logger."""
        session_id = runtime_logging.start(logger=self.mock_logger)
        self.assertEqual(session_id, self.mock_logger.session_id)
        self.assertTrue(runtime_logging.is_logging)
        self.assertEqual(runtime_logging.neuron_logger, self.mock_logger)

    @mock.patch('neuron.runtime_logging.LoggerFactory.get_logger')
    def test_start_with_default_logger(self, mock_get_logger):
        """Test starting logging with the default logger."""
        mock_get_logger.return_value = self.mock_logger
        session_id = runtime_logging.start()
        self.assertEqual(session_id, self.mock_logger.session_id)
        self.assertTrue(runtime_logging.is_logging)
        mock_get_logger.assert_called_once_with(logger_type="file", config=None)

    @mock.patch('neuron.runtime_logging.LoggerFactory.get_logger')
    def test_start_with_logger_type_and_config(self, mock_get_logger):
        """Test starting logging with a specific logger type and config."""
        mock_get_logger.return_value = self.mock_logger
        config = {"path": "logs/test.log"}
        session_id = runtime_logging.start(logger_type="file", config=config)
        self.assertEqual(session_id, self.mock_logger.session_id)
        self.assertTrue(runtime_logging.is_logging)
        mock_get_logger.assert_called_once_with(logger_type="file", config=config)

    @mock.patch('neuron.runtime_logging.logger.error')
    def test_start_with_exception(self, mock_error):
        """Test handling of exceptions when starting logging."""
        self.mock_logger.start = mock.MagicMock(side_effect=Exception("Test error"))
        runtime_logging.start(logger=self.mock_logger)
        self.assertFalse(runtime_logging.is_logging)
        mock_error.assert_called_once()
        self.assertIn("Failed to start logging", mock_error.call_args[0][0])

    def test_stop_when_logging(self):
        """Test stopping logging when it's active."""
        runtime_logging.start(logger=self.mock_logger)
        result = runtime_logging.stop()
        self.assertFalse(runtime_logging.is_logging)
        self.assertTrue(result)

    def test_stop_when_not_logging(self):
        """Test stopping logging when it's not active."""
        result = runtime_logging.stop()
        self.assertFalse(runtime_logging.is_logging)
        self.assertFalse(result)

    def test_logging_enabled(self):
        """Test the logging_enabled function."""
        self.assertFalse(runtime_logging.logging_enabled())
        runtime_logging.start(logger=self.mock_logger)
        self.assertTrue(runtime_logging.logging_enabled())
        runtime_logging.stop()
        self.assertFalse(runtime_logging.logging_enabled())

    def test_log_chat_completion(self):
        """Test logging a chat completion."""
        runtime_logging.start(logger=self.mock_logger)

        invocation_id = uuid.uuid4()
        client_id = 1
        wrapper_id = 2
        neuron_name = "TestNeuron"
        request = {"messages": [{"role": "user", "content": "Hello"}], "temperature": 0.7}
        response = "Hello, how can I help you?"
        is_cached = 0
        cost = 0.01
        start_time = datetime.now().isoformat()

        runtime_logging.log_chat_completion(
            invocation_id, client_id, wrapper_id, neuron_name,
            request, response, is_cached, cost, start_time
        )

        self.assertEqual(len(self.mock_logger.logs), 1)
        log_type, args, kwargs = self.mock_logger.logs[0]
        self.assertEqual(log_type, "chat_completion")

    @mock.patch('neuron.runtime_logging.logging_enabled')
    def test_log_chat_completion_when_disabled(self, mock_enabled):
        """Test that log_chat_completion does nothing when logging is disabled."""
        mock_enabled.return_value = False
        runtime_logging.log_chat_completion(
            uuid.uuid4(), 1, 2, "TestNeuron", {}, "", 0, 0.0, ""
        )
        self.assertEqual(len(self.mock_logger.logs), 0)

    def test_log_event(self):
        """Test logging an event."""
        runtime_logging.start(logger=self.mock_logger)

        runtime_logging.log_event("TestSource", "test_event", value="test_value")

        self.assertEqual(len(self.mock_logger.logs), 1)
        log_type, args, kwargs = self.mock_logger.logs[0]
        self.assertEqual(log_type, "event")

    @mock.patch('neuron.runtime_logging.logging_enabled')
    def test_log_event_when_disabled(self, mock_enabled):
        """Test that log_event does nothing when logging is disabled."""
        mock_enabled.return_value = False
        runtime_logging.log_event("TestSource", "test_event")
        self.assertEqual(len(self.mock_logger.logs), 0)


if __name__ == "__main__":
    unittest.main()
