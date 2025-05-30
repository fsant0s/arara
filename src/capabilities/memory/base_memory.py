from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict, field_serializer

from image import Image


class MemoryMimeType(Enum):
    """Supported MIME types for memory content."""

    TEXT = "text/plain"
    JSON = "application/json"
    MARKDOWN = "text/markdown"
    IMAGE = "image/*"
    BINARY = "application/octet-stream"


ContentType = Union[str, bytes, Dict[str, Any], Image]


class MemoryContent(BaseModel):
    """A memory content item."""

    content: ContentType
    """The content of the memory item. It can be a string, bytes, dict, or :class:`~Image`."""

    mime_type: MemoryMimeType | str = MemoryMimeType.TEXT
    """The MIME type of the memory content."""

    metadata: Dict[str, Any] | None = None
    """Metadata associated with the memory item."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("mime_type")
    def serialize_mime_type(self, mime_type: MemoryMimeType | str) -> str:
        """Serialize the MIME type to a string."""
        if isinstance(mime_type, MemoryMimeType):
            return mime_type.value
        return mime_type


class MemoryQueryResult(BaseModel):
    """Result of a memory :meth:`~memory.Memory.query` operation."""

    results: List[MemoryContent]


class UpdateContextResult(BaseModel):
    """Result of a memory :meth:`~memory.Memory.update_context` operation."""

    memories: MemoryQueryResult


class Memory(ABC):
    """Protocol defining the interface for memory implementations.

    A memory is the storage for data that can be used to enrich or modify the model context.

    A memory implementation can use any storage mechanism, such as a list, a database, or a file system.
    It can also use any retrieval mechanism, such as vector search or text search.
    It is up to the implementation to decide how to store and retrieve data.

    It is also a memory implementation's responsibility to update the model context
    with relevant memory content based on the current model context and querying the memory store.

    See :class:`~memory.ListMemory` for an example implementation.
    """

    component_type = "memory"

    @abstractmethod
    def update_context(
        self,
        model_context,
    ) -> UpdateContextResult:
        """
        Update the provided model context using relevant memory content.

        Args:
            model_context: The context to update.

        Returns:
            UpdateContextResult containing relevant memories
        """
        ...

    @abstractmethod
    def query(
        self,
        query: str | MemoryContent,
        **kwargs: Any,
    ) -> MemoryQueryResult:
        """
        Query the memory store and return relevant entries.

        Args:
            query: Query content item
            **kwargs: Additional implementation-specific parameters

        Returns:
            MemoryQueryResult containing memory entries with relevance scores
        """
        ...

    @abstractmethod
    def add(self, content: MemoryContent) -> None:
        """
        Add a new content to memory.

        Args:
            content: The memory content to add
        """
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all entries from memory."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Clean up any resources used by the memory implementation."""
        ...
