"""
Panel component for RAG (Retrieval-Augmented Generation) query / response.
"""
import streamlit as st
from utils.api import query_rag

from components.risk_badge import render_risk_badge

def render_rag_panel(base_url, api_key):
    # Initialize session state for RAG console
    if "rag_query" not in st.session_state:
        st.session_state["rag_query"] = ""
    if "rag_results" not in st.session_state:
        st.session_state["rag_results"] = None
    if "rag_answer" not in st.session_state:
        st.session_state["rag_answer"] = ""

    # Form to group input and button atomically
    with st.form("rag_search_form"):
        query = st.text_area("Ask a risk intelligence question", value=st.session_state["rag_query"])
        submitted = st.form_submit_button("Search")
        
        if submitted:
            st.session_state["rag_query"] = query
            with st.spinner("Analyzing risk databases..."):
                result = query_rag(base_url, api_key, query)
                
                if "error" in result:
                    st.error(f"Failed to query Risk Intelligence RAG database: {result['error']}")
                    st.session_state["rag_results"] = None
                    st.session_state["rag_answer"] = ""
                elif "detail" in result:
                    st.error(f"Error: {result['detail']}")
                    st.session_state["rag_results"] = None
                    st.session_state["rag_answer"] = ""
                else:
                    st.session_state["rag_results"] = result.get("results", [])
                    st.session_state["rag_answer"] = result.get("answer", "")

    # Always persist and render results if they exist in session state
    if st.session_state["rag_results"] is not None:
        results = st.session_state["rag_results"]
        answer = st.session_state["rag_answer"]
        
        if not results:
            st.info("No matching risk intelligence records found for your query. Try searching for a different borrower name, ID, or loan parameter.")
        else:
            # 1. Grounded Chatbot Response
            st.markdown("### 💬 Risk Assistant Grounded Response")
            st.markdown(f"""<div class="review-card" style="background: #F0EAE1 !important; border: 1px solid #D5C8B8 !important; padding: 24px; border-radius: 12px; margin-bottom: 24px; box-shadow: 0 4px 16px rgba(26,24,22,0.06); font-family: 'Inter', sans-serif;">
<div style="font-size: 1.15rem; font-weight: 700; margin-bottom: 12px; color: #5C3E21 !important; border-bottom: 1px solid #D5C8B8; padding-bottom: 8px; display: flex; align-items: center; gap: 8px;">
    🤖 Risk Analysis Assistant
</div>
<p style="white-space: pre-wrap; font-size: 15px; color: #1A1816; line-height: 1.7; margin: 0; font-weight: 500;">
{answer}
</p>
</div>""", unsafe_allow_html=True)
            
            # 2. Source Documents List
            st.markdown("#### 📚 Reference Sources")
            for idx, item in enumerate(results):
                text = item.get("text", "")
                meta = item.get("metadata") or {}
                distance = item.get("distance", 0.0)
                
                confidence = max(0.0, (1 - distance) * 100)
                
                rec = meta.get("recommendation", "N/A")
                risk_score = meta.get("risk_score", 0.0)
                borrower_id = meta.get("borrower_id", "N/A")
                loan_id = meta.get("loan_id", "N/A")
                
                badge_html = render_risk_badge(rec)
                
                card_html = f"""<div class="review-card" style="background: #FDFBF7 !important; border: 1px solid #C4B5A5 !important; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); font-family: 'Inter', sans-serif;">
<div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E5DCD0; padding-bottom: 10px; margin-bottom: 12px;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="background: #5C3E21; color: #FAF6F0; padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;">SOURCE</span>
        {badge_html}
        <span style="font-weight: 700; color: #5C3E21; font-size: 0.95rem;">Loan ID: <code style="background:#E5DCD0; padding:2px 6px; border-radius:4px; font-size:0.8rem;">{loan_id}</code></span>
    </div>
    <span style="font-size: 0.8rem; color: #666; font-weight: 700;">🎯 {confidence:.1f}% Match Relevance</span>
</div>
<p style="color: #2D2A26; font-size: 0.95rem; line-height: 1.6; margin-top: 0; margin-bottom: 14px; font-weight: 500;">
    {text}
</p>
<div style="display: flex; gap: 20px; font-size: 0.85rem; color: #4A4540; font-weight: 600; border-top: 1px dashed #E5DCD0; padding-top: 8px;">
    <span>👤 Borrower ID: <code style="background:#E5DCD0; padding:2px 6px; border-radius:4px; font-size:0.8rem;">{borrower_id}</code></span>
    <span>📊 Risk Score: <strong style="color: #5C3E21;">{risk_score:.1f}/100</strong></span>
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)