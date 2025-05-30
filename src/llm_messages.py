from dataclasses import dataclass
from typing import List, Literal, Optional, Union, Callable, TypeAlias

from pydantic import BaseModel, Field
from typing_extensions import Annotated, Any

from agents.types import FunctionCall
from image import Image

class SystemMessage(BaseModel):
    """System message contains instructions for the model coming from the developer.

    .. note::

        Open AI is moving away from using 'system' role in favor of 'developer' role.
        See `Model Spec <https://cdn.openai.com/spec/model-spec-2024-05-08.html#definitions>`_ for more details.
        However, the 'system' role is still allowed in their API and will be automatically converted to 'developer' role
        on the server side.
        So, you can use `SystemMessage` for developer messages.

    """

    content: str
    """The content of the message."""

    type: Literal["SystemMessage"] = "SystemMessage"


class UserMessage(BaseModel):
    """User message contains input from end users, or a catch-all for data provided to the model."""

    content: Union[str, List[Union[str, Image]]]
    """The content of the message."""

    source: str
    """The name of the agent that sent this message."""

    type: Literal["UserMessage"] = "UserMessage"


class AssistantMessage(BaseModel):
    """Assistant message are sampled from the language model."""

    content: Union[str, List[FunctionCall]]
    """The content of the message."""

    thought: str | None = None
    """The reasoning text for the completion if available. Used for reasoning model and additional text content besides function calls."""

    source: str
    """The name of the agent that sent this message."""

    type: Literal["AssistantMessage"] = "AssistantMessage"


class FunctionExecutionResult(BaseModel):
    """Function execution result contains the output of a function call."""

    content: str
    """The output of the function call."""

    name: str
    """(New in v0.4.8) The name of the function that was called."""

    call_id: str
    """The ID of the function call. Note this ID may be empty for some models."""

    is_error: bool | None = None
    """Whether the function call resulted in an error."""


LLMMessage = Annotated[
    Union[SystemMessage, UserMessage, AssistantMessage], Field(discriminator="type")
]


@dataclass
class RequestUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


FinishReasons = Literal["stop", "length", "function_calls", "content_filter", "unknown"]


@dataclass
class TopLogprob:
    logprob: float
    bytes: Optional[List[int]] = None


class ChatCompletionTokenLogprob(BaseModel):
    token: str
    logprob: float
    top_logprobs: Optional[List[TopLogprob] | None] = None
    bytes: Optional[List[int]] = None


class CreateResult(BaseModel):
    """CreateResult contains the output of a model completion."""

    finish_reason: FinishReasons
    """The reason the model finished generating the completion."""

    content: Union[str, List[FunctionCall]]
    """The output of the model completion."""

    usage: RequestUsage
    """Token usage details for both the prompt and the completion."""

    cached: bool
    """Indicates whether the completion was returned from a cache."""

    logprobs: Optional[List[ChatCompletionTokenLogprob] | None] = None
    """Log probabilities of the tokens in the completion."""

    thought: Optional[str] = None
    """The reasoning text for the completion, if available.
    Used for models that provide intermediate reasoning steps or textual explanations."""

    response_id: str
    """Unique identifier of the request made to generate the completion."""

    cost: float
    """Total cost of the request in monetary units (e.g., dollars)."""

    model_name: str
    """The name of the LLM model used to generate the completion."""

    message_retrieval_function: Optional[Callable[[], str]] = None
    """A function that retrieves a related message, if available."""

    config_id: Optional[Callable] = None
    """A builtin function or method used for configuration. Can be None and reassigned."""

    pass_filter: Optional[bool] = None
    """Indicates whether the result passed a certain filter. Can be None and reassigned."""

    class Config:
            protected_namespaces = ()

class FunctionExecutionResultMessage(BaseModel):
    """Function execution result message contains the output of multiple function calls."""

    content: List[FunctionExecutionResult]

    type: Literal["FunctionExecutionResultMessage"] = "FunctionExecutionResultMessage"

class ModelFamily:
    """A model family is a group of models that share similar characteristics from a capabilities perspective. This is different to discrete supported features such as vision, function calling, and JSON output.

    This namespace class holds constants for the model families that ARARA understands. Other families definitely exist and can be represented by a string, however, ARARA will treat them as unknown."""

    GPT_4O = "gpt-4o"
    O1 = "o1"
    O3 = "o3"
    GPT_4 = "gpt-4"
    GPT_35 = "gpt-35"
    R1 = "r1"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_5_HAIKU = "claude-3.5-haiku"
    CLAUDE_3_5_SONNET = "claude-3.5-sonnet"
    CLAUDE_3_7_SONNET = "claude-3.7-sonnet"
    UNKNOWN = "unknown"

    ANY: TypeAlias = Literal[
        "gpt-4o",
        "o1",
        "o3",
        "gpt-4",
        "gpt-35",
        "r1",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "claude-3-haiku",
        "claude-3-sonnet",
        "claude-3-opus",
        "claude-3.5-haiku",
        "claude-3.5-sonnet",
        "unknown",
    ]

    def __new__(cls, *args: Any, **kwargs: Any) -> "ModelFamily":
        raise TypeError(f"{cls.__name__} is a namespace class and cannot be instantiated.")

    @staticmethod
    def is_claude(family: str) -> bool:
        return family in (
            ModelFamily.CLAUDE_3_HAIKU,
            ModelFamily.CLAUDE_3_SONNET,
            ModelFamily.CLAUDE_3_OPUS,
            ModelFamily.CLAUDE_3_5_HAIKU,
            ModelFamily.CLAUDE_3_5_SONNET,
        )

    @staticmethod
    def is_gemini(family: str) -> bool:
        return family in (
            ModelFamily.GEMINI_1_5_FLASH,
            ModelFamily.GEMINI_1_5_PRO,
            ModelFamily.GEMINI_2_0_FLASH,
        )

    @staticmethod
    def is_openai(family: str) -> bool:
        return family in (
            ModelFamily.GPT_4O,
            ModelFamily.O1,
            ModelFamily.O3,
            ModelFamily.GPT_4,
            ModelFamily.GPT_35,
        )
