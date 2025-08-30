# test_rag_pipeline_colab_style.py
import sys
import os
import numpy as np
import pandas as pd

# ---------------------------
# Add RAG_utils to path
# ---------------------------
CURRENT_DIR = os.path.dirname(__file__)
RAG_UTILS_DIR = os.path.join(CURRENT_DIR, "RAG_utils")
if RAG_UTILS_DIR not in sys.path:
    sys.path.insert(0, RAG_UTILS_DIR)

# ---------------------------
# Imports
# ---------------------------
from embedding_utils import get_embedding
from rag_utils import search_colleges, drill_down_college, rag_index
from llm_utils import generate_answer_openrouter

# ---------------------------
# Load raw CSV for full info (needed for drill-down)
# ---------------------------
RAW_FILE = os.path.join(RAG_UTILS_DIR, "RAG_data", "final_rag.csv")
raw_df = pd.read_csv(RAW_FILE)

# ---------------------------
# Dummy model using embedding_utils
# ---------------------------
class DummyModel:
    def encode(self, texts, **kwargs):
        if isinstance(texts, list):
            return np.array([get_embedding(t) for t in texts], dtype="float32")
        else:
            return np.array([get_embedding(texts)], dtype="float32")

model = DummyModel()

# ---------------------------
# Test query
# ---------------------------
query = "Top CSE colleges in Bangalore under 11000 rank with good placements"
max_rank = 11000
min_package = 5.0
top_k = 20  # retrieve extra for deduplication
print("🔎 Running test for query:", query)

# ---------------------------
# Search FAISS (deduplicated & filtered like Colab)
# ---------------------------
results = search_colleges(
    query,
    model=model,
    index=rag_index,
    df=raw_df,
    top_k=top_k
)

# ---------------------------
# Apply Colab-style filtering
# ---------------------------
results_filtered = results.copy()
results_filtered = results_filtered.merge(
    raw_df[['College','Branch','Cutoff_rank','Avg_Package_LPA']],
    on=['College','Branch'],
    how='left'
)

results_filtered = results_filtered[
    (results_filtered['Cutoff_rank'] <= max_rank) &
    (results_filtered['Avg_Package_LPA'] >= min_package)
]

# Deduplicate by College + Branch keeping lowest distance
results_filtered = results_filtered.sort_values('faiss_dist').drop_duplicates(subset=['College','Branch'], keep='first')

# Pick top results
top_results = results_filtered.head(10)
print(f"✅ FAISS search returned {len(top_results)} colleges (up to top 10 shown):")
for idx, row in top_results.iterrows():
    print(f"{idx+1}. {row['content']} (Distance: {row['faiss_dist']:.4f})")

# ---------------------------
# Drill-down for top colleges
# ---------------------------
print("\n📄 Drill-down for top 5 colleges:")
for i, row in top_results.head(5).iterrows():
    college_name = row['College']
    print(f"\n📊 Drill-down tables for {college_name}:")
    drill_info = drill_down_college(college_name, raw_df)
    for branch, data in drill_info.items():
        print(f"\n🔹 Branch: {branch}")
        print("Cutoff Table:")
        print(data["cutoff"])
        print("Avg Package Table:")
        print(data["package"])

# ---------------------------
# Build context from top filtered results for LLM
# ---------------------------
context_lines = []
for _, row in top_results.iterrows():
    cname = row["College"]
    college_rows = raw_df[raw_df["College"] == cname]
    for _, c_row in college_rows.iterrows():
        line = f"- 🏫 {c_row['College']}, Branch: {c_row['Branch']}, Exam: {c_row['Exam']}, Cutoff: {c_row['Cutoff_rank']}, Avg Package: {c_row['Avg_Package_LPA']:.2f} LPA"
        context_lines.append(line)

context = "\n".join(context_lines)

# ---------------------------
# Generate LLM answer
# ---------------------------
response = generate_answer_openrouter(query, context=context, max_tokens=256)
print("\n💡 LLM response:")
print(response)
