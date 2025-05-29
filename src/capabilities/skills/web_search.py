# Ensure the 'tavily-python' library is installed: pip install tavily-python

from typing import List, Union, Dict, Any, Optional
from .skill import Skill
from agents import BaseAgent
import os

try:
    from tavily import TavilyClient
except ImportError:
    # This allows the module to be imported, but WebSearch instantiation will fail
    # if 'tavily-python' is not installed.
    TavilyClient = None

class WebSearch(Skill):
    """
    A skill that enables an agent to perform web searches using the Tavily API
    and incorporate the results into its context.
    """

    def __init__(
        self,
        tavily_api_key: str = None,
        max_results_per_query: int = 3,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_images: bool = False,
    ) -> None:
        """
        Initializes the WebSearch skill.

        Args:
            tavily_api_key (str): The API key for Tavily.
            max_results_per_query (int): Maximum number of search results per query. Defaults to 3.
            search_depth (str): Search depth, "basic" or "advanced". Defaults to "basic".
            include_domains (Optional[List[str]]): A list of domains to specifically include.
            exclude_domains (Optional[List[str]]): A list of domains to specifically exclude.
            include_answer (bool): Whether to include a summarized answer from Tavily. Defaults to False.
            include_raw_content (bool): Whether to include raw content snippets. Defaults to False.
            include_images (bool): Whether to include image search results. Defaults to False.

        Raises:
            ImportError: If the 'tavily-python' library is not installed.
            ValueError: If inputs are invalid (e.g., empty API key, invalid query types).
            RuntimeError: If the TavilyClient fails to initialize.
        """
        super().__init__()

        if TavilyClient is None:
            raise ImportError(
                "TavilyClient could not be imported. "
                "Please install the 'tavily-python' library (e.g., pip install tavily-python)."
            )

        # --- API Key Handling ---
        resolved_api_key = tavily_api_key
        if resolved_api_key is None:
            resolved_api_key = os.getenv("TAVILY_API_KEY")
        if not resolved_api_key or not isinstance(resolved_api_key, str):
            raise ValueError(
                "Tavily API key must be provided either as a parameter or "
                "set in the TAVILY_API_KEY environment variable. It must be a non-empty string."
            )
        self._tavily_api_key = resolved_api_key
        # --- End API Key Handling ---

        if not isinstance(max_results_per_query, int) or max_results_per_query <= 0:
            raise ValueError("'max_results_per_query' must be a positive integer.")
        self._max_results_per_query = max_results_per_query

        if search_depth not in ["basic", "advanced"]:
            raise ValueError("'search_depth' must be either 'basic' or 'advanced'.")
        self._search_depth = search_depth

        if include_domains is not None and not (
            isinstance(include_domains, list) and all(isinstance(d, str) for d in include_domains)
        ):
            raise TypeError("'include_domains' must be a list of strings or None.")
        self._include_domains = include_domains

        if exclude_domains is not None and not (
            isinstance(exclude_domains, list) and all(isinstance(d, str) for d in exclude_domains)
        ):
            raise TypeError("'exclude_domains' must be a list of strings or None.")
        self._exclude_domains = exclude_domains

        self._include_answer = bool(include_answer)
        self._include_raw_content = bool(include_raw_content)
        self._include_images = bool(include_images)

        try:
            self._tavily_client = TavilyClient(api_key=self._tavily_api_key)
        except Exception as e:
            # Catch potential errors from TavilyClient instantiation (e.g., invalid API key format)
            raise RuntimeError(f"Failed to initialize TavilyClient: {e}")


    def on_add_to_agent(self, agent: BaseAgent) -> None:
        """
        Registers this skill's search functionality with the agent.
        It hooks into the agent's message processing lifecycle to add search results.

        Args:
            agent (BaseAgent): The agent to which this skill is being added.
        """
        if not isinstance(agent, BaseAgent): # Redundant if super() checks, but good practice
            raise TypeError(
                f"Expected parameter 'agent' to be of type 'BaseAgent', but got {type(agent).__name__}."
            )

        self._agent.register_hook(
            hookable_method="process_all_messages_before_reply",
            hook=self.perform_search_and_collate_results
        )

    def perform_search_and_collate_results(
        self,
        processed_messages: Union[List[Dict[str, Any]], Dict[str, Any], str]
    ) -> List[Dict[str, Any]]:
        """
        Performs web searches for the configured queries using Tavily API,
        formats the results, and appends them to the processed messages.
        The processed_messages are normalized to a list of message dictionaries.

        Args:
            processed_messages (Union[List[Dict[str, Any]], Dict[str, Any], str]):
                The input message content. Can be a list of message dicts,
                a single message dict, or a string (assumed to be user content).

        Returns:
            List[Dict[str, Any]]: The normalized input messages with Tavily search
                                  results appended as a system message.
        """

        all_query_results_strings = []
        overall_tavily_answer: Optional[str] = None
        max_snippet_length = 250 # Max characters for content snippets

        query = [processed_messages[0]['content']]
        for query_text in query:
            try:
                search_params = {
                    "query": query_text,
                    "search_depth": self._search_depth,
                    "max_results": self._max_results_per_query,
                    "include_domains": self._include_domains,
                    "exclude_domains": self._exclude_domains,
                    "include_answer": self._include_answer,
                    "include_raw_content": self._include_raw_content,
                    "include_images": self._include_images,
                }
                # Filter out None params for cleaner API call
                active_search_params = {k: v for k, v in search_params.items() if v is not None or k in ["include_answer", "include_raw_content", "include_images"]}

                response = self._tavily_client.search(**active_search_params) # type: ignore

                # Capture the main answer if requested and available (only once from the first relevant response)
                if self._include_answer and response.get("answer") and not overall_tavily_answer:
                    overall_tavily_answer = str(response.get("answer",""))

                single_query_formatted_items = [f"Search results for query: '{query_text}'"]

                if response.get("results"):
                    for result_item in response["results"]: # type: ignore
                        formatted_item_parts = []
                        if result_item.get("url"): # Web result
                            formatted_item_parts.append(f"Title: {result_item.get('title', 'N/A')}")
                            formatted_item_parts.append(f"URL: {result_item.get('url', 'N/A')}")
                            content_snippet = str(result_item.get('content', 'N/A'))
                            if len(content_snippet) > max_snippet_length:
                                content_snippet = content_snippet[:max_snippet_length].rstrip() + "..."
                            formatted_item_parts.append(f"Snippet: {content_snippet}")
                            if self._include_raw_content and result_item.get("raw_content"):
                                raw_snippet = str(result_item.get('raw_content', 'N/A'))[:200].rstrip()+"..."
                                formatted_item_parts.append(f"Raw Content Snippet: {raw_snippet}")

                        elif result_item.get("image_url"): # Image result
                            formatted_item_parts.append(f"Image URL: {result_item.get('image_url', 'N/A')}")
                            formatted_item_parts.append(f"Image Source: {result_item.get('source', 'N/A')}")

                        if formatted_item_parts:
                             single_query_formatted_items.append("\n".join(formatted_item_parts))

                if len(single_query_formatted_items) == 1: # Only the "Search results for query..." header
                    single_query_formatted_items.append("No specific items found for this query.")

                all_query_results_strings.append("\n---\n".join(single_query_formatted_items))

            except Exception as e:
                error_message = f"[Error performing Tavily search for '{query_text}': {e}]"
                all_query_results_strings.append(error_message)

        # Collate all results
        collated_detailed_results = "\n\n==========\n\n".join(all_query_results_strings)

        final_content_parts = []
        if overall_tavily_answer:
            final_content_parts.append(f"Tavily Search Summary:\n{overall_tavily_answer}")

        if collated_detailed_results: # Add detailed results if any content was generated
            final_content_parts.append(f"Detailed Search Results:\n{collated_detailed_results}")

        if not final_content_parts:
            final_content = "No information retrieved or generated from Tavily search."
        else:
            final_content = "\n\n".join(final_content_parts)

        system_response_part = [{
            "content": final_content,
            "role": "assistant" # Or "tool_response", "assistant", depending on agent's schema
        }]

        return processed_messages + system_response_part

