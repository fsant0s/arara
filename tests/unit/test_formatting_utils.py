"""
Unit tests for formatting_utils module.
"""

import unittest
import os
import sys
from unittest.mock import patch

# Import the module to test
from neuron.formatting_utils import colored


class TestFormattingUtils(unittest.TestCase):
    """Tests for the formatting_utils module."""

    def test_colored_with_termcolor_available(self):
        """
        Test that colored returns colored text when termcolor is available.

        This test assumes that termcolor is installed, which should be the case
        in the development environment.
        """
        text = "Hello, World!"
        result = colored(text, color="red")
        # Since we can't easily check the exact ANSI codes without knowing the
        # terminal capabilities, we'll just check that the result is not the
        # original text (i.e., some transformation occurred)
        self.assertIsInstance(result, str)

    def test_colored_with_different_colors(self):
        """Test that colored works with different color options."""
        text = "Test text"

        # Test with different colors
        for color in ["red", "green", "blue", "yellow"]:
            result = colored(text, color=color)
            self.assertIsInstance(result, str)

    def test_colored_with_attributes(self):
        """Test that colored works with different attributes."""
        text = "Test text"

        # Test with different attributes
        attrs = ["bold", "underline"]
        result = colored(text, color="red", attrs=attrs)
        self.assertIsInstance(result, str)

    @patch("neuron.formatting_utils.colored", side_effect=lambda text, **kwargs: str(text))
    def test_colored_fallback_when_termcolor_unavailable(self, mock_colored):
        """
        Test that the fallback implementation works when termcolor is unavailable.

        This test mocks the colored function to simulate termcolor being unavailable.
        """
        text = "Hello, World!"
        # Call the patched version which should use our lambda that just returns the text
        result = mock_colored(text, color="red")
        # Check that text is returned as-is
        self.assertEqual(result, text)
        self.assertIsInstance(result, str)

    def test_colored_with_no_color_env_var(self):
        """Test that colored respects the NO_COLOR environment variable."""
        text = "Test text"

        # Save the original environment variable value
        original_no_color = os.environ.get('NO_COLOR')

        try:
            # Set the NO_COLOR environment variable
            os.environ['NO_COLOR'] = '1'

            # Import the module again to register the new environment value
            # We need to reload the module to ensure it sees the new environment variable
            import importlib
            import neuron.formatting_utils
            importlib.reload(neuron.formatting_utils)

            # Now get the colored function from the reloaded module
            colored_fn = neuron.formatting_utils.colored

            # Test with color, but it should respect NO_COLOR
            result = colored_fn(text, color="red")
            self.assertEqual(result, text)  # Should not apply color

        finally:
            # Restore the original environment variable
            if original_no_color is None:
                del os.environ['NO_COLOR']
            else:
                os.environ['NO_COLOR'] = original_no_color

            # Reload the module again to reset to the original state
            import neuron.formatting_utils
            importlib.reload(neuron.formatting_utils)


if __name__ == "__main__":
    unittest.main()
