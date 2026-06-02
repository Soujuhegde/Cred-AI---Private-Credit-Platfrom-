"""
Streamlit page for Loan details and application review.
"""
import sys
from pathlib import Path
import streamlit as st
import requests

# Add src/frontend to sys.path so modules can be imported directly
frontend_dir = Path(__file__).resolve().parent.parent
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

from styles.theme import inject_css
from components.header import render_header
from components.loan_form import render_loan_form
from utils.validators import validate_loan
from utils.api import submit_application

st.set_page_config(
    page_title="CredAI - Loan Application",
    page_icon="📄",
    layout="wide"
)

# Inject CSS and render header
inject_css()
render_header()

st.subheader("📄 Loan Application Structuring & Submission")

# Fetch config from session state
backend_url = st.session_state.get("backend_url", "http://localhost:8000")
api_key = st.session_state.get("api_key", "secret-internal-key")

# Verify borrower profile is loaded
if "borrower" not in st.session_state or st.session_state["borrower"] is None:
    st.warning("⚠️ No active borrower profile loaded in this session.")
    
    # Quick-load selectbox from local DB
    import sqlite3
    try:
        conn = sqlite3.connect("borrower.db")
        cursor = conn.cursor()
        cursor.execute("SELECT borrower_id, name FROM borrowers ORDER BY created_at DESC")
        existing_borrowers = cursor.fetchall()
        conn.close()
        
        if existing_borrowers:
            st.markdown("### ⚡ Quick Load Existing Borrower")
            options = ["-- Select a Borrower to Load --"] + [f"{name} ({bid})" for bid, name in existing_borrowers]
            selected_option = st.selectbox("Select a borrower from the database to continue:", options=options)
            if selected_option != "-- Select a Borrower to Load --":
                selected_bid = selected_option.split("(")[-1].replace(")", "").strip()
                # Fetch details from SQLite
                conn = sqlite3.connect("borrower.db")
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM borrowers WHERE borrower_id = ?", (selected_bid,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    st.session_state["borrower"] = dict(row)
                    st.success(f"Successfully loaded borrower: {row['name']}! Page unlocked.")
                    st.rerun()
    except Exception as e:
        st.error(f"Error loading database: {e}")
        
    st.info("Or, go to the onboarding page to create a new profile:")
    if st.button("Go to Onboarding"):
        st.switch_page("pages/1_borrower.py")
    st.stop()

borrower = st.session_state.get("borrower") or {}

st.info(f"Loaded Borrower: **{borrower.get('name')}** (ID: `{borrower.get('borrower_id')}`)")

# Form layout
with st.form("loan_structuring_form"):
    loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, max_value=50000000.0, step=10000.0, value=250000.0)
    loan_term_months = st.number_input("Loan Term (Months)", min_value=3, max_value=360, step=1, value=60)
    purpose = st.selectbox(
        "Purpose of Loan",
        options=["working_capital", "acquisition", "real_estate", "equipment_purchase", "refinancing"]
    )
    collateral_type = st.selectbox(
        "Collateral Type",
        options=["real_estate", "equipment", "receivables", "cash_deposit", "unsecured"]
    )
    collateral_value = st.number_input("Collateral Value ($)", min_value=0.0, step=10000.0, value=300000.0)

    submitted = st.form_submit_button("Submit Application for Orchestrator Evaluation")

    if submitted:
        errors = validate_loan(loan_amount, loan_term_months)
        if errors:
            for err in errors:
                st.error(err)
        else:
            loan_payload = {
                "borrower_id": borrower.get("borrower_id", "TEMP-ID"),
                "loan_amount": loan_amount,
                "loan_term_months": int(loan_term_months),
                "purpose": purpose,
                "collateral_type": collateral_type if collateral_type != "unsecured" else None,
                "collateral_value": collateral_value if collateral_type != "unsecured" else None
            }
            
            with st.spinner("Processing federated multi-agent credit intelligence..."):
                # Call submit_application API helper
                response_data = submit_application(backend_url, api_key, borrower, loan_payload)
                
                # Check for 404/failure fallback to /process
                if "error" in response_data or response_data.get("detail") == "Not Found" or not response_data:
                    try:
                        # Fallback to direct Concierge workflow endpoint
                        fallback_response = requests.post(
                            f"{backend_url}/process",
                            json={
                                "borrower": borrower,
                                "loan": loan_payload
                            },
                            headers={"X-API-Key": api_key}
                        )
                        if fallback_response.status_code == 200:
                            response_data = fallback_response.json()
                        else:
                            response_data = {"error": f"Orchestrator failed with status {fallback_response.status_code}: {fallback_response.text}"}
                    except Exception as ex:
                        response_data = {"error": f"Direct process fallback failed: {ex}"}
                
                if "error" in response_data:
                    st.error(response_data["error"])
                else:
                    st.session_state["summary"] = response_data
                    st.success("Evaluation complete! Credit Committee report generated.")
                    
                    # Display Visual Risk Envelope Maps
                    loan_info = response_data.get("loan") or {}
                    ltv = loan_info.get("ltv_ratio")
                    dsr = loan_info.get("debt_service_ratio")
                    
                    if ltv is not None and dsr is not None:
                        # LTV variables
                        ltv_pct = ltv * 100
                        ltv_color = "#28A745" if ltv <= 0.75 else "#DC3545"
                        ltv_desc = "✅ Collateral backing is safe (LTV is under the maximum 75% threshold)." if ltv <= 0.75 else "⚠️ Collateral backing is insufficient (LTV exceeds the 75% limit)."
                        
                        # DSR variables
                        dsr_pct = dsr * 100
                        if dsr <= 0.35:
                            dsr_color = "#28A745" # Safe Green
                            dsr_desc = "✅ Excellent debt coverage (Monthly payments are well below 35% of monthly income)."
                        elif dsr <= 0.45:
                            dsr_color = "#FFC107" # Warning Yellow
                            dsr_desc = "⚠️ Moderate debt coverage (Payments are between 35% and 45% of income. Acceptable but tight)."
                        else:
                            dsr_color = "#DC3545" # Danger Red
                            dsr_desc = "❌ High debt coverage warning (Payments exceed the maximum 45% DSR limit)."
                            
                        st.markdown(f"""<div style="background: #FAF3E6; border: 1px solid #C4B5A5; border-radius: 12px; padding: 20px; margin-top: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.02); font-family: 'Inter', sans-serif;">
<h4 style="color: #5C3E21; margin-top: 0; border-bottom: 1px solid #C4B5A5; padding-bottom: 8px; font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">
    📊 Real-time Risk Envelope Maps
</h4>

<!-- LTV Progress Bar -->
<div style="margin-bottom: 20px;">
    <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 0.95rem; color: #1A1816;">
        <span>Loan-to-Value (LTV) Ratio</span>
        <span style="color: {ltv_color};">{ltv_pct:.1f}% / 75.0% Max</span>
    </div>
    <div style="background: #E5DCD0; border-radius: 6px; height: 12px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid #C4B5A5;">
        <div style="background: {ltv_color}; height: 100%; width: {min(ltv_pct, 100.0)}%;"></div>
    </div>
    <div style="font-size: 0.85rem; color: #555; margin-top: 6px;">{ltv_desc}</div>
</div>

<!-- DSR Progress Bar -->
<div>
    <div style="display: flex; justify-content: space-between; font-weight: 600; font-size: 0.95rem; color: #1A1816;">
        <span>Debt-Service Ratio (DSR)</span>
        <span style="color: {dsr_color};">{dsr_pct:.1f}% / 45.0% Max</span>
    </div>
    <div style="background: #E5DCD0; border-radius: 6px; height: 12px; width: 100%; margin-top: 8px; overflow: hidden; border: 1px solid #C4B5A5;">
        <div style="background: {dsr_color}; height: 100%; width: {min(dsr_pct, 100.0)}%;"></div>
    </div>
    <div style="font-size: 0.85rem; color: #555; margin-top: 6px;">{dsr_desc}</div>
</div>
</div>""", unsafe_allow_html=True)

# Visual helper display (calls user component)
st.write("---")

if "summary" in st.session_state:
    if st.button("➡️ View Credit Memo / Report"):
        st.switch_page("pages/3_credit_report.py")
