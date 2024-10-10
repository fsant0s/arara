import pandas as pd
import numpy as np
import os

from typing import Dict, Optional, Union, Tuple, List
from neuron.agents.non_llm_agents import RetrieverAgent
from sklearn.metrics.pairwise import cosine_similarity

from ..agent_capability import AgentCapability

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

class DataFrameRetrieverCapability(AgentCapability):
    DEFAULT_DESCRIPTION_PROMPT = "A capability that retrieves and filters data from a pandas DataFrame."

    def __init__(self, 
                 dataset: pd.DataFrame = None, 
                 columns: List[str] = None, #Columns to be embedded
                 config: Dict = None, **kwargs
                 ) -> None:
        super().__init__(**kwargs)
        
        self._dataset = dataset
        self._columns = columns
        self._config = config
        self._model_name = self._config['model']
        self._model_path = self._config['model_dir']
        self._model, self._tokenizer = self._load_model(self._model_path, self._model_name)
        self._prepare_embeddings()

    def _load_model(self, model_dir: str, model_name: str) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Loads the PyTorch model from the specified path."""
        try:
            
            # Find all .pt files in the specified directory
            model_files = [f for f in os.listdir(model_dir) if f.endswith('.pt')]
            if not model_files:
                raise FileNotFoundError(f"No .pt files found in directory: {model_dir}")

            model_path = os.path.join(model_dir, model_files[0])

            # Load the tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name, device_map='auto')

            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model.load_state_dict(torch.load(model_path, map_location=device))
            model.generation_config.pad_token_id = tokenizer.pad_token_id
            model.eval()
            
            return model, tokenizer
        except Exception as e:
            raise e


    def _prepare_embeddings(self):
        """
        Converts each row of the dataset into a text representation and computes embeddings.
        """
        # If 'all' is specified, select all columns; otherwise, check for valid columns
        if self._columns == ['all']:
            valid_columns = self._dataset.columns
        else:
            valid_columns = [col for col in self._columns if col in self._dataset.columns]

        # Ensure there are valid columns to apply the function
        if len(valid_columns) > 0:
            # Apply the function to the existing columns
            self._dataset['text_verbalized'] = self._dataset[valid_columns].apply(self._row_to_text, axis=1)
        else:
            raise ValueError("None of the specified columns are present in the dataset.")

        # Compute embeddings for each text
        self._dataset['embeddings'] = self._dataset['text_verbalized'].apply(self._get_embedding)
        # Optionally, create a separate DataFrame to store embeddings
        self._embeddings_df = self._dataset[['embeddings']].copy()

    def _row_to_text(self, row):
        """
        Converts a DataFrame row into a text string in the format:
        'Column1 is Value1, Column2 is Value2, ...'
        """
        text = ', '.join([f"{row[col]}" for col in row.index if col not in ['text_verbalized', 'embeddings']])
        return text

    def _get_embedding(self, text: str):
        """
        Generates an embedding for the input text using the loaded model.
        """
        if not isinstance(text, str):
            raise ValueError("Input text must be a string.")

        try:
            inputs = self._tokenizer(text, return_tensors="pt")
            reponse = self._model(inputs['input_ids'].clone().detach())
            embeddings = reponse.logits
            reponse = embeddings.mean(dim=1)[0].tolist()
        except Exception as e:
            raise RuntimeError(f"LocalLLM exception occurred: {e}")
        return reponse

    def retrieve_similar(self, content: str, k=3):
        """
        Retrieves the top k most similar rows from the dataset based on the user's input text.
        """
        # Compute embedding for the user-provided text
        
        user_embedding = self._get_embedding(content)
        # Stack embeddings from the dataset
        embeddings = np.stack(self._dataset['embeddings'].values)
        # Compute cosine similarities
        similarities = cosine_similarity([user_embedding], embeddings)[0]
        # Get indices of top k similar embeddings
        top_k_indices = similarities.argsort()[-k:][::-1]
        # Return the corresponding rows from the original dataset (excluding 'text_verbalized' and 'embeddings' columns)
        return self._dataset.iloc[top_k_indices][self._dataset.columns.difference(['text_verbalized', 'embeddings'])]

    def add_to_agent(self, agent: RetrieverAgent) -> None:
        """
        Adds this capability to the specified agent.
        """
        if not isinstance(agent, RetrieverAgent):
            raise TypeError("The provided agent must be a RetrieverAgent.")
        # Update agent's description
        agent.update_description(
            agent.description
            + "\nYou've been given the special ability to perform data retrieval based on embeddings."
        )
        # Register the message processing hook
        agent.register_hook("process_last_received_message", self.process_last_received_message)

    def process_last_received_message(self, content: Union[str, Dict]) -> Optional[Dict]:
        """
        Processes the last message received by the agent.
        """
        if not isinstance(content, str):
            raise ValueError("Content must be a string to perform retrieval.")
        # Retrieve similar rows based on the user's input
        similar_rows = self.retrieve_similar(content)
        # Return the results as a list of dictionaries
        df = pd.DataFrame(similar_rows)
        result = '\n'.join([f"Item {i+1}: {self._row_to_text(row)}" for i, row in df.iterrows()])
        return result
