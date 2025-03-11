"""
Unit tests for code_utils module.
"""

import unittest
from typing import Any, Dict, List

from neuron.code_utils import UserMessageTextContentPart, content_str


class TestCodeUtils(unittest.TestCase):
    """Tests for code_utils module."""

    def test_content_str_with_none(self):
        """Test that content_str handles None correctly."""
        result = content_str(None)
        self.assertEqual(result, "")

    def test_content_str_with_string(self):
        """Test that content_str handles string input correctly."""
        test_str = "Hello, world!"
        result = content_str(test_str)
        self.assertEqual(result, test_str)

    def test_content_str_with_text_list(self):
        """Test that content_str handles a list of text items correctly."""
        content: List[Dict[str, Any]] = [
            {"type": "text", "text": "Hello, "},
            {"type": "text", "text": "world!"},
        ]
        result = content_str(content)
        self.assertEqual(result, "Hello, world!")

    def test_content_str_with_mixed_content(self):
        """Test that content_str handles mixed text and image_url content correctly."""
        content: List[Dict[str, Any]] = [
            {"type": "text", "text": "Check out this image: "},
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/image.jpg"},
            },
            {"type": "text", "text": " Isn't it nice?"},
        ]
        result = content_str(content)
        self.assertEqual(result, "Check out this image: <image> Isn't it nice?")

    def test_content_str_with_only_image(self):
        """Test that content_str handles content with only image_url correctly."""
        content: List[Dict[str, Any]] = [
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
        result = content_str(content)
        self.assertEqual(result, "<image>")

    def test_content_str_with_invalid_type(self):
        """Test that content_str raises TypeError for invalid content type."""
        with self.assertRaises(TypeError):
            content_str(123)  # type: ignore

    def test_content_str_with_invalid_list_item(self):
        """Test that content_str raises TypeError for invalid list item."""
        with self.assertRaises(TypeError):
            content_str(["invalid item"])  # type: ignore

    def test_content_str_with_missing_type(self):
        """Test that content_str raises AssertionError for dict without 'type'."""
        with self.assertRaises(AssertionError):
            content_str([{"text": "No type specified"}])  # type: ignore

    def test_content_str_with_unknown_type(self):
        """Test that content_str raises ValueError for unknown type."""
        with self.assertRaises(ValueError):
            content_str([{"type": "unknown_type", "content": "Some content"}])  # type: ignore


if __name__ == "__main__":
    unittest.main()
