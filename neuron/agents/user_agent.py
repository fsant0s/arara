from typing import Callable, Dict, List, Literal, Optional, Union

from ..runtime_logging import log_new_agent, logging_enabled
from .conversable_agent import ConversableAgent


class UserAgent(ConversableAgent):

    # Default RecommendationAgent.description values, based on interaction_mode
    DEFAULT_USER_AGENT_DESCRIPTIONS = {
        "DETAILED": "A user who provides detailed descriptions of the items they like, including features such as brand, category, price, intended use, and other specific preferences. This user helps personalize recommendations based on comprehensive information.",
        "BASIC": "A user who provides basic descriptions of the items they like, mentioning only general aspects such as product type and one or two main preferences. This user offers sufficient information for reasonably personalized recommendations.",
        "MINIMAL": "A user who provides minimal descriptions of the items they like, only mentioning the product name or general category. This user allows recommendations based on historical data and previous interactions without many additional details.",
    }

    def __init__(
        self,
        name: str,
        system_message: Optional[Union[str, List]] = "",
        description: Optional[str] = None,
        llm_config: Optional[Union[Dict, Literal[False]]] = None,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            description=(
                description if description is not None else self.DEFAULT_USER_AGENT_DESCRIPTIONS['DETAILED']
            ),
        )

        if logging_enabled():
            log_new_agent(self, locals())