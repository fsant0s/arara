"""
Unit tests for the runtime_logging module.

This module tests the functionality of the runtime logging system, including:
- Starting and stopping logging
- Logging chat completions
- Logging events and neuron creation
"""

import logging
import unittest
import uuid
from datetime import datetime
from unittest import mock

import neuron.runtime_logging as runtime_logging
from neuron.logger.base_logger import BaseLogger, LLMConfig


class MockLogger(BaseLogger):
    """Mock logger for testing."""

    def __init__(self):
        """Initialize the mock logger."""
        self.started = False
        self.session_id = "test-session-id"
        self.events = []

    def start(self):
        """Start the logger."""
        self.started = True
        return self.session_id

    def stop(self):
        """Stop the logger."""
        self.started = False
        return True

    def log_chat_completion(self, *args, **kwargs):
        """Log a chat completion."""
        self.events.append(("chat_completion", args, kwargs))

    def log_new_neuron(self, *args, **kwargs):
        """Log a new neuron."""
        self.events.append(("new_neuron", args, kwargs))

    def log_event(self, *args, **kwargs):
        """Log an event."""
        self.events.append(("event", args, kwargs))

    def log_new_wrapper(self, *args, **kwargs):
        """Log a new wrapper."""
        self.events.append(("new_wrapper", args, kwargs))

    def log_new_client(self, *args, **kwargs):
        """Log a new client."""
        self.events.append(("new_client", args, kwargs))

    def get_connection(self):
        """Get the connection."""
        return None

    def error(self, message):
        """Log an error message."""
        self.events.append(("error", message))


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

    @mock.patch("neuron.runtime_logging.LoggerFactory.get_logger")
    def test_start_with_default_logger(self, mock_get_logger):
        """Test starting logging with the default logger."""
        mock_get_logger.return_value = self.mock_logger
        session_id = runtime_logging.start()
        self.assertEqual(session_id, self.mock_logger.session_id)
        self.assertTrue(runtime_logging.is_logging)
        mock_get_logger.assert_called_once_with(logger_type="file", config=None)

    @mock.patch("neuron.runtime_logging.LoggerFactory.get_logger")
    def test_start_with_logger_type_and_config(self, mock_get_logger):
        """Test starting logging with a specific logger type and config."""
        mock_get_logger.return_value = self.mock_logger
        config = {"path": "logs/test.log"}
        session_id = runtime_logging.start(logger_type="file", config=config)
        self.assertEqual(session_id, self.mock_logger.session_id)
        self.assertTrue(runtime_logging.is_logging)
        mock_get_logger.assert_called_once_with(logger_type="file", config=config)

    @mock.patch("neuron.runtime_logging.logger.error")
    def test_start_with_exception(self, mock_error):
        """Test handling of exceptions when starting logging."""
        # Configure the mock to raise an exception
        self.mock_logger.start = mock.MagicMock(side_effect=Exception("Test error"))

        # Call start with the mock logger that will raise an exception
        session_id = runtime_logging.start(logger=self.mock_logger)

        # The session_id should be None when an exception occurs
        self.assertIsNone(session_id)

        # Para este teste, vamos verificar que is_logging permanece False após uma exceção
        self.assertFalse(runtime_logging.is_logging)

    def test_stop_when_logging(self):
        """Test stopping logging when it's active."""
        # First, mock that logging is active
        runtime_logging.is_logging = True
        runtime_logging.neuron_logger = self.mock_logger

        # Now call stop and check the result
        result = runtime_logging.stop()

        # Verify that logging is now inactive
        self.assertFalse(runtime_logging.is_logging)

        # The result should match what the logger's stop method returns
        # In our MockLogger, the stop method should return True
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
        request = {
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
        }
        response = "Hello, how can I help you?"
        is_cached = 0
        cost = 0.01
        start_time = datetime.now().isoformat()

        runtime_logging.log_chat_completion(
            invocation_id,
            client_id,
            wrapper_id,
            neuron_name,
            request,
            response,
            is_cached,
            cost,
            start_time,
        )

        self.assertEqual(len(self.mock_logger.events), 1)
        log_type, args, kwargs = self.mock_logger.events[0]
        self.assertEqual(log_type, "chat_completion")

    @mock.patch("neuron.runtime_logging.logging_enabled")
    def test_log_chat_completion_when_disabled(self, mock_enabled):
        """Test that log_chat_completion does nothing when logging is disabled."""
        mock_enabled.return_value = False
        runtime_logging.log_chat_completion(uuid.uuid4(), 1, 2, "TestNeuron", {}, "", 0, 0.0, "")
        self.assertEqual(len(self.mock_logger.events), 0)

    def test_log_event(self):
        """Test logging an event."""
        runtime_logging.start(logger=self.mock_logger)

        runtime_logging.log_event("TestSource", "test_event", value="test_value")

        self.assertEqual(len(self.mock_logger.events), 1)
        log_type, args, kwargs = self.mock_logger.events[0]
        self.assertEqual(log_type, "event")

    @mock.patch("neuron.runtime_logging.logging_enabled")
    def test_log_event_when_disabled(self, mock_enabled):
        """Test that log_event does nothing when logging is disabled."""
        mock_enabled.return_value = False
        runtime_logging.log_event("TestSource", "test_event")
        self.assertEqual(len(self.mock_logger.events), 0)


if __name__ == "__main__":
    unittest.main()
