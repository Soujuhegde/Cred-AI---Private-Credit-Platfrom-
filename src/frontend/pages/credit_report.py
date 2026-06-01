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
        st.switch_page("pages/loans.py")
    st.stop()

summary = st.session_state["summary"]
borrower = summary.get("borrower", {})
loan = summary.get("loan", {})
intel = summary.get("intelligence", {})
final_rec = summary.get("final_recommendation", "REVIEW")
narrative = summary.get("narrative", "")

# Display Recommendation badge
rec_html = render_risk_badge(final_rec)
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom: 20px;">
        <h3>Recommendation Status:</h3>
        {rec_html}
    </div>
    """,
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
            <p style="white-space: pre-wrap; font-size:15px; color:#ddd; line-height:1.6;">
                {narrative}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown("### 🔍 Risk Factors & Market Insights")
    st.markdown("**Identified Risk Factors:**")
    risk_factors = intel.get("risk_factors", [])
    if risk_factors:
        for factor in risk_factors:
            st.markdown(f"- ⚠️ {factor}")
    else:
        st.markdown("- None identified.")
        
    st.markdown("---")
    st.markdown("**Market Insights:**")
    st.write(intel.get("market_insights", "No insights available."))

st.write("---")

# RAG Panel Section
st.markdown("### 🕵️ Risk Intelligence RAG Query Panel")
render_rag_panel(backend_url, api_key)
