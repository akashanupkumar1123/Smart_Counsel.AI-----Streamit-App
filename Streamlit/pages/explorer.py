import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import os

# ==============================
# ⚙️ Page Config
# ==============================
st.set_page_config(page_title="🏫 College Explorer", layout="wide")

# ==============================
# 🎨 Global & Custom CSS Styling
# ==============================
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(120deg, #fceabb, #f8b500, #e97777);
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
    }
    .big-title {
        font-size: 2.8em;
        font-weight: 800;
        background: linear-gradient(to right, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .caption {
        font-size: 1.1em;
        font-weight: 500;
        color: #444;
        text-align: center;
        margin-top: 0.5em;
    }
    hr.fancy {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #00c6ff, #0072ff);
        margin: 2rem 0;
    }
    /* Styling for dataframe */
    .dataframe th {
        font-weight: bold !important;
        text-align: center !important;
    }
    .dataframe td {
        padding: 8px !important;
        font-weight: 600 !important;
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================
# 🏷️ Title & Intro
# ==============================
st.markdown('<div class="big-title">🏫 College Explorer</div>', unsafe_allow_html=True)
st.markdown("Explore top colleges in Karnataka based on branch, NIRF rankings, and placements.")

# ==============================
# 📊 Branch Trend Visualization (Image from assets)
# ==============================
st.markdown('<hr class="fancy">', unsafe_allow_html=True)
st.markdown("### 📊 Branch Trend Visualization")

plot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "plots", "trend_branches.png"))

if os.path.exists(plot_path):
    with st.container():
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            image = Image.open(plot_path)
            st.image(image, use_container_width=True)
            st.markdown('<div class="caption">Branch Trend Over the Years</div>', unsafe_allow_html=True)
else:
    st.warning(f"❌ Plot not found: {plot_path}")

# ==============================
# 📂 Load Placement & Cutoff Data
# ==============================
@st.cache_data
def load_datasets():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    placements_path = os.path.join(base_dir, "placements.csv")
    cutoffs_path = os.path.join(base_dir, "merged_cutoffs.csv")

    for path in [placements_path, cutoffs_path]:
        if not os.path.exists(path):
            st.error(f"❌ Required file not found: {path}")
            st.stop()

    df_placements = pd.read_csv(placements_path)
    df_cutoffs = pd.read_csv(cutoffs_path)

    # Rename columns for consistency
    df_placements.rename(columns={"College": "college"}, inplace=True)

    # Clean essential columns
    df_placements = df_placements.dropna(subset=["college", "Branch"])
    df_cutoffs = df_cutoffs.dropna(subset=["college", "branch"])

    return df_placements, df_cutoffs

df_placements, df_cutoffs = load_datasets()

# ==============================
# Hardcoded college to city and full name mappings
# ==============================
COLLEGE_CITY_MAP = {
    'RVCE': 'Bangalore',
    'BMSCE': 'Bangalore',
    'MSRIT': 'Bangalore',
    'DSCE': 'Bangalore',
    'PESU': 'Bangalore',
    'UVCE': 'Bangalore',
    'BIT': 'Bangalore',
    'KLEIT': 'Hubli',
    'MVJCE': 'Bangalore',
    'SIT': 'Tumkur',
    'JSSSTU': 'Mysore',
    'NIE': 'Mysore',
    'NHCE': 'Bangalore',
    'NMIT': 'Bangalore',
    'BNMIT': 'Bangalore',
    'BMSIT': 'Bangalore',
    'REVA': 'Bangalore',
    'MSRUAS': 'Bangalore',
    'PESCE': 'Mandya',
    'PRES': 'Bangalore',
    'DSATM': 'Bangalore',
    'RVUNIV': 'Bangalore',
    'SDMCET': 'Dharwad',
    'VVCE': 'Mysore',
    'CMRIT': 'Bangalore',
    'SJBIT': 'Bangalore',
    'AIT': 'Bangalore',
    'GIT': 'Ramohalli',
    'RNSIT': 'Bangalore',
    'AEC': 'Bangalore',
    'NCET': 'Mangalore',
    'SJBCE': 'Mangalore',
    'AECMandya': 'Mandya',
    'CITGubbi': 'Tumkur',
    'GMIT': 'Hubli',
    'BMIT': 'Ballari',
    'KSIT': 'Bangalore',
    'YKCE': 'Moodbidri',
    'RIT': 'Bangalore',
    'SCEM': 'Chikmagalur',
    'JNNCE': 'Shimoga',
    'SITM': 'Mangalore',
    'ACU': 'Bangalore',
    'VVIT': 'Bangalore',
    'BITM': 'Bagalkot',
    'JIT': 'Davangere',
    'DBIT': 'Bangalore',
    'VemanaIT': 'Bangalore',
    'AITM': 'Mandya',
    'VIT': 'Mysore',
    'HKBK': 'Bangalore',
    'DrAIT': 'Bangalore',
    'RAIT': 'Bangalore',
    'EastPoint': 'Bangalore',
    'VSM': 'Hubli',
    'SDMIT': 'Dharmasthala',
    'KLSGIT': 'Belgaum',
}

COLLEGE_FULLNAME_MAP = {
    'RVCE': 'R V College of Engineering',
    'BMSCE': 'B M S College of Engineering',
    'MSRIT': 'M S Ramaiah Institute of Technology',
    'DSCE': 'Dayananda Sagar College of Engineering',
    'PESU': 'PES University',
    'UVCE': 'University Visvesvaraya College of Engineering',
    'BIT': 'Bangalore Institute of Technology',
    'KLEIT': 'K L E Institute of Technology',
    'MVJCE': 'M V J College of Engineering',
    'SIT': 'Siddaganga Institute of Technology',
    'JSSSTU': 'JSS Science & Technology University',
    'NIE': 'National Institute of Engineering',
    'NHCE': 'New Horizon College of Engineering',
    'NMIT': 'Nitte Meenakshi Institute of Technology',
    'BNMIT': 'B N M Institute of Technology',
    'BMSIT': 'B M S Institute of Technology & Management',
    'REVA': 'REVA University',
    'MSRUAS': 'MS Ramaiah University of Applied Sciences',
    'PESCE': 'P E S College of Engineering',
    'PRES': 'Presidency University',
    'DSATM': 'Dayananda Sagar Academy of Technology & Management',
    'RVUNIV': 'R V University',
    'SDMCET': 'Sri Dharmasthala Manjunatheshwara College of Engineering',
    'VVCE': 'Vidyavardhaka College of Engineering',
    'CMRIT': 'CMR Institute of Technology',
    'SJBIT': 'S J B Institute of Technology',
    'AIT': 'Dr Ambedkar Institute of Technology',
    'GIT': 'Global Institute of Technology',
    'RNSIT': 'R V Narsimha Institute of Technology',
    'AEC': 'Acharya Engineering College',
    'NCET': 'Nitte Composite Engineering College',
    'SJBCE': 'St. Joseph Engineering College',
    'AECMandya': 'Acharya Engineering College, Mandya',
    'CITGubbi': 'CIT Gubbi',
    'GMIT': 'Govt. ML Khalsa Institute of Technology',
    'BMIT': 'Ballari Institute of Technology & Management',
    'KSIT': 'K S Institute of Technology',
    'YKCE': 'Yenepoya College of Engineering',
    'RIT': 'Rajarajeswari Institute of Technology',
    'SCEM': 'St Joseph’s College of Engineering',
    'JNNCE': 'JNN College of Engineering',
    'SITM': 'Sahyadri Institute of Technology & Management',
    'ACU': 'Acharya College of Engineering',
    'VVIT': 'Visvesvaraya Vidyalaya College of Engineering',
    'BITM': 'Basava Institute of Technology & Management',
    'JIT': 'Jain Institute of Technology',
    'DBIT': 'Dudhsagar Business Institute of Technology',
    'VemanaIT': 'Vemana Institute of Technology',
    'AITM': 'Adichunchanagiri Institute of Technology',
    'VIT': 'Vijayanagara Institute of Technology',
    'HKBK': 'H K Bharadwaj College of Engineering',
    'DrAIT': 'Dr Ambedkar Institute of Technology',
    'RAIT': 'Rajarshi College of Engineering',
    'EastPoint': 'East Point College of Engineering & Technology',
    'VSM': 'Vidya Vikas Institute of Technology',
    'SDMIT': 'SDM Institute of Technology',
    'KLSGIT': 'KLS Gogte Institute of Technology',
}

# Map city in placements dataframe
df_placements['City'] = df_placements['college'].map(COLLEGE_CITY_MAP)

# ==============================
# Branch shortform consistent mapping
# ==============================
branch_short_map = {
    "Computer Science and Engineering": "CSE",
    "Information Science and Engineering": "ISE",
    "Electronics and Communication Engineering": "ECE",
    "Electrical and Electronics Engineering": "EEE",
    "Mechanical Engineering": "MECH",
    "Civil Engineering": "CIVIL",
    "Artificial Intelligence and Data Science": "AIML"
}

df_placements['Branch_Short'] = df_placements['Branch'].map(branch_short_map).fillna(df_placements['Branch'])
df_cutoffs['Branch_Short'] = df_cutoffs['branch'].map(branch_short_map).fillna(df_cutoffs['branch'])

# ==============================
# Sidebar filters (city dropdown with placeholder)
# ==============================
st.markdown('<hr class="fancy">', unsafe_allow_html=True)
st.markdown("### 🧠 Explore Colleges by Filters")

with st.sidebar.expander("🎛️ Filter Colleges", expanded=True):
    cities = sorted(set(COLLEGE_CITY_MAP.values()))
    city_options = ["Choose City"] + cities
    selected_city = st.selectbox("📍 City / District", options=city_options, index=0)

    min_avg_package = st.slider("💰 Minimum Average Package (LPA)", 0.0, 15.0, 4.0, 0.5)
    min_max_package = st.slider("💸 Minimum Maximum Package (LPA)", 0.0, 30.0, 6.0, 0.5)

    min_nirf = st.slider("🏅 Minimum NIRF Rank", 1, 500, 1)
    max_nirf = st.slider("🏅 Maximum NIRF Rank", 1, 500, 100)
    if min_nirf > max_nirf:
        st.sidebar.error("⚠️ Minimum NIRF cannot be greater than maximum NIRF.")

# ==============================
# Branch filter on main page
# ==============================
branches = ["All"] + sorted(df_placements["Branch_Short"].dropna().unique())
selected_branch = st.selectbox("🧪 Branch", branches)

# ==============================
# Apply filters to placement data
# ==============================
filtered_df = df_placements.copy()

if selected_city != "Choose City":
    filtered_df = filtered_df[filtered_df['City'] == selected_city]

if selected_branch != "All":
    filtered_df = filtered_df[filtered_df['Branch_Short'] == selected_branch]

filtered_df = filtered_df[
    (filtered_df["Avg_Package_LPA"] >= min_avg_package) &
    (filtered_df["Max_Package_LPA"] >= min_max_package) &
    (filtered_df["NIRF_Rank"] >= min_nirf) &
    (filtered_df["NIRF_Rank"] <= max_nirf)
]

# ==============================
# Add badges (highlights)
# ==============================
def add_badges(row):
    badges = []
    if row["NIRF_Rank"] <= 100:
        badges.append("🥇 Top Ranked")
    if row["Avg_Package_LPA"] >= 6:
        badges.append("🧑‍💼 Great Placements")
    return " | ".join(badges)

if not filtered_df.empty:
    filtered_df["Highlights"] = filtered_df.apply(add_badges, axis=1)

    def format_package(val):
        return f"{val:.2f} LPA"

    display_df = filtered_df[[
        "college", "Branch_Short", "Avg_Package_LPA", "Max_Package_LPA", "NIRF_Rank", "City", "Highlights"
    ]].copy()

    display_df["Avg_Package_LPA"] = display_df["Avg_Package_LPA"].apply(format_package)
    display_df["Max_Package_LPA"] = display_df["Max_Package_LPA"].apply(format_package)

    st.success(f"🎯 Found {len(display_df)} matching colleges")
    styled_df = display_df.style.set_table_styles([
        {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]},
        {'selector': 'td', 'props': [('padding', '8px'), ('font-weight', '600'), ('text-align', 'center')]}
    ])
    st.write(styled_df, unsafe_allow_html=True)

    # ==============================
    # Show full college names below the table in bold
    # ==============================
    unique_colleges = filtered_df['college'].unique()
    st.markdown("---")
    st.markdown("### 🏫 College Names and Cities")
    for code in unique_colleges:
        full_name = COLLEGE_FULLNAME_MAP.get(code, "Unknown College Name")
        city = COLLEGE_CITY_MAP.get(code, "Unknown City")
        st.markdown(f"**{code} - {full_name} ({city})**")

    # ==============================
    # Cutoff Rank Trends Visualization (No filters)
    # ==============================
    st.markdown('<hr class="fancy">', unsafe_allow_html=True)
    st.markdown("### 📈 Cutoff Rank Trends")

    df_cutoff_filtered = df_cutoffs.copy()

    # Apply city filter to cutoff data if city selected
    if selected_city != "Choose City":
        df_cutoff_filtered['City'] = df_cutoff_filtered['college'].map(COLLEGE_CITY_MAP)
        df_cutoff_filtered = df_cutoff_filtered[df_cutoff_filtered['City'] == selected_city]

    # Branch filter for cutoff data
    if selected_branch != "All":
        df_cutoff_filtered = df_cutoff_filtered[df_cutoff_filtered['Branch_Short'] == selected_branch]

    if df_cutoff_filtered.empty:
        st.warning("⚠️ No cutoff data available for selected filters.")
    else:
        fig = px.line(df_cutoff_filtered,
                      x='year',
                      y='cutoff_rank',
                      color='college',
                      line_dash='Branch_Short',
                      labels={"year": "Year", "cutoff_rank": "Cutoff Rank", "college": "College", "Branch_Short": "Branch"},
                      title="Cutoff Rank Trends Over Years")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # Placement Package Trends (No year filter)
    # ==============================
    st.markdown('<hr class="fancy">', unsafe_allow_html=True)
    st.markdown("### 📊 Placement Package Trends")

    agg_placements = filtered_df.groupby(['Branch_Short'], as_index=False).agg({
        'Avg_Package_LPA': 'mean',
        'Max_Package_LPA': 'mean'
    })

    if agg_placements.empty:
        st.warning("⚠️ No placement data available for selected filters.")
    else:
        fig2 = px.bar(agg_placements, x='Branch_Short', y='Avg_Package_LPA', color='Branch_Short',
                      labels={"Avg_Package_LPA": "Average Package (LPA)", "Branch_Short": "Branch"},
                      title="Average Placement Package by Branch")
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("❗ No colleges match your filters. Try adjusting the criteria.")

# ==============================
# 📌 Footer
# ==============================
st.markdown("---")
st.markdown("✨ Designed for Smart Counsel AI – 2025")
