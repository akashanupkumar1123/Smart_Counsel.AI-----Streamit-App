import streamlit as st
import sys
import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from streamlit_lottie import st_lottie
import json
import os
from PIL import Image
import numpy as np
import pandas as pd
from pathlib import Path

# ---------------------------
# Path setup for RAG imports
# ---------------------------
CURRENT_DIR = os.path.dirname(__file__)
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# ---------------------------
# Import RAG & LLM utils
# ---------------------------
from RAG_utils.embedding_utils import get_embedding
from RAG_utils.llm_utils import generate_answer_openrouter
from RAG_utils.rag_utils import search_colleges, drill_down_college, rag_index

# ---------------------------
# Load raw CSV for full info (for context + drill-down)
# ---------------------------
ROOT_DIR = Path.cwd()
RAW_FILE = ROOT_DIR / "RAG_utils" / "RAG_data" / "final_rag.csv"
raw_df = pd.read_csv(RAW_FILE)

# ---------------------------
# DummyModel to wrap embedding
# ---------------------------
class DummyModel:
    def encode(self, texts, **kwargs):
        if isinstance(texts, list):
            return np.array([get_embedding(t) for t in texts], dtype="float32")
        else:
            return np.array([get_embedding(texts)], dtype="float32")

model = DummyModel()

# ---------------------------
# Streamlit Page Setup
# ---------------------------
st.set_page_config(page_title="Smart Q&A", layout="wide", page_icon="💬")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(120deg, #fceabb, #f8b500, #e97777); background-attachment: fixed; font-family: 'Segoe UI', sans-serif; }
    .big-title { font-size: 2.5em; font-weight: 800; background: linear-gradient(to right, #1e3c72, #2a5298); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }
    hr.fancy { border: none; height: 2px; background: linear-gradient(to right, #00c6ff, #0072ff); margin: 2rem 0; }
    .card { background-color: #f0f4f8; padding: 15px; border-radius: 12px; margin-bottom: 12px; box-shadow: 2px 2px 12px rgba(0,0,0,0.1); font-family: 'Segoe UI', sans-serif; font-size: 1.05em; line-height: 1.4em; }
    .smart-answer { background-color: #e0f7fa; padding: 18px; border-radius: 12px; margin-bottom: 12px; box-shadow: 2px 2px 10px rgba(0,0,0,0.15); font-size: 1.1em; line-height: 1.4em; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">💬 Ask Smart Counsel AI</div>', unsafe_allow_html=True)
st.markdown("Ask about **KCET/COMEDK colleges, branches, cutoffs, placements**, and more.")

# ---------------------------
# Load Lottie Animation
# ---------------------------
def load_lottie(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"⚠️ Could not load animation: {e}")
        return None

lottie_path = os.path.join(PARENT_DIR, "assets", "animations", "college.json")
lottie_data = load_lottie(lottie_path)
if lottie_data:
    st_lottie(lottie_data, height=200)

# ---------------------------
# Settings
# ---------------------------
with st.expander("⚙️ Settings"):
    top_k = st.slider("📄 Number of retrieved colleges", 1, 10, 5)
    max_tokens = st.slider("✏️ Max tokens to generate", 32, 512, 256, step=32)
    min_cutoff = st.number_input("📝 Max KCET/COMEDK rank", min_value=1, max_value=30000, value=6000, step=500)
    min_package = st.number_input("💰 Min Avg Package (LPA)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)

# ---------------------------
# User Question Input
# ---------------------------
st.markdown('<hr class="fancy">', unsafe_allow_html=True)
query = st.text_input("🔍 Ask your question (e.g., Best CSE colleges under 10k rank?)")
context = ""
filtered_results = pd.DataFrame()

if query:
    with st.spinner("🤖 Thinking..."):
        try:
            # ---------------------------
            # Step 1: FAISS search (retrieve extra for filtering)
            # ---------------------------
            results = search_colleges(
                query,
                model=model,
                index=rag_index,
                df=raw_df,
                top_k=top_k*2  # retrieve extra to allow filtering
            )

            # ---------------------------
            # Step 2: Merge with cutoff & package info
            # ---------------------------
            filtered_results = results.merge(
                raw_df[['College','Branch','Cutoff_rank','Avg_Package_LPA']],
                on=['College','Branch'],
                how='left'
            )

            # ---------------------------
            # Step 3: Apply user filters
            # ---------------------------
            filtered_results = filtered_results[
                (filtered_results['Cutoff_rank'] <= min_cutoff) &
                (filtered_results['Avg_Package_LPA'] >= min_package)
            ]

            # ---------------------------
            # Step 4: Deduplicate & sort by FAISS distance
            # ---------------------------
            filtered_results = filtered_results.sort_values('faiss_dist').drop_duplicates(subset=['College','Branch'], keep='first')

            # ---------------------------
            # Step 5: Pick top_k results
            # ---------------------------
            filtered_results = filtered_results.head(top_k)

            # ---------------------------
            # Build bullet-point context for LLM from raw_df
            # ---------------------------
            context_lines = []
            college_names = filtered_results['College'].unique()
            context = "\n".join([f"- 🏫 {cname}" for cname in college_names])

            # ---------------------------
            # Generate LLM answer
            # ---------------------------
            if context.strip():
                prompt = f"""
You are a helpful assistant. Based on the context below, answer the question concisely.

Question: {query}

Context:
{context}

Answer precisely, focusing on the most relevant colleges.
"""
                response = generate_answer_openrouter(prompt,context=context, max_tokens=max_tokens)
            else:
                response = "⚠️ No relevant information found."

        except Exception as e:
            response = f"❌ [Error during processing]: {e}"

    # ---------------------------
    # Display Smart Answer
    # ---------------------------
    st.markdown("### ✅ Smart Answer")
    if not context.strip():
        st.warning("⚠️ No relevant information found.")
    else:
        st.markdown(f'<div class="smart-answer">{response}</div>', unsafe_allow_html=True)

    # ---------------------------
    # Drill-down per college
    # ---------------------------
    st.markdown('<hr class="fancy">', unsafe_allow_html=True)
    st.markdown("### 📄 Retrieved Supporting Colleges (Click to expand for details)")
    for _, row in filtered_results.iterrows():
        cname = row['College']
        with st.expander(f"🏫 {cname}"):
            branch_info = drill_down_college(cname, raw_df)
            for branch, data in branch_info.items():
                st.markdown(f"**Branch:** {branch}")
                st.markdown("**Cutoff Table:**")
                st.dataframe(data["cutoff"])
                st.markdown("**Avg Package Table:**")
                st.dataframe(data["package"])

# ---------------------------
# Optional Plot
# ---------------------------
st.markdown('<hr class="fancy">', unsafe_allow_html=True)
st.markdown("### 📊 Placement vs Fee Snapshot")
plot_path = os.path.join(PARENT_DIR, "assets", "plots", "feevpack.png")
if os.path.exists(plot_path):
    st.image(Image.open(plot_path), use_container_width=True, caption="Fees vs Placements - Overview")
else:
    st.warning(f"⚠️ Could not find plot: {plot_path}")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown("✨ Powered by OpenRouter + FAISS | Smart Counsel AI – 2025")
