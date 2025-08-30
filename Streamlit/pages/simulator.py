import streamlit as st
import pandas as pd
from PIL import Image
from pathlib import Path
import plotly.express as px

# === Page Setup ===
st.set_page_config(
    page_title="Mock Option Entry",
    layout="wide",
    page_icon="🧑🏽‍💻"
)

# === Global Background Gradient Styling ===
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(120deg, #fceabb, #f8b500, #e97777);
        background-attachment: fixed;
    }
    .main-title {
        font-size: 2.5em;
        font-weight: 800;
        background: linear-gradient(to right, #2b5876, #4e4376);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }
    .chat-bubble {
        background-color: #f3f6fb;
        border-radius: 1rem;
        padding: 1rem;
        box-shadow: 1px 1px 10px rgba(0,0,0,0.05);
        margin: 1rem 0;
        font-size: 1.05rem;
    }
    hr.fancy {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# === Title + Intro ===
st.markdown('<div class="main-title">🧑🏽‍💻 Mock Option Entry Simulator</div>', unsafe_allow_html=True)
st.markdown("Simulate your CET/COMEDK option entry and get a visual estimate of likely allotments based on cutoffs.")

# === Load Cutoffs Data ===
@st.cache_data
def load_cutoffs():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    cutoffs_path = BASE_DIR / "data" / "merged_cutoffs.csv"
    if not cutoffs_path.exists():
        st.error(f"❌ merged_cutoffs.csv not found at: {cutoffs_path}")
        st.stop()
    return pd.read_csv(cutoffs_path)

cutoffs_df = load_cutoffs()

# === Load College Full Names + Shortform + City ===
@st.cache_data
def load_colleges():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    clg_path = BASE_DIR / "data" / "college_list.csv"
    if not clg_path.exists():
        st.error(f"❌ college_list.csv not found at: {clg_path}")
        st.stop()
    return pd.read_csv(clg_path)[['Code', 'Name', 'City']]

college_df = load_colleges()

# === Sidebar Inputs ===
st.sidebar.header("📝 Enter Your Details")
max_rank = int(cutoffs_df['cutoff_rank'].max())
rank = st.sidebar.slider("🎯 Your CET/COMEDK Rank", 1, max_rank, value=15000, step=50)

categories = cutoffs_df['category'].dropna().unique().tolist()
sorted_categories = sorted(categories)
category_options = ["Choose your category"] + sorted_categories
category = st.sidebar.selectbox("🧬 Your Category", options=category_options, index=0)

# Later in code, you can check if category == "Choose your category" to handle no selection


exams = cutoffs_df['exam'].dropna().unique().tolist()
exam = st.sidebar.selectbox("📘 Exam Type", sorted(exams))


# Dummy placeholders for selected_college & selected_branch to avoid NameError
selected_college = None
selected_branch = None

@st.cache_data
def get_mini_plot_data_dynamic(selected_colleges_codes, selected_branches, exam):
    if not selected_colleges_codes or not selected_branches:
        return pd.DataFrame()  # empty if nothing selected
    df = cutoffs_df[
        (cutoffs_df['college'].isin(selected_colleges_codes)) &
        (cutoffs_df['branch'].isin(selected_branches)) &
        (cutoffs_df['exam'] == exam) &
        (cutoffs_df['year'] >= 2020) &
        (cutoffs_df['year'] <= 2025)
    ]
    return df

# These will be updated after dropdowns are selected
selected_college_codes = []
selected_branch_list = []

mini_chart_df = get_mini_plot_data_dynamic(selected_college_codes, selected_branch_list, exam)

if not mini_chart_df.empty:
    fig = px.line(
        mini_chart_df,
        x='year',
        y='cutoff_rank',
        color='college',
        line_dash='branch',
        markers=True,
        labels={'year':'Year','cutoff_rank':'Cutoff Rank'},
        range_y=[1000,10000],
        range_x=[2020,2025]
    )
    fig.update_yaxes(autorange="reversed")
    st.sidebar.plotly_chart(fig, use_container_width=True)


# === Main Page: College & Branch Dropdowns ===
st.markdown('<hr class="fancy">', unsafe_allow_html=True)
st.markdown("### 🎓 Choose Your Preferences")

college_options = [f"{row['Name']} ({row['Code']}) | {row['City']}" for _, row in college_df.iterrows()]
selected_college = st.selectbox("🏫 Preferred College", options=college_options, index=0)

branch_options = cutoffs_df['branch'].dropna().unique().tolist()
selected_branch = st.selectbox("🛠️ Preferred Branch", options=branch_options, index=0)

# Update mini plot selection after dropdowns
selected_college_codes = [selected_college.split('(')[1].split(')')[0]]
selected_branch_list = [selected_branch]
mini_chart_df = get_mini_plot_data_dynamic(selected_college_codes, selected_branch_list, exam)

if not mini_chart_df.empty:
    fig = px.line(
        mini_chart_df,
        x='year',
        y='cutoff_rank',
        color='college',
        line_dash='branch',
        markers=True,
        labels={'year':'Year','cutoff_rank':'Cutoff Rank'},
        range_y=[1000,10000],
        range_x=[2020,2025]
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

# === Pre-filtered Data for Simulation ===
@st.cache_data
def get_filtered_cutoffs(college_code, branch, category, exam):
    return cutoffs_df[
        (cutoffs_df['college'] == college_code) &
        (cutoffs_df['branch'] == branch) &
        (cutoffs_df['category'] == category) &
        (cutoffs_df['exam'] == exam)
    ]

# === Simulation Logic ===
st.markdown('<hr class="fancy">', unsafe_allow_html=True)
if st.button("🚀 Simulate Allotment"):
    st.subheader("📋 Simulation Results")
    st.info("🔍 Here's a **mock allotment result** based on your profile:")

    college_code = selected_college.split('(')[1].split(')')[0]
    filtered = get_filtered_cutoffs(college_code, selected_branch, category, exam)

    if filtered.empty:
        st.warning("⚠️ No colleges match your selection. Try adjusting your filters.")
    else:
        # ✅ Keep only one row per year (best cutoff)
        filtered = filtered.groupby('year', as_index=False).agg({'cutoff_rank':'min'})
        filtered = filtered.sort_values(by='year', ascending=False)

        def calculate_chance(user_rank, cutoff_rank):
            if user_rank <= cutoff_rank:
                return 100
            diff = user_rank - cutoff_rank
            chance = max(0, 100 - (diff / 5000) * 100)
            return int(chance)

        total = len(filtered)
        progress_bar = st.progress(0)

        for idx, (_, row) in enumerate(filtered.iterrows(), start=1):
            cutoff_rank = row['cutoff_rank']
            year = row['year']
            city = college_df[college_df['Code'] == college_code]['City'].values[0]
            college_full = college_df[college_df['Code'] == college_code]['Name'].values[0]

            chance_pct = calculate_chance(rank, cutoff_rank)
            color = "#d4edda" if chance_pct >= 80 else "#fff3cd" if chance_pct >= 50 else "#f8d7da"

            st.markdown(
                f"<div style='background-color:{color}; padding:8px; border-radius:10px; margin-bottom:5px;'>"
                f"🏫 <strong>{college_full} ({college_code})</strong> | 🏙️ {city} | 🛠️ {selected_branch} | 📅 {year} | 🎯 Chance: {chance_pct}%"
                f"</div>",
                unsafe_allow_html=True
            )
            progress_bar.progress(idx / total)

        st.markdown("""
            <div class="chat-bubble">
                📌 This simulation gives only a rough estimate.<br>
                Real allotments depend on official round-wise cutoffs and multiple reservation factors.
            </div>
        """, unsafe_allow_html=True)


# === Footer ===
st.markdown("---")
st.success("✅ You're ready to plan your real-world CET/COMEDK options smartly!")
st.caption("✨ Powered by Smart Counsel AI – 2025 Edition")
