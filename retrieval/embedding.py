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
        Generate semantic embedding using mean pooling
        """

        # 🔹 Input validation
        if not text or not isinstance(text, str) or not text.strip():
            raise ValueError("Invalid input text for embedding")

        # 🔹 Tokenization
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # 🔹 Model inference
        with torch.no_grad():
            outputs = self.model(**inputs)

        # 🔹 Mean Pooling
        token_embeddings = outputs.last_hidden_state  # (1, seq_len, 768)
        attention_mask = inputs["attention_mask"]

        mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        masked_embeddings = token_embeddings * mask

        sum_embeddings = torch.sum(masked_embeddings, dim=1)
        sum_mask = torch.clamp(mask.sum(dim=1), min=1e-9)

        embedding = (sum_embeddings / sum_mask).cpu().numpy()[0]

        # 🔹 Normalize (important for cosine similarity)
        norm = np.linalg.norm(embedding)
        if norm == 0:
            raise ValueError("Zero norm embedding encountered")

        embedding = embedding / norm

        return embedding