"""
Header component for the application.
"""
import streamlit as st

def render_header():
    st.markdown(
        """
        <h1 style='text-align:center'>
            🏦 CredAI - Private Credit Platform
        </h1>
        """,
        unsafe_allow_html=True,
    )