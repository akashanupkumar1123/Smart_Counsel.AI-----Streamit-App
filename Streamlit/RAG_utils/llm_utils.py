import os
import requests
from dotenv import load_dotenv
import streamlit as st

# ---------------------------
# Load environment variables
# ---------------------------
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# ---------------------------
# Cached API call wrapper
# ---------------------------
@st.cache_data(show_spinner=False)
def generate_answer_openrouter(
    query: str,
    context: str,
    max_tokens: int = 256,
    model: str = "openai/gpt-4o-mini",
    temperature: float = 0.0,
    top_p: float = 0.8,
) -> str:
    """
    Generate an answer using OpenRouter API with caching to avoid repeated calls.
    
    Args:
        query (str): User's question.
        context (str): Retrieved context from RAG.
        max_tokens (int): Max tokens in response.
        model (str): Model identifier.
        temperature (float): Sampling temperature.
        top_p (float): Nucleus sampling probability.
    
    Returns:
        str: Answer string with emotes or error message.
    """
    if not OPENROUTER_API_KEY:
        return "❌ API key missing! Set OPENROUTER_API_KEY in your .env file."

    if not context.strip():
        return "⚠️ No context available to answer the question."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Answer ONLY using the provided context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}\n\nAnswer:"},
    ]

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }

    try:
        response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()
        return f"💡 Answer:\n{answer}"
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Try again!"
    except requests.exceptions.RequestException as e:
        return f"❌ Request failed: {e}"
    except KeyError:
        return f"⚠️ Unexpected API response: {response.text}"

# ---------------------------
# Optional standalone test
# ---------------------------
if __name__ == "__main__":
    test_context = (
        "🏫 College A: 95% students placed, Avg Package 20 LPA. "
        "🏫 College B: Strong AI research opportunities."
    )
    test_query = "What is the placement percentage of College A?"
    print("🔎 Query:", test_query)
    print("📄 Context:", test_context)
    print("\n--- Answer ---")
    print(generate_answer_openrouter(test_query, test_context))
