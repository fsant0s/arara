"""
Centralized pricing information for various LLM providers.
Prices are typically per 1,000 tokens (1K) for input and output.
Formato:
PROVIDER_NAME: {
    "model_name_1": (input_cost_per_1k, output_cost_per_1k),
    "model_name_2": (input_cost_per_1k, output_cost_per_1k),
    ...
}

SEE https://github.com/AgentOps-AI/tokencost
"""

import warnings

# Prices per 1M (million) tokens (input, output)
MODEL_PRICING_PER_1K_TOKENS = {
    "groq": {
        "gemma2-9b-it": (0.0002, 0.0002),
        "qwen-2.5-32b": (0.00059, 0.00079),
        "llama-3.3-70b-versatile": (0.00059, 0.00079),
        "llama3-70b-8192": (0.00059, 0.00079),
        "mixtral-8x7b-32768": (0.00024, 0.00024),
        "llama3-8b-8192": (0.00005, 0.00008),
        "gemma-7b-it": (0.00007, 0.00007),
        "llama3-groq-70b-8192-tool-use-preview": (0.00089, 0.00089),
    },
    "openai": {
        # Example of how you would add OpenAI models (fictional values)
        "gpt-4": (0.03, 0.06),
        "gpt-4-0613": (0.03, 0.06),
        "gpt-4o": (0.0025, 0.01),
        "gpt-4o-mini": (0.00015, 0.0006),
        "gpt-4o-mini-2024-07-18": (0.00015, 0.0006),
        "o1-mini": (0.0011, 0.0044),
        "o1-mini-2024-09-12": (0.003, 0.012),
        "chatgpt-4o-latest": (0.005, 0.015),
        "gpt-4.1-2025-04-14": (0.02, 0.08),
        # Add other OpenAI models here
    },
    "ollama": {},
    "maritaca": {
        "sabia-3": (0.00009, 0.00179),
        "sabia-3.1": (0.00009, 0.00179),
    },
    # Add other providers here
    # "anthropic": {
    # "claude-3-opus-20240229": (0.015, 0.075),
    # },
}

# You can also add other types of costs here, if necessary
# For example, costs per image, per minute of audio, etc.
# OTHER_MODEL_PRICING = {
#     "openai": {
#         "dall-e-3": {
#             "standard_1024x1024": 0.040, # per imagem
#         },
#         "tts-1": 0.015, # per 1k
#     }
# }


def calculate_token_cost(
    input_tokens: int, output_tokens: int, provider: str, model_name: str
) -> float | None:
    """
    Calculate the cost of the completion using centralized pricing.

    Args:
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        provider: The name of the provider (e.g., "groq", "openai", "maritaca).
        model_name: The specific model name.

    Returns:
        The calculated cost, or None if pricing information is not available.
    """
    total_cost = 0.0
    provider_pricing = MODEL_PRICING_PER_1K_TOKENS.get(provider.lower())

    if not provider_pricing:
        warnings.warn(
            f"Cost calculation not available for provider '{provider}'. Model: '{model_name}'",
            UserWarning,
        )
        return None

    model_pricing_info = provider_pricing.get(model_name)

    if model_pricing_info:
        input_cost_per_k, output_cost_per_k = model_pricing_info
        input_cost = (input_tokens / 1000) * input_cost_per_k
        output_cost = (output_tokens / 1000) * output_cost_per_k
        total_cost = input_cost + output_cost
        return total_cost
    else:
        # Fallback: tentar encontrar modelo que comece com o nome fornecido
        # Útil para modelos com sufixos de versão/preview que podem não estar listados explicitamente
        # mas compartilham o preço base. Ex: "gpt-4-turbo-preview" usando preços de "gpt-4-turbo"
        for known_model_name, (input_cost_pk, output_cost_pk) in provider_pricing.items():
            if model_name.startswith(known_model_name):
                warnings.warn(
                    f"Exact match for model '{model_name}' not found for provider '{provider}'. "
                    f"Using pricing for base model '{known_model_name}'.",
                    UserWarning,
                )
                input_cost = (input_tokens / 1000) * input_cost_pk
                output_cost = (output_tokens / 1000) * output_cost_pk
                total_cost = input_cost + output_cost
                return total_cost

        warnings.warn(
            f"Cost calculation not available for model '{model_name}' under provider '{provider}'.",
            UserWarning,
        )
        return None
