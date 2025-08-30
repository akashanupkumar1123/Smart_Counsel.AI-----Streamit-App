import pandas as pd
import numpy as np
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import streamlit as st

from pathlib import Path

# ---------------------------
# Paths
# ---------------------------


# Project root: Streamlit/
ROOT_DIR = Path.cwd()


# RAG_data is inside RAG_utils
DATA_DIR = ROOT_DIR / "RAG_utils" / "RAG_data"

RAG_DF_FILE = DATA_DIR / "final_rag_df.pkl"
RAG_INDEX_FILE = DATA_DIR / "final_rag_index.faiss"
RAW_CSV_FILE = DATA_DIR / "final_rag.csv"



raw_df = pd.read_csv(RAW_CSV_FILE)
# Separate 2024 and 2025 rows
df_2024 = raw_df[raw_df['Year']==2024][['College', 'Branch', 'Avg_Package_LPA']]
df_2025 = raw_df[raw_df['Year']==2025].drop(columns=['Avg_Package_LPA'])

# Merge to copy 2024 Avg_Package_LPA into 2025
raw_df.loc[raw_df['Year']==2025, 'Avg_Package_LPA'] = df_2025.merge(
    df_2024,
    on=['College', 'Branch'],
    how='left'
)['Avg_Package_LPA']



# ---------------------------
# Load main RAG data
# ---------------------------
with open(RAG_DF_FILE, "rb") as f:
    rag_df = pickle.load(f)

rag_index = faiss.read_index(str(RAG_INDEX_FILE))

# Load raw CSV for drill-down (full info)
raw_df = pd.read_csv(RAW_CSV_FILE)

# ---------------------------
# Load college locations (for printing)
# ---------------------------
LOC_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "college_list.csv"
college_loc_df = pd.read_csv(LOC_FILE)
college_loc_map = dict(zip(college_loc_df["Name"], college_loc_df["City"]))

# ---------------------------
# Load & cache SentenceTransformer model
# ---------------------------
@st.cache_resource(show_spinner=False)
def load_model():
    """Load SentenceTransformer model (cached for efficiency)."""
    model = SentenceTransformer("all-mpnet-base-v2")  # high-quality embedding
    return model

# ---------------------------
# FAISS search function with Colab-style filtering & deduplication
# ---------------------------
def search_colleges(query, model, index, df=rag_df, top_k=10, max_rank=None, min_package=None):
    """
    Search colleges using FAISS embeddings.
    Deduplicate based on 'College+Branch' and filter by Cutoff_rank / Avg_Package_LPA.
    Returns top_results DataFrame.
    """
    # Encode query
    query_vec = model.encode([query], normalize_embeddings=True)
    query_vec = np.array(query_vec, dtype=np.float32)

    # Retrieve more than needed for post-filtering
    k = top_k * 3
    distances, indices = index.search(query_vec, k)
    results = df.iloc[indices[0]].copy()
    results["faiss_dist"] = distances[0]

    # ---------------------------
    # Apply numeric filters if provided
    # ---------------------------
    if max_rank is not None:
        results = results[results["Cutoff_rank"] <= max_rank]
    if min_package is not None:
        results = results[results["Avg_Package_LPA"] >= min_package]

    # ---------------------------
    # Deduplicate: keep best match per College+Branch (lowest distance)
    # ---------------------------
    results_filtered = results.sort_values("faiss_dist").drop_duplicates(subset=["College", "Branch"], keep="first")

    # Keep top_k final results
    top_results = results_filtered.head(top_k)

    # Ensure 'content' is present
    if "content" not in top_results.columns:
        top_results["content"] = top_results.apply(
            lambda row: f"{row['College']} | {row['Branch']} | {row['Category']} | Cutoff: {row['Cutoff_rank']} | Exam: {row['Exam']} | Year: {row['Year']} | Avg Package: {row['Avg_Package_LPA']}",
            axis=1
        )

    return top_results[["College", "Branch", "content", "faiss_dist"]].reset_index(drop=True)

# ---------------------------
# Drill-down college info by branch (raw_df)
# ---------------------------
def drill_down_college(college_name, full_df):
    """
    Returns branch-aware drill-down info for a selected college.
    Each branch gets pivot tables for Cutoff and Avg Package per Year and Exam.
    Handles duplicate Year-Exam entries by aggregating.
    """
    df = full_df[full_df["College"] == college_name].copy()
    df["Cutoff_rank"] = df["Cutoff_rank"].round(0).astype(int)
    df["Avg_Package_LPA"] = df["Avg_Package_LPA"].round(2)

    branch_dict = {}
    for branch, branch_df in df.groupby("Branch"):
        pivot_cutoff = branch_df.pivot_table(
            index="Year",
            columns="Exam",
            values="Cutoff_rank",
            aggfunc="min"
        )
        pivot_package = branch_df.pivot_table(
            index="Year",
            columns="Exam",
            values="Avg_Package_LPA",
            aggfunc="mean"
        )
        branch_dict[branch] = {"cutoff": pivot_cutoff, "package": pivot_package}

    return branch_dict

# ---------------------------
# Pretty-print FAISS results with content only
# ---------------------------
def print_college_preview(results):
    for idx, row in results.iterrows():
        rank = idx + 1
        print(f"\n🏫 [{rank}] {row['College']} | {row['Branch']}")
        print(f"📄 Content: {row['content']}")
        print(f"📏 FAISS Distance: {row['faiss_dist']:.4f}")

# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    model = load_model()
    query = "Best colleges for COMPUTER SCIENCE AND ENGINEERING (CSE) under KCET rank 6000"

    top_results = search_colleges(query, model, rag_index, top_k=20, max_rank=6000, min_package=5.0)
    print_college_preview(top_results)

    # Drill-down uses raw CSV for full details
    if not top_results.empty:
        first_college = top_results.iloc[0]["College"]
        drill_info = drill_down_college(first_college, raw_df)
        for branch, data in drill_info.items():
            print(f"\n📊 Drill-down for {first_college} | {branch}")
            print("🔹 Cutoff Table:")
            print(data["cutoff"])
            print("🔹 Avg Package Table:")
            print(data["package"])
