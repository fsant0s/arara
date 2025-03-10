"""
Security utilities for the NEURON framework.

This module provides utilities for secure handling of API keys, secrets,
and other security-related functionality.
"""

import os
import logging
import warnings
from typing import Dict, Optional, Any, List

logger = logging.getLogger(__name__)


class CredentialManager:
    """
    Securely manages API keys and other credentials.

    This class provides methods to securely access API keys and other credentials
    from environment variables with proper validation and error handling.
    """

    @staticmethod
    def get_api_key(name: str, required: bool = True) -> Optional[str]:
        """
        Retrieves an API key from environment variables.

        Args:
            name: The name of the API key (e.g., "OPENAI", "GROQ")
            required: Whether the API key is required (raises error if missing)

        Returns:
            The API key as a string or None if not required and not found

        Raises:
            ValueError: If the API key is required but not found in environment variables
        """
        env_var_name = f"{name.upper()}_API_KEY"
        api_key = os.environ.get(env_var_name)

        if not api_key and required:
            raise ValueError(
                f"Missing required API key: {env_var_name}. "
                f"Please set the {env_var_name} environment variable."
            )

        if not api_key and not required:
            warnings.warn(
                f"API key {env_var_name} not found in environment variables.",
                UserWarning,
                stacklevel=2
            )

        return api_key

    @staticmethod
    def validate_api_key(api_key: Optional[str], provider: str) -> bool:
        """
        Validates that an API key is properly formatted.

        Args:
            api_key: The API key to validate
            provider: The name of the provider (e.g., "OPENAI", "GROQ")

        Returns:
            True if the API key is valid, False otherwise
        """
        if not api_key:
            return False

        # Basic validation: not empty and meets minimum length requirements
        min_length = {
            "OPENAI": 20,
            "GROQ": 20,
            "COHERE": 20,
            # Add more providers as needed
        }.get(provider.upper(), 10)

        if len(api_key) < min_length:
            return False

        prefix_checks = {
            "OPENAI": api_key.startswith(("sk-", "org-")),
            "GROQ": api_key.startswith("gsk_"),
            # Add more provider-specific validations as needed
        }

        # If we have a specific check for this provider, use it
        # Otherwise, just check that the key is not empty
        return prefix_checks.get(provider.upper(), True)

    @staticmethod
    def get_endpoint_url(name: str, required: bool = False) -> Optional[str]:
        """
        Retrieves an API endpoint URL from environment variables.

        Args:
            name: The name of the service (e.g., "OPENAI", "AZURE_OPENAI")
            required: Whether the URL is required (raises error if missing)

        Returns:
            The endpoint URL as a string or None if not required and not found

        Raises:
            ValueError: If the URL is required but not found in environment variables
        """
        possible_env_vars = [
            f"{name.upper()}_API_BASE",
            f"{name.upper()}_ENDPOINT",
            f"{name.upper()}_URL",
        ]

        for env_var in possible_env_vars:
            url = os.environ.get(env_var)
            if url:
                return url

        if required:
            raise ValueError(
                f"Missing required API endpoint URL for {name}. "
                f"Please set one of these environment variables: {', '.join(possible_env_vars)}"
            )

        return None


def sanitize_input(input_data: Any) -> Any:
    """
    Sanitizes input data to prevent injection attacks.

    This function applies appropriate sanitization techniques based on the input type.

    Args:
        input_data: The input data to sanitize

    Returns:
        The sanitized input data
    """
    if isinstance(input_data, str):
        # Remove potentially dangerous control characters
        return "".join(char for char in input_data if ord(char) >= 32 or char == "\n" or char == "\t")
    elif isinstance(input_data, dict):
        return {k: sanitize_input(v) for k, v in input_data.items()}
    elif isinstance(input_data, list):
        return [sanitize_input(item) for item in input_data]
    else:
        # For non-container types, return as is
        return input_data


def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Validates a file path to prevent path traversal attacks.

    Args:
        file_path: The file path to validate
        allowed_extensions: List of allowed file extensions (e.g., ['.txt', '.csv'])

    Returns:
        True if the file path is valid, False otherwise
    """
    # Prevent path traversal attacks
    if ".." in file_path or file_path.startswith("/"):
        return False

    # Validate file extension if specified
    if allowed_extensions:
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in allowed_extensions:
            return False

    return True
