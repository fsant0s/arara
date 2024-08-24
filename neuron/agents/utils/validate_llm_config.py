
from ...oai import OpenAIWrapper

def validate_llm_config(self_llm_config, llm_config, default_config):
        
        assert llm_config in (None, False) or isinstance(
            llm_config, dict
        ), "llm_config must be a dict or False or None."
        if llm_config is None:
            llm_config = default_config
        self_llm_config = default_config if llm_config is None else llm_config
        # TODO: more complete validity check
        if self_llm_config in [{}, {"config_list": []}, {"config_list": [{"model": ""}]}]:
            raise ValueError(
                "When using OpenAI or Azure OpenAI endpoints, specify a non-empty 'model' either in 'llm_config' or in each config of 'config_list'."
            )
        return None if self_llm_config is False else OpenAIWrapper(**self_llm_config)