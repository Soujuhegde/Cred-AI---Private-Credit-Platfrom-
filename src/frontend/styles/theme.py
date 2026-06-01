"""
Theme and CSS configuration.
"""
import streamlit as st

def inject_css():

    st.markdown(
        """
        <style>
        /* 1. Global Streamlit Viewport Overrides */
        [data-testid="stAppViewContainer"] {
            background-color: #FAF6F0 !important;
            color: #1A1816 !important;
            font-family: 'Inter', sans-serif;
        }
        
        [data-testid="stHeader"] {
            background-color: #FAF6F0 !important;
        }
        
        [data-testid="stSidebar"] {
            background-color: #F0EAE1 !important;
            border-right: 1px solid #D5C8B8 !important;
        }
        
        /* Streamlit typography overrides */
        h1, h2, h3, h4, h5, h6, p, label, span, div, li {
            color: #1A1816 !important;
        }
        
        /* 2. Premium Earthy Cards */
        .review-card, .agent-card {
            background: #F0EAE1 !important;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #D5C8B8;
            box-shadow: 0 4px 12px rgba(26, 24, 22, 0.04);
            margin-bottom: 16px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .review-card:hover, .agent-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(26, 24, 22, 0.08);
        }
        
        .review-title {
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 12px;
            color: #5C3E21 !important;
            border-bottom: 1px solid #D5C8B8;
            padding-bottom: 6px;
        }
        
        .review-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 0.95rem;
        }
        
        /* 3. High-Contrast Accessible Badges */
        .badge-status {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .badge-approve {
            background-color: #E2EFE0 !important;
            color: #1E4620 !important;
            border: 1px solid #C4DFC0;
        }
        
        .badge-review {
            background-color: #FFF2D6 !important;
            color: #784F00 !important;
            border: 1px solid #FCE4B3;
        }
        
        .badge-decline {
            background-color: #FDE8E8 !important;
            color: #8C1D1D !important;
            border: 1px solid #F8C4C4;
        }
        
        /* 4. Streamlit form control improvements */
        div[data-baseweb="input"],
        div[data-baseweb="select"],
        div[data-baseweb="textarea"] {
            background-color: #FAF6F0 !important;
            border: 1px solid #D5C8B8 !important;
            border-radius: 6px !important;
        }
        
        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="select"]:focus-within,
        div[data-baseweb="textarea"]:focus-within {
            border-color: #5C3E21 !important;
            box-shadow: 0 0 0 2px rgba(92, 62, 33, 0.2) !important;
        }
        
        /* Force correct text and background colors inside HTML inputs/selects */
        input, textarea, select {
            color: #1A1816 !important;
            background-color: #FAF6F0 !important;
        }
        
        /* Style the selectbox value container and its text elements */
        div[data-baseweb="select"] > div {
            background-color: #FAF6F0 !important;
            color: #1A1816 !important;
        }
        
        div[data-baseweb="select"] div,
        div[data-baseweb="select"] span,
        div[data-testid="stSelectbox"] div,
        div[data-testid="stSelectbox"] span {
            color: #1A1816 !important;
            background-color: transparent !important;
        }
        
        /* Select dropdown dropdown menu override */
        div[data-baseweb="menu"], 
        div[data-baseweb="menu"] ul, 
        ul[role="listbox"],
        li[role="option"],
        div[role="option"] {
            background-color: #FAF6F0 !important;
            color: #1A1816 !important;
        }
        
        li[role="option"] *,
        div[role="option"] * {
            color: #1A1816 !important;
            background-color: transparent !important;
        }
        
        li[role="option"]:hover, 
        div[role="option"]:hover, 
        li[role="option"][aria-selected="true"],
        div[role="option"][aria-selected="true"] {
            background-color: #F0EAE1 !important;
            color: #1A1816 !important;
        }
        
        /* 5. Custom & Streamlit Native Button Overrides */
        .custom-btn,
        button[kind="secondary"], 
        button[kind="primary"], 
        button[kind="secondaryFormSubmit"], 
        button[kind="primaryFormSubmit"] {
            background-color: #E5DCD0 !important;
            color: #1A1816 !important;
            border: 1px solid #C4B5A5 !important;
            border-radius: 6px !important;
            padding: 8px 16px !important;
            font-weight: 600 !important;
            cursor: pointer;
            transition: background-color 0.15s ease, border-color 0.15s ease !important;
        }
        
        .custom-btn:hover,
        button[kind="secondary"]:hover, 
        button[kind="primary"]:hover, 
        button[kind="secondaryFormSubmit"]:hover, 
        button[kind="primaryFormSubmit"]:hover {
            background-color: #D8CEBF !important;
            border-color: #B6A695 !important;
            color: #1A1816 !important;
        }
        
        /* 6. Premium Sidebar Navigation Overrides */
        [data-testid="stSidebarNavItems"] {
            padding-top: 20px !important;
            gap: 8px !important;
            display: flex !important;
            flex-direction: column !important;
        }
        
        [data-testid="stSidebarNavItems"] li {
            border-radius: 8px !important;
            overflow: hidden !important;
            margin: 2px 0 !important;
        }
        
        [data-testid="stSidebarNavItems"] a {
            padding: 12px 16px !important;
            font-size: 1.05rem !important;
            font-weight: 500 !important;
            color: #4A4540 !important;
            text-decoration: none !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
            border-radius: 8px !important;
            background-color: transparent !important;
            transition: all 0.2s ease !important;
        }
        
        /* Sidebar Nav Hover State */
        [data-testid="stSidebarNavItems"] a:hover {
            background-color: #FAF6F0 !important;
            color: #5C3E21 !important;
            padding-left: 20px !important;
        }
        
        /* Sidebar Nav Active Page State */
        [data-testid="stSidebarNavItems"] a[aria-current="page"],
        [data-testid="stSidebarNavItems"] a:active {
            background-color: #FAF6F0 !important;
            color: #1A1816 !important;
            font-weight: 700 !important;
            border-left: 4px solid #5C3E21 !important;
            box-shadow: 0 2px 8px rgba(26, 24, 22, 0.04) !important;
        }
        
        /* Style icons inside sidebar links if they exist */
        [data-testid="stSidebarNavItems"] a span {
            color: inherit !important;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )