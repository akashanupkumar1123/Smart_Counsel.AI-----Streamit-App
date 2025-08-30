import streamlit as st
import pandas as pd
import os
import plotly.express as px
from pathlib import Path

# === Page Setup ===
st.set_page_config(page_title="🎓 College Predictor", layout="wide", page_icon="🎓")

# === Background Gradient & Title Style ===
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(120deg, #fceabb, #f8b500, #e97777);
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
    }
    .main-title {
        font-size: 2.5em;
        font-weight: 800;
        background: linear-gradient(to right, #2b5876, #4e4376);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 10px;
    }
    .card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.25rem;
        border-radius: 15px;
        margin-bottom: 12px;
        box-shadow: 0 10px 20px rgba(118, 75, 162, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        font-family: 'Segoe UI', sans-serif;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(118, 75, 162, 0.6);
    }
    .progress-bar-container {
        margin-top: 12px;
        background: #e0e0e0;
        border-radius: 9px;
        height: 18px;
        overflow: hidden;
    }
    .progress-fill {
        display: block;
        height: 100%;
        color: #fff;
        font-weight: bold;
        font-size: 12px;
        line-height: 18px;
        text-align: center;
        border-radius: 9px;
    }
    .top-badge {
        background-color: #ffd700;
        color: #000;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 8px;
        margin-left: 8px;
        font-size: 0.9em;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

# === Title ===
st.markdown('<div class="main-title">🎓 Smart College Predictor</div>', unsafe_allow_html=True)
st.markdown("Predict likely colleges for **KCET / COMEDK** based on your rank, category, branch, and historical cutoffs.")

# === Sidebar Filters ===
st.sidebar.header("⚙️ Prediction Settings")
exam_type = st.sidebar.selectbox("📘 Select Exam Type", ["KCET", "COMEDK"])
branches = st.sidebar.multiselect("🧪 Branch", ["CSE", "ISE", "ECE", "EEE", "MECH", "CIVIL", "AIML"], default=None)
categories = st.sidebar.multiselect("🧬 Category / Caste", ["GM", "OBC", "SC", "ST", "1G", "2A", "2B", "3A", "3B", "EWS", "GMK", "HKR", "Tulu", "Christian", "Muslim", "Others"], default=None)
rank = st.sidebar.number_input("🎯 Your Rank", min_value=1, max_value=100000, value=15000)
year_range = st.sidebar.slider("📅 Year Range", 2020, 2025, (2020, 2025))
predict_btn = st.sidebar.button("Predict Colleges")

# === Load CSV ===
data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "merged_cutoffs.csv"))
if not os.path.exists(data_file):
    st.error(f"❌ CSV file not found: {data_file}")
    st.stop()

df = pd.read_csv(data_file)
df = df.rename(columns={
    "College": "college",
    "Branch": "branch",
    "Category": "category",
    "Cutoff_Rank": "cutoff_rank",
    "Exam": "exam",
    "Year": "year",
    "Round": "round"
})

branch_map = {
    "CSE": "Computer Science and Engineering",
    "ISE": "Information Science and Engineering",
    "ECE": "Electronics and Communication Engineering",
    "EEE": "Electrical and Electronics Engineering",
    "MECH": "Mechanical Engineering",
    "CIVIL": "Civil Engineering",
    "AIML": "Artificial Intelligence and Data Science"
}
branch_short_map = {v: k for k, v in branch_map.items()}

# === Show PNG only before Predict is clicked ===
if not predict_btn:
    img_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "plots", "cutoff.png"))
    if os.path.exists(img_file):
        st.image(img_file, use_container_width=True)

# === Filter and display results only after Predict button is clicked ===
if predict_btn:
    filtered_df = df[df["exam"].str.upper() == exam_type.upper()]
    if branches:
        filtered_df = filtered_df[filtered_df["branch"].isin([branch_map.get(b, b) for b in branches])]
    if categories:
        filtered_df = filtered_df[filtered_df["category"].isin(categories)]
    filtered_df = filtered_df[(filtered_df["year"] >= year_range[0]) & (filtered_df["year"] <= year_range[1])]

    # Select up to 2 colleges per year by best cutoff rank
    display_list = []
    for yr in range(year_range[0], year_range[1] + 1):
        year_df = filtered_df[filtered_df['year'] == yr]
        top2 = year_df.nsmallest(2, 'cutoff_rank')
        display_list.append(top2)

    display_df = pd.concat(display_list).reset_index(drop=True)

    top_colleges = display_df['college'].unique()

    st.markdown("---")
    st.subheader("📋 Predicted Colleges")

    if display_df.empty:
        st.warning("⚠️ No colleges match your criteria. Try adjusting your filters.")
    else:
        num_cols = 3
        cols = st.columns(num_cols)

        for idx, row in display_df.iterrows():
            col = cols[idx % num_cols]
            with col:
                diff = abs(rank - row['cutoff_rank'])
                chance = 100 * (1 / (1 + diff / row['cutoff_rank']))  # Chance formula
                chance = max(5, min(100, int(chance)))

                color = "#28a745" if chance >= 80 else "#ffc107" if chance >= 50 else "#dc3545"
                badge = "🏅 Top College" if idx == 0 else ""

                round_display = str(row['round']).replace("Round", "").strip()
                round_label = f"🔄 Round {round_display}" if round_display.isdigit() else f"🔄 {row['round']}"

                branch_short = branch_short_map.get(row['branch'], row['branch'])

                st.markdown(f"""
                <div class="card">
                    <div><strong>{row['college']}</strong> {f'<span class="top-badge">{badge}</span>' if badge else ''}</div>
                    <div style="margin-top:4px; font-size:0.9em;">
                        🛠️ {branch_short} | 🧬 {row['category']} | 📅 {row['year']} | {round_label}
                    </div>
                    <div class="progress-bar-container">
                        <span class="progress-fill" style="width:{chance}%; background:{color};">{chance}% Chance</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"### 📊 Cutoff Rank by Branch for Predicted Colleges ({year_range[0]} - {year_range[1]})")

        # Use display_df for entire selected year range on plot
        if display_df.empty:
            st.warning("⚠️ No data available for plotting.")
        else:
            fig = px.bar(
                display_df,
                x='branch',
                y='cutoff_rank',
                color='college',
                labels={'cutoff_rank': 'Cutoff Rank', 'branch': 'Branch', 'college': 'College'},
                category_orders={"college": top_colleges},
                color_discrete_sequence=px.colors.qualitative.D3,
            )
            fig.update_yaxes(autorange='reversed', range=[25000, 500])
            fig.update_layout(
                template="plotly_white",
                height=550,
                showlegend=True,
                margin=dict(l=60, r=20, t=60, b=60)
            )
            st.plotly_chart(fig, use_container_width=True)

        st.success("✅ Prediction complete! Adjust filters to try different ranks, branches, or categories.")
