from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import inspect
import uuid

from neuron.runtime_logging import log_chat_completion, log_new_client, log_new_wrapper, logging_enabled
from neuron.logger.logger_utils import get_current_ts
from neuron.io.base import IOStream

from .base_client import BaseClient
from .helpers import PlaceHolderClient, get_client_by_type_name

import logging
import sys
from flaml.automl.logger import logger_formatter
logger = logging.getLogger(__name__)
if not logger.handlers:
    # Add the console handler.
    _ch = logging.StreamHandler(stream=sys.stdout)
    _ch.setFormatter(logger_formatter)
    logger.addHandler(_ch)

# importing opeanai
try:
    import openai
except ImportError:
    raise ImportError("Please install openai>=1 and diskcache to use neuron.ClientWrapper.")
else:
    from openai import APIError, APITimeoutError, OpenAI

class ClientWrapper:
    """A wrapper class for AI models (custom and cloud-based)."""

    extra_kwargs = {
        "agent",
        "filter_func",
        "allow_format_str_template",
        "context",
        "api_version",
        "client_type",
        "tags",
        "price",
    }

    openai_kwargs = set(inspect.getfullargspec(OpenAI.__init__).kwonlyargs)
    total_usage_summary: Optional[Dict[str, Any]] = None
    actual_usage_summary: Optional[Dict[str, Any]] = None

    def __init__(self, *, config_list: Optional[List[Dict[str, Any]]] = None, **base_config: Any):
        """
        Args:
            config_list: a list of config dicts to override the base_config.
                They can contain additional kwargs as allowed in the [create](/docs/reference/oai/client#create) method. E.g.,

        ```python
        config_list=[
            {
                "model": "gpt-4",
                "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                "client_type": "azure",
                "base_url": os.environ.get("AZURE_OPENAI_API_BASE"),
                "api_version": "2024-02-01",
            },
            {
                "model": "gpt-3.5-turbo",
                "api_key": os.environ.get("OPENAI_API_KEY"),
                "client_type": "openai",
                "base_url": "https://api.openai.com/v1",
            },
            {
                "model": "llama-7B",
                "base_url": "http://127.0.0.1:8080",
            }
        ]
        ```

            base_config: base config. It can contain both keyword arguments for openai client
                and additional kwargs.
                When using OpenAI or Azure OpenAI endpoints, please specify a non-empty 'model' either in `base_config` or in each config of `config_list`.
        """
        if logging_enabled():
            log_new_wrapper(self, locals())
        openai_config, extra_kwargs = self._separate_openai_config(base_config)
        # It's OK if "model" is not provided in base_config or config_list
        # Because one can provide "model" at `create` time.

        self._clients: List[BaseClient] = []
        self._config_list: List[Dict[str, Any]] = []
        if config_list:
            config_list = [config.copy() for config in config_list]  # make a copy before modifying
            for config in config_list:
                self._register_default_client(config, openai_config)  # could modify the config
                self._config_list.append(
                    {**extra_kwargs, **{k: v for k, v in config.items() if k not in self.openai_kwargs}}
                )
        else:
            self._register_default_client(extra_kwargs, openai_config)
            self._config_list = [extra_kwargs]
        self.wrapper_id = id(self)

    def _separate_openai_config(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Separate the config into openai_config and extra_kwargs."""
        openai_config = {k: v for k, v in config.items() if k in self.openai_kwargs}
        extra_kwargs = {k: v for k, v in config.items() if k not in self.openai_kwargs}
        return openai_config, extra_kwargs

    def _separate_create_config(self, config: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Separate the config into create_config and extra_kwargs."""
        create_config = {k: v for k, v in config.items() if k not in self.extra_kwargs}
        extra_kwargs = {k: v for k, v in config.items() if k in self.extra_kwargs}
        return create_config, extra_kwargs

    def _register_default_client(self, config: Dict[str, Any], openai_config: Dict[str, Any]) -> None:
        """Create a client with the given config to override openai_config,
        after removing extra kwargs.

        For Azure models/deployment names there's a convenience modification of model removing dots in
        the it's value (Azure deployment names can't have dots). I.e. if you have Azure deployment name
        "gpt-35-turbo" and define model "gpt-3.5-turbo" in the config the function will remove the dot
        from the name and create a client that connects to "gpt-35-turbo" Azure deployment.
        """
        openai_config = {**openai_config, **{k: v for k, v in config.items() if k in self.openai_kwargs}}
        openai_config = config if not openai_config else openai_config
        
        client_type = config.get("client")
        model_client_cls_name = config.get("model_client_cls")
        if model_client_cls_name is not None:
            # a config for a custom client is set
            # adding placeholder until the register_model_client is called with the appropriate class
            self._clients.append(PlaceHolderClient(config))
            logger.info(
                f"Detected custom model client in config: {model_client_cls_name}, model client can not be used until register_model_client is called."
            )
            # TODO: logging for custom client
        else:   
            try:
                client = get_client_by_type_name(client_type, openai_config)
                self._clients.append(client)
                if logging_enabled():
                    log_new_client(client, self, openai_config)
            except Exception as e:
                logger.error(f"Failed to create client with config: {config}. Error: {e}", exc_info=True)
                raise

    def register_model_client(self, model_client_cls: BaseClient, **kwargs):
        """Register a model client.

        Args:
            model_client_cls: A custom client class that follows the BaseClient interface
            **kwargs: The kwargs for the custom client class to be initialized with
        """
        existing_client_class = False
        for i, client in enumerate(self._clients):
            if isinstance(client, PlaceHolderClient):
                placeholder_config = client.config

                if placeholder_config.get("model_client_cls") == model_client_cls.__name__:
                    self._clients[i] = model_client_cls(placeholder_config, **kwargs)
                    return
            elif isinstance(client, model_client_cls):
                existing_client_class = True

        if existing_client_class:
            logger.warn(
                f"Model client {model_client_cls.__name__} is already registered. Add more entries in the config_list to use multiple model clients."
            )
        else:
            raise ValueError(
                f'Model client "{model_client_cls.__name__}" is being registered but was not found in the config_list. '
                f'Please make sure to include an entry in the config_list with "model_client_cls": "{model_client_cls.__name__}"'
            )

    @classmethod
    def instantiate(
        cls,
        template: Optional[Union[str, Callable[[Dict[str, Any]], str]]],
        context: Optional[Dict[str, Any]] = None,
        allow_format_str_template: Optional[bool] = False,
    ) -> Optional[str]:
        if not context or template is None:
            return template  # type: ignore [return-value]
        if isinstance(template, str):
            return template.format(**context) if allow_format_str_template else template
        return template(context)

    def _construct_create_params(self, create_config: Dict[str, Any], extra_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Prime the create_config with additional_kwargs."""
        # Validate the config
        prompt: Optional[str] = create_config.get("prompt")
        messages: Optional[List[Dict[str, Any]]] = create_config.get("messages")
        if (prompt is None) == (messages is None):
            raise ValueError("Either prompt or messages should be in create config but not both.")
        context = extra_kwargs.get("context")
        if context is None:
            # No need to instantiate if no context is provided.
            return create_config
        # Instantiate the prompt or messages
        allow_format_str_template = extra_kwargs.get("allow_format_str_template", False)
        # Make a copy of the config
        params = create_config.copy()
        if prompt is not None:
            # Instantiate the prompt
            params["prompt"] = self.instantiate(prompt, context, allow_format_str_template)
        elif context:
            # Instantiate the messages
            params["messages"] = [
                (
                    {
                        **m,
                        "content": self.instantiate(m["content"], context, allow_format_str_template),
                    }
                    if m.get("content")
                    else m
                )
                for m in messages  # type: ignore [union-attr]
            ]
        return params

    def create(self, **config: Any) -> BaseClient.BaseClientResponseProtocol:
        """Make a completion for a given config using available clients.
        Besides the kwargs allowed in openai's [or other] client, we allow the following additional kwargs.
        The config in each client will be overridden by the config.
        """
        
        invocation_id = str(uuid.uuid4())
        last = len(self._clients) - 1
        # Check if all configs in config list are activated
        non_activated = [
            client.config["model_client_cls"] for client in self._clients if isinstance(client, PlaceHolderClient)
        ]
        if non_activated:
            raise RuntimeError(
                f"Model client(s) {non_activated} are not activated. Please register the custom model clients using `register_model_client` or filter them out form the config list."
            )
        for i, client in enumerate(self._clients):
            # merge the input config with the i-th config in the config list
            full_config = {**config, **self._config_list[i]}
            # separate the config into create_config and extra_kwargs
            create_config, extra_kwargs = self._separate_create_config(full_config)
            
            # construct the create params
            params = self._construct_create_params(create_config, extra_kwargs)
            
            filter_func = extra_kwargs.get("filter_func")
            context = extra_kwargs.get("context")
            agent = extra_kwargs.get("agent")
            price = extra_kwargs.get("price", None)
            if isinstance(price, list):
                price = tuple(price)
            elif isinstance(price, float) or isinstance(price, int):
                logger.warning(
                    "Input price is a float/int. Using the same price for prompt and completion tokens. Use a list/tuple if prompt and completion token prices are different."
                )
                price = (price, price)

            total_usage = None
            actual_usage = None

            try:
                request_ts = get_current_ts()
                response = client.create(params)
            except APITimeoutError as err:
                logger.debug(f"config {i} timed out", exc_info=True)
                if i == last:
                    raise TimeoutError(
                        "OpenAI API call timed out. This could be due to congestion or too small a timeout value. The timeout can be specified by setting the 'timeout' value (in seconds) in the llm_config (if you are using agents) or the BaseClient constructor (if you are using the BaseClient directly)."
                    ) from err
            except APIError as err:
                error_code = getattr(err, "code", None)
                if logging_enabled():
                    log_chat_completion(
                        invocation_id=invocation_id,
                        client_id=id(client),
                        wrapper_id=id(self),
                        agent=agent,
                        request=params,
                        response=f"error_code:{error_code}, config {i} failed",
                        is_cached=0,
                        cost=0,
                        start_time=request_ts,
                    )

                if error_code == "content_filter":
                    # raise the error for content_filter
                    raise
                logger.debug(f"config {i} failed", exc_info=True)
                if i == last:
                    raise
            else:
                # add cost calculation before caching no matter filter is passed or not
                if price is not None:
                    response.cost = self._cost_with_customized_price(response, price)
                else:
                    response.cost = client.cost(response)

                actual_usage = client.get_usage(response)
                total_usage = actual_usage.copy() if actual_usage is not None else total_usage
                self._update_usage(actual_usage=actual_usage, total_usage=total_usage)
        
                if logging_enabled():
                    # TODO: log the config_id and pass_filter etc.
                    log_chat_completion(
                        invocation_id=invocation_id,
                        client_id=id(client),
                        wrapper_id=id(self),
                        agent=agent,
                        request=params,
                        response=response,
                        is_cached=0,
                        cost=response.cost,
                        start_time=request_ts,
                    )
                response.message_retrieval_function = client.message_retrieval
                # check the filter
                pass_filter = filter_func is None or filter_func(context=context, response=response)
                if pass_filter or i == last:
                    # Return the response if it passes the filter or it is the last client
                    response.config_id = i
                    response.pass_filter = pass_filter
                    return response
                continue  # filter is not passed; try the next config
        raise RuntimeError("Should not reach here.")

    @staticmethod
    def _cost_with_customized_price(
        response: BaseClient.BaseClientResponseProtocol, price_1k: Tuple[float, float]
    ) -> None:
        """If a customized cost is passed, overwrite the cost in the response."""
        n_input_tokens = response.usage.prompt_tokens if response.usage is not None else 0  # type: ignore [union-attr]
        n_output_tokens = response.usage.completion_tokens if response.usage is not None else 0  # type: ignore [union-attr]
        if n_output_tokens is None:
            n_output_tokens = 0
        return (n_input_tokens * price_1k[0] + n_output_tokens * price_1k[1]) / 1000

    
    def _update_usage(self, actual_usage, total_usage):
        def update_usage(usage_summary, response_usage):
            # go through RESPONSE_USAGE_KEYS and check that they are in response_usage and if not just return usage_summary
            for key in BaseClient.RESPONSE_USAGE_KEYS:
                if key not in response_usage:
                    return usage_summary

            model = response_usage["model"]
            cost = response_usage["cost"]
            prompt_tokens = response_usage["prompt_tokens"]
            completion_tokens = response_usage["completion_tokens"]
            if completion_tokens is None:
                completion_tokens = 0
            total_tokens = response_usage["total_tokens"]

            if usage_summary is None:
                usage_summary = {"total_cost": cost}
            else:
                usage_summary["total_cost"] += cost

            usage_summary[model] = {
                "cost": usage_summary.get(model, {}).get("cost", 0) + cost,
                "prompt_tokens": usage_summary.get(model, {}).get("prompt_tokens", 0) + prompt_tokens,
                "completion_tokens": usage_summary.get(model, {}).get("completion_tokens", 0) + completion_tokens,
                "total_tokens": usage_summary.get(model, {}).get("total_tokens", 0) + total_tokens,
            }
            return usage_summary

        if total_usage is not None:
            self.total_usage_summary = update_usage(self.total_usage_summary, total_usage)
        if actual_usage is not None:
            self.actual_usage_summary = update_usage(self.actual_usage_summary, actual_usage)

    def print_usage_summary(self, mode: Union[str, List[str]] = ["actual", "total"]) -> None:
        """Print the usage summary."""
        iostream = IOStream.get_default()

        def print_usage(usage_summary: Optional[Dict[str, Any]], usage_type: str = "total") -> None:
            word_from_type = "including" if usage_type == "total" else "excluding"
            if usage_summary is None:
                iostream.print("No actual cost incurred (all completions are using cache).", flush=True)
                return

            iostream.print(f"Usage summary {word_from_type} cached usage: ", flush=True)
            iostream.print(f"Total cost: {round(usage_summary['total_cost'], 5)}", flush=True)
            for model, counts in usage_summary.items():
                if model == "total_cost":
                    continue  #
                iostream.print(
                    f"* Model '{model}': cost: {round(counts['cost'], 5)}, prompt_tokens: {counts['prompt_tokens']}, completion_tokens: {counts['completion_tokens']}, total_tokens: {counts['total_tokens']}",
                    flush=True,
                )

        if self.total_usage_summary is None:
            iostream.print('No usage summary. Please call "create" first.', flush=True)
            return

        if isinstance(mode, list):
            if len(mode) == 0 or len(mode) > 2:
                raise ValueError(f'Invalid mode: {mode}, choose from "actual", "total", ["actual", "total"]')
            if "actual" in mode and "total" in mode:
                mode = "both"
            elif "actual" in mode:
                mode = "actual"
            elif "total" in mode:
                mode = "total"

        iostream.print("-" * 100, flush=True)
        if mode == "both":
            print_usage(self.actual_usage_summary, "actual")
            iostream.print()
            if self.total_usage_summary != self.actual_usage_summary:
                print_usage(self.total_usage_summary, "total")
            else:
                iostream.print(
                    "All completions are non-cached: the total cost with cached completions is the same as actual cost.",
                    flush=True,
                )
        elif mode == "total":
            print_usage(self.total_usage_summary, "total")
        elif mode == "actual":
            print_usage(self.actual_usage_summary, "actual")
        else:
            raise ValueError(f'Invalid mode: {mode}, choose from "actual", "total", ["actual", "total"]')
        iostream.print("-" * 100, flush=True)

    def clear_usage_summary(self) -> None:
        """Clear the usage summary."""
        self.total_usage_summary = None
        self.actual_usage_summary = None

    @classmethod
    def extract_text_or_completion_object(
        cls, response: BaseClient.BaseClientResponseProtocol
    ) -> Union[List[str], List[BaseClient.BaseClientResponseProtocol.Choice.Message]]:
        """Extract the text or ChatCompletion objects from a completion or chat response.

        Args:
            response (ChatCompletion | Completion): The response from openai.

        Returns:
            A list of text, or a list of ChatCompletion objects if function_call/tool_calls are present.
        """
        return response.message_retrieval_function(response)