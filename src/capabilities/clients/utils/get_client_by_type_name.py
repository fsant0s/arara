from capabilities.clients.groq import GroqClient
from capabilities.clients.ollama import OllamaClient
from capabilities.clients.openai import OpenAIClient


def get_client_by_type_name(client_type: str, openai_config: dict) -> object:
    """
    Retrieves a client instance based on the provided type, using lazy loading to optimize resource utilization.

    Args:
        client_type (str): Type of the client to retrieve, should be lowercase.
        openai_config (dict): Configuration parameters for client initialization.

    Returns:
        object: An instance of the requested client, or an error message if the type is unknown.
    """

    def create_client(client_key: str) -> object:
        """
        Lazily instantiates a client based on the client key to ensure that resources are used efficiently.

        Args:
            client_key (str): Key identifying the client type.

        Returns:
            object: Initialized client object, or an error message if the key is unrecognized.
        """
        # Mapping from client keys to their constructor functions
        client_constructors = {
            "groq": GroqClient,
            "openai": OpenAIClient,
            "ollama": OllamaClient,
            "maritaca": OpenAIClient,  # Assuming Maritaca uses the same client as OpenAI
            "openrouter": OpenAIClient,  # Assuming OpenRouter uses the same client as OpenAI
        }

        # Retrieve the appropriate client class from the mapping
        ClientClass = client_constructors.get(client_key)
        if ClientClass is None:
            return "Client type unknown"

        # Instantiate the client with the given configuration
        return ClientClass(**openai_config)

    client_type_normalized = client_type.lower()
    client = create_client(client_type_normalized)

    return client
