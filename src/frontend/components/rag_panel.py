"""
Panel component for RAG (Retrieval-Augmented Generation) query / response.
"""
import streamlit as st
from utils.api import query_rag

def render_rag_panel(base_url, api_key):

    query = st.text_area(
        "Ask a risk intelligence question"
    )

    if st.button("Search"):

        result = query_rag(
            base_url,
            api_key,
            query
        )

        st.json(result)