"""
Streamlit page for Borrower interface.
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
from utils.validators import validate_borrower

st.set_page_config(
    page_title="CredAI - Borrower Onboarding",
    page_icon="👤",
    layout="wide"
)

# Inject CSS and render header
inject_css()
render_header()

st.subheader("👤 Borrower Onboarding")

# Fetch config from session state
backend_url = st.session_state.get("backend_url", "http://localhost:8000")
api_key = st.session_state.get("api_key", "secret-internal-key")

# We can query borrower agent url (port 8001) or fallback to concierge-derived port
borrower_agent_url = "http://localhost:8001"

st.write("Onboard a new borrower into the system database or load an existing borrower's profile.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Onboard New Borrower")
    with st.form("borrower_onboarding_form"):
        name = st.text_input("Full Name", placeholder="e.g. John Doe")
        email = st.text_input("Email Address", placeholder="e.g. john.doe@example.com")
        annual_income = st.number_input("Annual Income ($)", min_value=0.0, step=5000.0, value=75000.0)
        credit_score = st.slider("Credit Score", min_value=300, max_value=850, value=720)
        employment_status = st.selectbox(
            "Employment Status",
            options=["employed", "self_employed", "unemployed"]
        )
        company_name = st.text_input("Company Name (Optional)", placeholder="e.g. Acme Corp")
        
        submitted = st.form_submit_button("Submit & Save Onboarding")
        
        if submitted:
            errors = validate_borrower(name, email, annual_income)
            if errors:
                for err in errors:
                    st.error(err)
            else:
                borrower_payload = {
                    "name": name,
                    "email": email,
                    "annual_income": annual_income,
                    "credit_score": credit_score,
                    "employment_status": employment_status,
                    "company_name": company_name if company_name else None
                }
                
                # Attempt to register borrower with Borrower Onboarding Agent
                try:
                    res = requests.post(
                        f"{borrower_agent_url}/borrowers",
                        json=borrower_payload,
                        headers={"X-API-Key": api_key}
                    )
                    
                    if res.status_code == 200:
                        borrower_data = res.json() or {}
                        st.session_state["borrower"] = borrower_data
                        st.success(f"Borrower onboarded successfully! Borrower ID: {borrower_data.get('borrower_id')}")
                        st.json(borrower_data)
                    else:
                        st.warning(f"Could not reach Borrower Agent directly ({res.status_code}). Saving to session state locally.")
                        # Local mock ID
                        borrower_payload["borrower_id"] = "LOCAL-TEMP-ID"
                        st.session_state["borrower"] = borrower_payload
                        st.success("Borrower profile saved locally.")
                        st.json(borrower_payload)
                except Exception as e:
                    st.warning(f"Borrower Agent offline: {e}. Saving to session state locally.")
                    borrower_payload["borrower_id"] = "LOCAL-TEMP-ID"
                    st.session_state["borrower"] = borrower_payload
                    st.success("Borrower profile saved locally.")
                    st.json(borrower_payload)

with col2:
    st.markdown("### Retrieve Existing Borrower")
    
    # Quick-load selectbox from local DB
    import sqlite3
    try:
        conn = sqlite3.connect("borrower.db")
        cursor = conn.cursor()
        cursor.execute("SELECT borrower_id, name FROM borrowers ORDER BY created_at DESC")
        existing_borrowers = cursor.fetchall()
        conn.close()
        
        if existing_borrowers:
            options = ["-- Select a Borrower to Load --"] + [f"{name} ({bid})" for bid, name in existing_borrowers]
            selected_option = st.selectbox("⚡ Quick Load Onboarded Borrower:", options=options)
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
                    borrower_data = dict(row) or {}
                    st.session_state["borrower"] = borrower_data
                    st.success(f"Successfully loaded borrower: {borrower_data.get('name')}!")
                    st.rerun()
    except Exception as e:
        st.error(f"Error loading database: {e}")

    st.write("---")
    search_id = st.text_input("Or, enter Borrower ID to search manually:")
    if st.button("Fetch Borrower Profile"):
        if search_id:
            try:
                res = requests.get(
                    f"{borrower_agent_url}/borrowers/{search_id}",
                    headers={"X-API-Key": api_key}
                )
                if res.status_code == 200:
                    borrower_data = res.json() or {}
                    st.session_state["borrower"] = borrower_data
                    st.success("Borrower found and loaded.")
                    st.json(borrower_data)
                else:
                    st.error(f"Borrower not found on server ({res.status_code}).")
            except Exception as e:
                st.error(f"Failed to query Borrower Agent: {e}")
        else:
            st.warning("Please enter a Borrower ID.")

    st.write("---")
    st.markdown("#### Current Loaded Borrower (Session State)")
    if "borrower" in st.session_state:
        st.write(st.session_state["borrower"])
    else:
        st.info("No borrower profile loaded yet. Onboard one or search above.")
