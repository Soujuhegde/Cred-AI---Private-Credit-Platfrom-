"""
Streamlit page for Credit Report analysis.
"""
import sys
from pathlib import Path
import streamlit as st

# Add src/frontend to sys.path so modules can be imported directly
frontend_dir = Path(__file__).resolve().parent.parent
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

from styles.theme import inject_css
from components.header import render_header
from components.risk_badge import render_risk_badge
from components.metric_row import render_metric_row
from components.rag_panel import render_rag_panel

st.set_page_config(
    page_title="CredAI - Credit Memo",
    page_icon="📊",
    layout="wide"
)

# Inject CSS and render header
inject_css()
render_header()

st.subheader("📊 Credit Committee Recommendation & Memo")

# Fetch config from session state
backend_url = st.session_state.get("backend_url", "http://localhost:8000")
api_key = st.session_state.get("api_key", "secret-internal-key")

# Check if summary is available
if "summary" not in st.session_state:
    st.info("No credit committee report available. Submit a loan application to evaluate.")
    if st.button("Go to Loan Application"):
        st.switch_page("pages/2_loans.py")
    st.stop()

summary = st.session_state["summary"]
borrower = summary.get("borrower", {})
loan = summary.get("loan", {})
intel = summary.get("intelligence", {})
final_rec = summary.get("final_recommendation", "REVIEW")
narrative = summary.get("narrative", "")

# Display Recommendation badge
rec_html = render_risk_badge(final_rec).strip()
st.markdown(
    f'<div style="display:flex; align-items:center; gap:12px; margin-bottom: 24px;"><h3 style="margin:0;">Recommendation Status:</h3>{rec_html}</div>',
    unsafe_allow_html=True
)

# Structure metrics row
metrics = [
    {"label": "Loan Amount", "value": f"${loan.get('loan_amount', 0.0):,.0f}"},
    {"label": "Term (Months)", "value": str(loan.get("loan_term_months", 0))},
    {"label": "Debt Service Ratio", "value": f"{loan.get('debt_service_ratio', 0.0) * 100:.1f}%"},
    {"label": "Risk Score", "value": f"{intel.get('risk_score', 0.0):.1f}/100"},
    {"label": "Default Probability", "value": f"{intel.get('default_probability', 0.0) * 100:.1f}%"}
]

render_metric_row(metrics)

st.write("---")

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 📝 Credit Committee Narrative")
    st.markdown(
        f"""
        <div class="review-card">
            <div class="review-title">Memo Overview</div>
            <p style="white-space: pre-wrap; font-size: 15px; color: #1A1816; line-height: 1.6; font-family: 'Inter', sans-serif;">
                {narrative}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown("### 🔍 Risk Factors & Market Insights")
    
    # Structure Risk Factors
    risk_factors = intel.get("risk_factors", [])
    risk_html = ""
    if risk_factors:
        for factor in risk_factors:
            clean_factor = str(factor).replace("_", " ").title()
            risk_html += f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; background: rgba(220, 53, 69, 0.08); border-left: 4px solid #DC3545; padding: 10px; border-radius: 4px;"><span style="font-size: 1.1rem; color: #DC3545;">⚠️</span><span style="color: #4A1A1A; font-weight: 500; font-size: 0.95rem;">{clean_factor}</span></div>'
    else:
        risk_html = '<div style="display: flex; align-items: center; gap: 8px; background: rgba(40, 167, 69, 0.08); border-left: 4px solid #28A745; padding: 10px; border-radius: 4px;"><span style="font-size: 1.1rem; color: #28A745;">✅</span><span style="color: #1A3E20; font-weight: 500; font-size: 0.95rem;">No major risk factors flagged. Excellent profile!</span></div>'

    # Structure Market Insights
    insights_text = intel.get("market_insights", "No insights available.")
    insights_html = f'<div style="background: #FAF6F0; border: 1px solid #D5C8B8; border-radius: 8px; padding: 16px; margin-top: 16px; box-shadow: inset 0 1px 3px rgba(0,0,0,0.02);"><div style="color: #5C3E21; font-weight: 700; margin-bottom: 8px; font-size: 1rem; display: flex; align-items: center; gap: 6px;">💡 Market Insights</div><p style="color: #2D2A26; font-size: 0.95rem; line-height: 1.6; margin: 0; white-space: pre-wrap;">{insights_text}</p></div>'

    outer_html = f'<div class="review-card" style="background: #FAF3E6 !important; border: 1px solid #C4B5A5 !important; padding: 20px;"><div class="review-title" style="border-bottom: 1px solid #C4B5A5 !important; margin-bottom: 16px;">Risk & Market Analysis</div><div style="margin-bottom: 16px;"><div style="font-weight: 700; color: #5C3E21; margin-bottom: 8px; font-size: 0.85rem; letter-spacing: 0.5px;">IDENTIFIED RISK FACTORS</div>{risk_html}</div>{insights_html}</div>'

    st.markdown(outer_html, unsafe_allow_html=True)

st.write("---")

# RAG Panel Section
st.markdown("### 🕵️ Risk Intelligence RAG Query Panel")
render_rag_panel(backend_url, api_key)
