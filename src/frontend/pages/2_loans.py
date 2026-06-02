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
if "borrower" not in st.session_state:
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

borrower = st.session_state["borrower"]

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
                    st.json(response_data)

# Visual helper display (calls user component)
st.write("---")

if "summary" in st.session_state:
    if st.button("➡️ View Credit Memo / Report"):
        st.switch_page("pages/3_credit_report.py")

render_loan_form()
