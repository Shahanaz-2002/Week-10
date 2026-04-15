import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


class BioBERTEmbedding:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BioBERTEmbedding, cls).__new__(cls)

            cls._instance.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )

            cls._instance.MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"

            print("🔄 Loading BioClinicalBERT model... (only once)")

            cls._instance.tokenizer = AutoTokenizer.from_pretrained(
                cls._instance.MODEL_NAME
            )

            cls._instance.model = AutoModel.from_pretrained(
                cls._instance.MODEL_NAME
            )

            cls._instance.model.to(cls._instance.device)
            cls._instance.model.eval()

        return cls._instance

    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding using CLS token (best for sentence representation)
        """

        if not text or not isinstance(text, str) or not text.strip():
            return np.zeros(768)  
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        
        embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]

        return embedding