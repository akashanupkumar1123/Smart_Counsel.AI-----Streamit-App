import streamlit as st
from streamlit_lottie import st_lottie
import json
import os

# === Streamlit Page Config ===
# Sets the title, icon, and layout for the web app
st.set_page_config(
    page_title="Smart Counsel AI",
    layout="wide",
    page_icon="🎓"
)

# === Hide Default Multipage Navigation Sidebar ===
# Removes Streamlit's default navigation sidebar
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# === App Background Styling ===
# Gradient background for the main app
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(120deg, #fceabb, #f8b500, #e97777);
        background-attachment: fixed;
    }
    </style>
""", unsafe_allow_html=True)


# === Utility Function: Load Lottie Animation ===
# Reads and returns a Lottie JSON animation from the given file path
def load_lottie(path: str):
    with open(path, "r") as f:
        return json.load(f)

BASE_DIR = os.path.dirname(__file__)

# === Sidebar Section ===
with st.sidebar:
    # Sidebar Header
    st.markdown("## 🤖 **Smart Counsel AI**")
    st.markdown("*Your all-in-one CET/COMEDK Counseling Assistant*")

    # Load Lottie Animation in Sidebar (Advisor/Guide animation)
    lottie_path = os.path.join(BASE_DIR, "assets", "animations", "advisor.json")
    if os.path.exists(lottie_path):
        st_lottie(load_lottie(lottie_path), height=180)
    else:
        st.warning("⚠️ Missing Lottie animation!")

    # Sidebar Navigation Links
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.page_link("pages/predictor.py", label="🎓 Rank-to-College Predictor")
    st.page_link("pages/explorer.py", label="🏫 College Explorer")
    st.page_link("pages/faq.py", label="💬 GPT - RAG Q&A")
    st.page_link("pages/simulator.py", label="🧑🏽‍💻 Mock Option Entry")


# === Gradient Welcome Header ===
# Animated header with gradient text effect
st.markdown("""
    <style>
    .gradient-text {
        font-size: 3em;
        font-weight: 900;
        background: linear-gradient(to right, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s infinite alternate;
        text-align: center;
    }

    @keyframes pulse {
        0% { letter-spacing: 1px; }
        100% { letter-spacing: 3px; }
    }
    </style>
    <h1 class="gradient-text">👋 Welcome to Smart Counsel AI</h1>
""", unsafe_allow_html=True)

st.markdown("Your trusted guide for **KCET & COMEDK** counseling.")


# === College Map Section ===
# Embeds an interactive HTML map of Karnataka Engineering Colleges
st.subheader("🗺️ Karnataka Engineering Colleges Map")
html_path = os.path.join(BASE_DIR, "assets", "plots", "karnataka_colleges_map.html")
if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    st.components.v1.html(html_content, height=600, scrolling=True)
else:
    st.error("❌ Map file not found: `assets/plots/karnataka_colleges_map.html`")


# === Navigation Cards Section ===
# Quick-access navigation cards to different pages
st.markdown("---")
st.subheader("🔍 What do you want to explore?")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("pages/predictor.py", label="🎯 Rank Predictor", help="Predict colleges based on rank", icon="🎓")

with col2:
    st.page_link("pages/explorer.py", label="🏫 College Explorer", help="Explore cutoffs, fees & placements")

with col3:
    st.page_link("pages/faq.py", label="🤖 GPT - RAG Q&A", help="Chat with GPT about colleges")

with col4:
    st.page_link("pages/simulator.py", label="🧩 Mock Option Entry", help="Try your option entry strategy")


# === Final Note Section ===
# Displays a success message at the end of the homepage
st.markdown("---")
st.success("✅ Use the sidebar or cards above to begin your counseling journey with Smart Counsel AI!")
