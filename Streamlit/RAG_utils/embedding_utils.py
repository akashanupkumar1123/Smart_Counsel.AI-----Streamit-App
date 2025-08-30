# embedding_utils.py
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import normalize_embeddings

# ---------------------------
# Cache the model to load only once per session
# ---------------------------
@st.cache_resource(show_spinner=False)
def load_model(model_name: str = "all-mpnet-base-v2") -> SentenceTransformer:
    """
    Load SentenceTransformer model and cache it for efficiency.

    Args:
        model_name (str): Name of the sentence-transformers model to load.

    Returns:
        SentenceTransformer: Loaded embedding model.
    """
    return SentenceTransformer(model_name)


# ---------------------------
# Compute embedding with caching
# ---------------------------
@st.cache_data(show_spinner=False)
def get_embedding(text: str, model_name: str = "all-mpnet-base-v2") -> np.ndarray:
    """
    Get vector embedding for input text using cached SentenceTransformer model.

    Args:
        text (str): The input text to embed.
        model_name (str): Model name to match FAISS index dimension.

    Returns:
        np.ndarray: Embedding vector as float32 numpy array.
    """
    model = load_model(model_name)

    # Ensure input is a list
    texts = [text] if isinstance(text, str) else text

    # Compute normalized embeddings
    embedding = model.encode(texts, batch_size=32, normalize_embeddings=True)

    # Return first embedding if single text, else all
    return np.array(embedding[0], dtype=np.float32) if isinstance(text, str) else np.array(embedding, dtype=np.float32)


# ---------------------------
# Standalone test
# ---------------------------
if __name__ == "__main__":
    sample_text = "Top colleges in Bangalore for computer science under 20k rank"

    # Compute embedding
    embedding_vector = get_embedding(sample_text)

    print("✅ Embedding computed successfully!")
    print(f"Embedding shape: {embedding_vector.shape}")
    print(f"First 5 values: {embedding_vector[:5]}")
