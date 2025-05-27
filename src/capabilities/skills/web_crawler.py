import requests
from bs4 import BeautifulSoup

from .skill import Skill
from agents.base import BaseAgent
from typing import List, Union


class WebCrawler(Skill):
    """
    An skill that enables a agent to normalize various message types into plain text content.

    This is useful for preparing messages for processing, display, or logging by extracting their semantic content,
    regardless of the original message format (TextMessage, ToolCall, or Response).
    """

    def __init__(self, urls: List[str]) -> None:
        """
        Initialize the skill and bind it to a src.

        Args:
            agent (BaseAgent): The agent to which this skill is attached.
            urls (List[str]): A list of URLs to crawl.
        """
        super().__init__()
        if not isinstance(urls, list):
            raise TypeError(f"Expected 'urls' to be a list, but got {type(urls).__name__}.")

        if not urls:
            raise ValueError("The 'urls' list must not be empty.")

        if not all(isinstance(url, str) and url.strip() for url in urls):
            raise ValueError("Each URL must be a non-empty string.")

        self._urls = urls

    def on_add_to_agent(self, agent: BaseAgent):
        """
        Register this skill as a utility hook.
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(
                f"Expected parameter 'agent' to be of type 'BaseAgent', but got {type(agent).__name__}."
            )
        self._agent.register_hook(hookable_method="process_all_messages_before_reply", hook=self.extract_text_from_url)

    def extract_text_from_url(self, processed_messages: Union[dict, str]) ->  Union[dict, str]:
        """
        Crawl all URLs, extract and clean the textual content, and return it
        concatenated with the input processed messages.

        Args:
            processed_messages (str): The input message content before the web scraping.

        Returns:
            str: The input processed messages followed by the extracted content.
        """
        extracted_contents = []

        for url in self._urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for tag in soup(["script", "style", "noscript"]):
                        tag.decompose()
                    raw_text = soup.get_text(separator="\n")
                    lines = [line.strip() for line in raw_text.splitlines()]
                    cleaned_text = "\n".join(line for line in lines if line)
                    extracted_contents.append(cleaned_text)
                else:
                    extracted_contents.append(f"[Failed to fetch {url}: Status {response.status_code}]")
            except Exception as e:
                extracted_contents.append(f"[Error fetching {url}: {e}]")

        scraped_content = "\n\n".join(extracted_contents)

        system_response = [{
            "content": scraped_content,
            "role": "system"
        }]

        return processed_messages + system_response
