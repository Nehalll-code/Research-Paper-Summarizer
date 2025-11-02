"""
Custom UI Components for Streamlit
Beautiful, reusable UI elements with modern styling
"""
import streamlit as st
from datetime import datetime


def load_custom_css():
    """Load custom CSS for beautiful styling."""
    st.markdown("""
    <style>
    /* Main Theme */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #ec4899;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --dark-bg: #0f172a;
        --light-text: #f1f5f9;
    }
    
    /* Global Styles */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f1f5f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main Container */
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        font-size: 2rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(30, 41, 59, 0.5);
        border: 2px solid rgba(99, 102, 241, 0.3);
        color: #f1f5f9;
        padding: 10px 15px;
        border-radius: 6px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Info/Success/Warning/Error Boxes */
    .stAlert {
        background: rgba(30, 41, 59, 0.8);
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border-left-color: #10b981;
    }
    
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border-left-color: #f59e0b;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: #ef4444;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        border-bottom: 2px solid rgba(99, 102, 241, 0.2);
        padding-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        background: transparent;
        border: 2px solid transparent;
        color: #cbd5e1;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        color: #f1f5f9;
        border-color: #6366f1;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border-color: #6366f1;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #6366f1;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.2);
    }
    
    /* Spinners and Loading */
    .stSpinner > div {
        border-top-color: #6366f1;
    }
    
    /* Divider */
    hr {
        border: 1px solid rgba(99, 102, 241, 0.2);
        margin: 2rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #8b5cf6 0%, #a78bfa 100%);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease;
    }
    
    .slide-in {
        animation: slideInLeft 0.5s ease;
    }
    
    .pulse {
        animation: pulse 2s ease infinite;
    }
    
    /* Cards */
    .card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    
    .card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
    }
    
    /* Typography */
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        h1 { font-size: 2rem; }
        h2 { font-size: 1.5rem; }
        .main { padding: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)


def header_with_icon(title, icon, subtitle=""):
    """Create a beautiful header with icon and subtitle."""
    col1, col2 = st.columns([1, 10])
    with col1:
        st.markdown(f"<div style='font-size: 3rem'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem; margin-top: -1rem'>{subtitle}</p>", 
                       unsafe_allow_html=True)


def stat_card(label, value, icon="📊", color="primary"):
    """Create a beautiful stat card."""
    colors = {
        "primary": "#6366f1",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444"
    }
    color_val = colors.get(color, colors["primary"])
    
    st.markdown(f"""
    <div class='metric-card'>
        <div style='display: flex; justify-content: space-between; align-items: center'>
            <div>
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0'>{label}</p>
                <p class='stat-number' style='margin: 0.5rem 0'>{value}</p>
            </div>
            <div style='font-size: 2.5rem'>{icon}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def info_box(title, content, icon="ℹ️", color="primary"):
    """Create a beautiful info box."""
    colors = {
        "primary": "#6366f1",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444"
    }
    color_val = colors.get(color, colors["primary"])
    
    st.markdown(f"""
    <div class='card' style='border-left: 4px solid {color_val}'>
        <p style='color: {color_val}; font-weight: 600; margin: 0 0 0.5rem 0'>{icon} {title}</p>
        <p style='color: #cbd5e1; margin: 0'>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def success_box(title, content, icon="✅"):
    """Create a success box."""
    info_box(title, content, icon, "success")


def warning_box(title, content, icon="⚠️"):
    """Create a warning box."""
    info_box(title, content, icon, "warning")


def error_box(title, content, icon="❌"):
    """Create an error box."""
    info_box(title, content, icon, "danger")


def summary_box(title, summary_text, words):
    """Create a beautiful summary box."""
    st.markdown(f"""
    <div class='card'>
        <p style='font-size: 1.1rem; font-weight: 700; margin: 0 0 1rem 0; color: #6366f1'>{title}</p>
        <p style='color: #cbd5e1; line-height: 1.8; margin: 0'>{summary_text}</p>
        <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(99, 102, 241, 0.2)'>
            <p style='color: #94a3b8; font-size: 0.9rem; margin: 0'>📊 {words} words</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
