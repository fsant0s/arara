"""
Unit tests for the security_utils module.

This module tests the functionality of the security utilities, including:
- CredentialManager for handling API keys and endpoints
- Input sanitization functions
- File path validation functions
"""

import os
import unittest
import warnings
from unittest import mock

from neuron.security_utils import CredentialManager, sanitize_input, validate_file_path


class TestCredentialManager(unittest.TestCase):
    """Tests for the CredentialManager class."""

    def setUp(self):
        """Set up test environment."""
        # Clear any environment variables that might interfere with tests
        if "TEST_API_KEY" in os.environ:
            del os.environ["TEST_API_KEY"]

    def test_get_api_key_when_present(self):
        """Test retrieving an API key when it's present in environment variables."""
        with mock.patch.dict(os.environ, {"TEST_API_KEY": "test_key_value"}):
            api_key = CredentialManager.get_api_key("TEST")
            self.assertEqual(api_key, "test_key_value")

    def test_get_api_key_required_but_missing(self):
        """Test that ValueError is raised when a required API key is missing."""
        with self.assertRaises(ValueError):
            CredentialManager.get_api_key("NONEXISTENT", required=True)

    def test_get_api_key_not_required_and_missing(self):
        """Test that a warning is issued when a non-required API key is missing."""
        with warnings.catch_warnings(record=True) as w:
            api_key = CredentialManager.get_api_key("NONEXISTENT", required=False)
            self.assertIsNone(api_key)
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, UserWarning))

    def test_validate_api_key_openai_valid(self):
        """Test validation of a valid OpenAI API key."""
        self.assertTrue(
            CredentialManager.validate_api_key("sk-validopenaiapikey12345678901234", "OPENAI")
        )

    def test_validate_api_key_openai_invalid(self):
        """Test validation of an invalid OpenAI API key."""
        self.assertFalse(CredentialManager.validate_api_key("invalid", "OPENAI"))
        self.assertFalse(CredentialManager.validate_api_key(None, "OPENAI"))

    def test_validate_api_key_groq_valid(self):
        """Test validation of a valid Groq API key."""
        self.assertTrue(
            CredentialManager.validate_api_key("gsk_validgroqapikey123456789012345", "GROQ")
        )

    def test_validate_api_key_groq_invalid(self):
        """Test validation of an invalid Groq API key."""
        self.assertFalse(CredentialManager.validate_api_key("invalid", "GROQ"))
        self.assertFalse(
            CredentialManager.validate_api_key("invalid-prefix-12345678901234567890", "GROQ")
        )

    def test_get_endpoint_url_when_present(self):
        """Test retrieving an endpoint URL when it's present in environment variables."""
        with mock.patch.dict(os.environ, {"OPENAI_API_BASE": "https://api.openai.com/v1"}):
            url = CredentialManager.get_endpoint_url("OPENAI")
            self.assertEqual(url, "https://api.openai.com/v1")

    def test_get_endpoint_url_alternative_var_names(self):
        """Test retrieving an endpoint URL using alternative environment variable names."""
        with mock.patch.dict(os.environ, {"TEST_URL": "https://test.api/v1"}):
            url = CredentialManager.get_endpoint_url("TEST")
            self.assertEqual(url, "https://test.api/v1")

    def test_get_endpoint_url_required_but_missing(self):
        """Test that ValueError is raised when a required endpoint URL is missing."""
        with self.assertRaises(ValueError):
            CredentialManager.get_endpoint_url("NONEXISTENT", required=True)

    def test_get_endpoint_url_not_required_and_missing(self):
        """Test that None is returned when a non-required endpoint URL is missing."""
        url = CredentialManager.get_endpoint_url("NONEXISTENT", required=False)
        self.assertIsNone(url)


class TestSanitizeInput(unittest.TestCase):
    """Tests for the sanitize_input function."""

    def test_sanitize_string(self):
        """Test sanitizing a string with potentially dangerous characters."""
        input_str = "Hello\x00World\x1FLLM"
        sanitized = sanitize_input(input_str)
        self.assertEqual(sanitized, "HelloWorldLLM")

    def test_sanitize_string_preserves_newlines_tabs(self):
        """Test that sanitize_input preserves newlines and tabs."""
        input_str = "Hello\nWorld\tLLM"
        sanitized = sanitize_input(input_str)
        self.assertEqual(sanitized, "Hello\nWorld\tLLM")

    def test_sanitize_dict(self):
        """Test sanitizing a dictionary with nested values."""
        input_dict = {"text": "Hello\x00World", "nested": {"value": "Test\x1FValue"}}
        expected = {"text": "HelloWorld", "nested": {"value": "TestValue"}}
        self.assertEqual(sanitize_input(input_dict), expected)

    def test_sanitize_list(self):
        """Test sanitizing a list with various values."""
        input_list = ["Hello\x00World", 123, {"key": "Value\x1F"}]
        expected = ["HelloWorld", 123, {"key": "Value"}]
        self.assertEqual(sanitize_input(input_list), expected)

    def test_sanitize_non_container_types(self):
        """Test that sanitize_input returns non-container types as is."""
        self.assertEqual(sanitize_input(123), 123)
        self.assertEqual(sanitize_input(None), None)
        self.assertEqual(sanitize_input(True), True)


class TestValidateFilePath(unittest.TestCase):
    """Tests for the validate_file_path function."""

    def test_valid_path(self):
        """Test validation of a valid file path."""
        self.assertTrue(validate_file_path("data/file.txt"))
        self.assertTrue(validate_file_path("subdir/data/file.csv"))

    def test_path_traversal_attempt(self):
        """Test that path traversal attempts are rejected."""
        self.assertFalse(validate_file_path("../data/file.txt"))
        self.assertFalse(validate_file_path("data/../file.txt"))
        self.assertFalse(validate_file_path("/etc/passwd"))

    def test_file_extension_validation(self):
        """Test validation of file extensions."""
        self.assertTrue(validate_file_path("data/file.txt", allowed_extensions=[".txt", ".csv"]))
        self.assertTrue(validate_file_path("data/file.csv", allowed_extensions=[".txt", ".csv"]))
        self.assertFalse(validate_file_path("data/file.exe", allowed_extensions=[".txt", ".csv"]))
        self.assertFalse(validate_file_path("data/file.js", allowed_extensions=[".txt", ".csv"]))


if __name__ == "__main__":
    unittest.main()
