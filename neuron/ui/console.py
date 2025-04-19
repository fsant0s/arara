import os
import sys
import time
from typing import Awaitable, Callable,  List, Optional, TypeVar, Union, cast

from neuron.cancellation_token import CancellationToken
from neuron.models import RequestUsage

from neuron.base import Response, TaskResult
from neuron.messages import (
    BaseAgentEvent,
    BaseChatMessage,
    ModelClientStreamingChunkEvent,
    MultiModalMessage
)

from termcolor import colored

def format_sender(name: str) -> str:
    color_map = {
        "user": "cyan",
        "math": "green",
        "assistant": "yellow",
        "system": "magenta",
    }
    color = color_map.get(name.lower(), "white")
    return colored(f"⟶ {name.capitalize()}:", color, attrs=["bold"])


def _is_running_in_iterm() -> bool:
    return os.getenv("TERM_PROGRAM") == "iTerm.app"


def _is_output_a_tty() -> bool:
    return sys.stdout.isatty()

SyncInputFunc = Callable[[str], str]
AsyncInputFunc = Callable[[str, Optional[CancellationToken]], Awaitable[str]]
InputFuncType = Union[SyncInputFunc, AsyncInputFunc]

T = TypeVar("T", bound=TaskResult | Response)

def aprint(output: str, end: str = "\n", flush: bool = False) -> None:
    print(output, end=end, flush=flush)

def Console(
    stream,
    *,
    no_inline_images: bool = False,
    output_stats: bool = False,
) -> T:
    render_image_iterm = _is_running_in_iterm() and _is_output_a_tty() and not no_inline_images
    start_time = time.time()
    total_usage = RequestUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

    last_processed: Optional[T] = None
    streaming_chunks: List[str] = []

    for message in stream:
        if message is None: continue
        if isinstance(message, Response):
            duration = time.time() - start_time

            # Format response content
            if isinstance(message.chat_message, MultiModalMessage):
                final_content = message.chat_message.to_text(iterm=render_image_iterm)
            else:
                final_content = message.chat_message.to_text()

            # Print formatted sender and message
            aprint(format_sender(message.chat_message.source), flush=True)
            aprint(final_content, flush=True)

            # Print usage if needed
            if message.chat_message.models_usage:
                if output_stats:
                    aprint(
                        f"[Prompt tokens: {message.chat_message.models_usage.prompt_tokens}, "
                        f"Completion tokens: {message.chat_message.models_usage.completion_tokens}]",
                        flush=True,
                    )
                total_usage.completion_tokens += message.chat_message.models_usage.completion_tokens
                total_usage.prompt_tokens += message.chat_message.models_usage.prompt_tokens

            # Print summary if enabled
            if output_stats:
                num_inner_messages = len(message.inner_messages or [])
                aprint(
                    f"{'-' * 10} Summary {'-' * 10}\n"
                    f"Number of inner messages: {num_inner_messages}\n"
                    f"Total prompt tokens: {total_usage.prompt_tokens}\n"
                    f"Total completion tokens: {total_usage.completion_tokens}\n"
                    f"Duration: {duration:.2f} seconds\n",
                    flush=True
                )

            last_processed = message  # type: ignore

        else:
            message = cast(BaseAgentEvent | BaseChatMessage, message)

            if not streaming_chunks:
                aprint(format_sender(message.source), flush=True)

            if isinstance(message, ModelClientStreamingChunkEvent):
                aprint(message.to_text(), end="")
                streaming_chunks.append(message.content)
            else:
                if streaming_chunks:
                    streaming_chunks.clear()
                    aprint("", end="\n", flush=True)

                elif isinstance(message, MultiModalMessage):
                    aprint(message.to_text(iterm=render_image_iterm), flush=True)
                else:
                    aprint(message.to_text(), flush=True)

                if message.models_usage and output_stats:
                    aprint(
                        f"[Prompt tokens: {message.models_usage.prompt_tokens}, "
                        f"Completion tokens: {message.models_usage.completion_tokens}]",
                        flush=True,
                    )
                    total_usage.completion_tokens += message.models_usage.completion_tokens
                    total_usage.prompt_tokens += message.models_usage.prompt_tokens

    return last_processed

