# 🎓 Smart Counsel AI

**Smart Counsel AI** is your all-in-one intelligent college predictor, explorer, and Q&A assistant built specifically for **KCET & COMEDK aspirants** in Karnataka 🇮🇳. It combines the power of **retrieval-augmented generation (RAG)**, data filtering, and an engaging UI to deliver real-time, explainable answers to all your college-related queries.

------------------------------------------------

## 🔥 Features

- 🎓 **College Predictor** – Predict colleges based on your rank and category.
- 🏫 **Explorer** – Filter colleges by branch, placement, NIRF rank, and more.
- 💬 **Smart Q&A** – Ask anything about cutoffs, fees, colleges, and get GPT/FLAN-based answers.
- 🧑‍💻 **Option Entry Simulator** – Practice mock entries with filters and cutoffs.
- 📊 **Visual Insights** – Trends, cutoff snapshots, and placement graphs.
- ✨ **Modern UI** – Responsive design, Lottie animations, gradient themes, and emoji-rich interface.

--------------------------------------------------------------------

## 🚀 Tech Stack

| Layer             | Libraries/Tools                                |
|------------------|-------------------------------------------------|
| Web App          | `Streamlit`, `streamlit-lottie`                 |
| ML/Embedding     | `sentence-transformers`, `MiniLM-L6-v2`         |
| LLM Answering    | `transformers`, `FLAN-T5-base` or `Mistral`     |
| Vector DB        | `FAISS`                                         |
| Backend Tools    | `pandas`, `numpy`, `torch`, `pickle`, `matplotlib` |

--------------------------------------------------------------------

## 📁 Project Structure

Smart_Counsel_AI/
├── app.py # Main Streamlit launcher
├── pages/
│ ├── predictor.py # 🎓 Rank-to-College predictor
│ ├── explorer.py # 🏫 College filter explorer
│ ├── faq.py # 💬 GPT/FLAN Smart Q&A
│ └── simulator.py # 🧑‍💻 Option Entry simulator
├── RAG_utils/
│ ├── rag_utils.py # FAISS retrieval logic
│ └── llm_utils.py # Answer generation using FLAN or Mistral
├── data/
│ ├── cutoff_data/ # KCET/COMEDK 2023 cutoff files
│ ├── colleges.csv # College codes & names
│ ├── placements.csv # Placement/NIRF info
│ ├── seat_matrix.csv # Category-wise seat matrix
│ ├── fees.csv # Fee structure and scholarships
│ └── college_list.csv # Simplified college list
├── assets/
│ ├── animations/ # Lottie JSON animations
│ └── plots/ # PNG/HTML visuals (trend_branches, fee_vs_pack)
└── requirements.txt

----------------------------------------------------------------



---

## 🧠 How RAG Works

1. **Query embedding** via `MiniLM-L6-v2`.
2. **Top 5 chunks** retrieved using `FAISS`.
3. **Context passed** to a local or HuggingFace LLM (e.g., FLAN-T5).
4. **Answer generated** in real-time using `transformers` pipeline.

---

## 🛠️ Installation

### 🔧 1. Clone & Setup
```bash
git clone https://github.com/yourname/Smart_Counsel_AI.git
cd Smart_Counsel_AI
pip install -r requirements.txt
