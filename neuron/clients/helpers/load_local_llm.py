import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_local_llm(model_name: str, model_dir: str) -> None:
    """Loads the PyTorch model from the specified path."""
    try:

        # Find all .pt files in the specified directory
        model_files = [f for f in os.listdir(model_dir) if f.endswith(".pt")]
        if not model_files:
            raise FileNotFoundError(f"No .pt files found in directory: {model_dir}")

        model_path = os.path.join(model_dir, model_files[0])

        # Load the tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto")

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.generation_config.pad_token_id = tokenizer.pad_token_id
        model.eval()

        return model, tokenizer
    except Exception as e:
        raise e
