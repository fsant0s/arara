"""
Unit tests for exception_utils module.
"""

import unittest

from neuron.exception_utils import (
    CredentialError,
    FileTypeError,
    InputValidationError,
    NeuronNameConflict,
    PathTraversalError,
    SecurityError,
    SenderRequired,
)


class TestNeuronNameConflict(unittest.TestCase):
    """Tests for NeuronNameConflict exception."""

    def test_default_message(self):
        """Test that default message is correctly set."""
        exception = NeuronNameConflict()
        self.assertEqual(str(exception), "Found multiple neurons with the same name.")

    def test_custom_message(self):
        """Test that custom message is correctly set."""
        custom_msg = "Custom error message"
        exception = NeuronNameConflict(msg=custom_msg)
        self.assertEqual(str(exception), custom_msg)


class TestSenderRequired(unittest.TestCase):
    """Tests for SenderRequired exception."""

    def test_default_message(self):
        """Test that default message is correctly set."""
        exception = SenderRequired()
        self.assertEqual(exception.message, "Sender is required but not provided.")
        self.assertEqual(str(exception), "Sender is required but not provided.")

    def test_custom_message(self):
        """Test that custom message is correctly set."""
        custom_msg = "Custom sender error message"
        exception = SenderRequired(message=custom_msg)
        self.assertEqual(exception.message, custom_msg)
        self.assertEqual(str(exception), custom_msg)


class TestSecurityError(unittest.TestCase):
    """Tests for SecurityError exception."""

    def test_default_message(self):
        """Test that default message is correctly set."""
        exception = SecurityError()
        self.assertEqual(exception.message, "A security error occurred.")
        self.assertEqual(str(exception), "A security error occurred.")

    def test_custom_message(self):
        """Test that custom message is correctly set."""
        custom_msg = "Custom security error message"
        exception = SecurityError(message=custom_msg)
        self.assertEqual(exception.message, custom_msg)
        self.assertEqual(str(exception), custom_msg)


class TestCredentialError(unittest.TestCase):
    """Tests for CredentialError exception."""

    def test_default_message(self):
        """Test that default message is correctly set."""
        exception = CredentialError()
        self.assertEqual(exception.message, "Invalid or missing credential.")
        self.assertIsNone(exception.provider)

    def test_with_provider(self):
        """Test that provider is correctly included in the message."""
        exception = CredentialError(provider="openai")
        self.assertIn("openai", exception.message)
        self.assertEqual(exception.provider, "openai")

    def test_custom_message_with_provider(self):
        """Test that custom message with provider is correctly set."""
        custom_msg = "API key not found"
        exception = CredentialError(message=custom_msg, provider="groq")
        self.assertIn(custom_msg, exception.message)
        self.assertIn("groq", exception.message)
        self.assertEqual(exception.provider, "groq")


class TestInputValidationError(unittest.TestCase):
    """Tests for InputValidationError exception."""

    def test_default_message(self):
        """Test that default message is correctly set."""
        exception = InputValidationError()
        self.assertEqual(exception.message, "Input validation failed.")
        self.assertIsNone(exception.field)

    def test_with_field(self):
        """Test that field is correctly included in the message."""
        exception = InputValidationError(field="user_id")
        self.assertIn("user_id", exception.message)
        self.assertEqual(exception.field, "user_id")


class TestPathTraversalError(unittest.TestCase):
    """Tests for PathTraversalError exception."""

    def test_default_message(self):
        """Test that default message is correctly set."""
        exception = PathTraversalError()
        self.assertEqual(exception.message, "Potential path traversal detected.")
        self.assertIsNone(exception.path)

    def test_with_path(self):
        """Test that path is correctly included in the message."""
        test_path = "../../../etc/passwd"
        exception = PathTraversalError(path=test_path)
        self.assertIn(test_path, exception.message)
        self.assertEqual(exception.path, test_path)


class TestFileTypeError(unittest.TestCase):
    """Tests for FileTypeError exception."""

    def test_default_message(self):
        """Test that default message is correctly set."""
        exception = FileTypeError()
        self.assertEqual(exception.message, "Invalid or disallowed file type.")
        self.assertIsNone(exception.file_path)
        self.assertIsNone(exception.allowed_types)

    def test_with_file_path(self):
        """Test that file_path is correctly included in the message."""
        test_path = "malicious.exe"
        exception = FileTypeError(file_path=test_path)
        self.assertIn(test_path, exception.message)
        self.assertEqual(exception.file_path, test_path)

    def test_with_file_path_and_allowed_types(self):
        """Test that file_path and allowed_types are correctly included in the message."""
        test_path = "document.exe"
        allowed_types = [".txt", ".pdf", ".docx"]
        exception = FileTypeError(file_path=test_path, allowed_types=allowed_types)
        self.assertIn(test_path, exception.message)
        for allowed_type in allowed_types:
            self.assertIn(allowed_type, exception.message)
        self.assertEqual(exception.file_path, test_path)
        self.assertEqual(exception.allowed_types, allowed_types)


if __name__ == "__main__":
    unittest.main()
