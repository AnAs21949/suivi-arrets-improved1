"""
CICOR - Suivi des Arrêts Production
Main Streamlit application entry point.

Run with: streamlit run app.py
"""
import streamlit as st
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import APP_NAME, APP_VERSION
from data.database import init_db, seed_reference_data, DB_PATH

# Initialize database on first run
if not DB_PATH.exists():
    init_db()
    seed_reference_data()

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - WHITE BACKGROUND theme matching CICOR design
st.markdown("""
<style>
    /* Force white background everywhere */
    .stApp {
        background-color: #ffffff !important;
    }
    
    .main {
        background-color: #ffffff !important;
    }
    
    .main .block-container {
        padding-top: 1rem;
        max-width: 1400px;
        background-color: #ffffff !important;
    }
    
    /* Sidebar styling - keep blue gradient */
    [data-testid="stSidebar"] {
        background: rgba(205, 230, 250, 1);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }
    
    [data-testid="stSidebar"] .stSelectbox label {
        color: white !important;
    }
    
    /* MAIN CONTENT - Force dark text on white */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        color: #1a365d !important;
    }
    
    .main p, .main span, .main div, .main label {
        color: #2d3748 !important;
    }
    
    /* Form labels */
    .main .stSelectbox label, .main .stTextInput label, .main .stDateInput label,
    .main .stTimeInput label, .main .stNumberInput label, .main .stTextArea label {
        color: #2d3748 !important;
        font-weight: 600 !important;
    }
    
    /* Selectbox and input styling - light background */
    .main .stSelectbox > div > div,
    .main .stTextInput > div > div > input,
    .main .stNumberInput > div > div > input,
    .main .stTextArea > div > div > textarea {
        background-color: #f7fafc !important;
        color: #1a202c !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* Card-like containers */
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);
        border: none;
        color: white;
    }
    
    /* Form styling */
    .stForm {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: #2d3748 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3182ce !important;
        color: white !important;
    }
    
    /* Success/error messages */
    .success-box {
        padding: 1rem;
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #10b981;
        border-radius: 10px;
        color: #065f46;
    }
    
    .error-box {
        padding: 1rem;
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 1px solid #ef4444;
        border-radius: 10px;
        color: #991b1b;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Improve table readability */
    .dataframe {
        font-size: 0.9rem;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border-radius: 8px;
        font-weight: 600;
        color: #2d3748 !important;
    }
    
    /* Sidebar stats box */
    .sidebar-stats {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    
    .sidebar-stats h4 {
        color: #f6ad55 !important;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-stat-value {
        color: white !important;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .sidebar-stat-label {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h1 style="color: #015DA4; font-size: 2rem; font-weight: 800; margin: 0;">cicor</h1>
    <p style="color: rgba(255,255,255,0.8); font-size: 0.85rem; margin-top: 0.25rem;">Suivi Arrêts Production</p>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Navigation menu
page = st.sidebar.radio(
    "Navigation",
    ["📊 Tableau de bord", "➕ Nouvel arrêt", "📋 Historique", "⚙️ Admin"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# User info in sidebar (simplified - no auth for now)
st.sidebar.markdown("**Utilisateur:**")
if 'current_user' not in st.session_state:
    st.session_state.current_user = "Opérateur"

st.session_state.current_user = st.sidebar.selectbox(
    "Connecté en tant que",
    ["Opérateur", "Superviseur", "Admin"],
    label_visibility="collapsed"
)

# This week stats in sidebar
from data.repository import ArretRepository
from core.calculations import get_current_week, get_week_boundaries
from datetime import date

current_week = get_current_week()
week_start, week_end = get_week_boundaries(current_week)
week_filters = {'date_from': week_start, 'date_to': min(week_end, date.today())}
week_stats = ArretRepository.get_stats(week_filters)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 1rem;">
    <p style="color: #f6ad55; font-size: 0.75rem; margin: 0; font-weight: 600;">↗ Cette semaine</p>
    <div style="display: flex; justify-content: space-between; margin-top: 0.5rem;">
        <div>
            <p style="color: white; font-size: 1.5rem; font-weight: 700; margin: 0;">{week_stats['total_heures']:.1f}h</p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.7rem; margin: 0;">Total arrêts</p>
        </div>
        <div>
            <p style="color: white; font-size: 1.5rem; font-weight: 700; margin: 0;">{week_stats['total_impact']*100:.1f}%</p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.7rem; margin: 0;">Impact</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"<p style='color: rgba(255,255,255,0.5); font-size: 0.75rem; text-align: center; margin-top: 1rem;'>v{APP_VERSION}</p>", unsafe_allow_html=True)

# Route to appropriate page
if page == "➕ Nouvel arrêt":
    from pages.saisie import render_saisie_page
    render_saisie_page()
    
elif page == "📋 Historique":
    from pages.journal import render_journal_page
    render_journal_page()
    
elif page == "📊 Tableau de bord":
    from pages.dashboard import render_dashboard_page
    render_dashboard_page()
    
elif page == "⚙️ Admin":
    from pages.admin import render_admin_page
    render_admin_page()