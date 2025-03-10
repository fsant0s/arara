from typing import Any, List, Optional


class NeuronNameConflict(Exception):
    def __init__(self, msg: str = "Found multiple neurons with the same name.", *args: Any, **kwargs: Any):
        super().__init__(msg, *args, **kwargs)


class SenderRequired(Exception):
    """Exception raised when the sender is required but not provided."""

    def __init__(self, message: str = "Sender is required but not provided."):
        self.message = message
        super().__init__(self.message)


class SecurityError(Exception):
    """Base exception for all security-related errors."""

    def __init__(self, message: str = "A security error occurred."):
        self.message = message
        super().__init__(self.message)


class CredentialError(SecurityError):
    """Exception raised for errors related to API keys and credentials."""

    def __init__(self, message: str = "Invalid or missing credential.", provider: Optional[str] = None):
        self.provider = provider
        self.message = f"{message} Provider: {provider}" if provider else message
        super().__init__(self.message)


class InputValidationError(SecurityError):
    """Exception raised when input validation fails."""

    def __init__(self, message: str = "Input validation failed.", field: Optional[str] = None):
        self.field = field
        self.message = f"{message} Field: {field}" if field else message
        super().__init__(self.message)


class PathTraversalError(SecurityError):
    """Exception raised when a potential path traversal attack is detected."""

    def __init__(self, message: str = "Potential path traversal detected.", path: Optional[str] = None):
        self.path = path
        self.message = f"{message} Path: {path}" if path else message
        super().__init__(self.message)


class FileTypeError(SecurityError):
    """Exception raised when an invalid or disallowed file type is detected."""

    def __init__(
        self,
        message: str = "Invalid or disallowed file type.",
        file_path: Optional[str] = None,
        allowed_types: Optional[List[str]] = None
    ):
        self.file_path = file_path
        self.allowed_types = allowed_types

        if file_path and allowed_types:
            self.message = f"{message} File: {file_path}. Allowed types: {', '.join(allowed_types)}"
        elif file_path:
            self.message = f"{message} File: {file_path}"
        else:
            self.message = message

        super().__init__(self.message)

