"""
Streamlit page for Admin Event Audit Logs & Database Analytics.
"""
import sys
import sqlite3
from pathlib import Path
import streamlit as st

# Add src/frontend to sys.path so modules can be imported directly
frontend_dir = Path(__file__).resolve().parent.parent
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

from styles.theme import inject_css
from components.header import render_header

st.set_page_config(
    page_title="CredAI - Admin Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Inject CSS and render header
inject_css()
render_header()

st.subheader("🛡️ Multi-Agent Event Audit Logs & Analytics")
st.write("Browse system-wide relational statistics and the append-only multi-agent event audit timeline.")

# ── 1. Relational Metrics & Database Insights ──
borrowers_count = 0
loans_count = 0
events_count = 0
success_evals = 0

# Fetch Statistics from local SQLite DBs
try:
    # Borrowers
    conn = sqlite3.connect("borrower.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM borrowers")
    borrowers_count = cursor.fetchone()[0]
    conn.close()
except:
    pass

try:
    # Loans
    conn = sqlite3.connect("loan.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM loans")
    loans_count = cursor.fetchone()[0]
    conn.close()
except:
    pass

try:
    # Events & Evaluations
    conn = sqlite3.connect("credit_intelligence.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM credit_intelligence_events")
    events_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM credit_intelligence")
    success_evals = cursor.fetchone()[0]
    conn.close()
except:
    pass

# Display premium statistical indicators
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div class="review-card" style="text-align: center; background: #FDFBF7 !important; border: 1px solid #C4B5A5 !important; padding: 20px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #5C3E21; letter-spacing: 0.5px;">ONBOARDED BORROWERS</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #1A1816; margin-top: 10px;">{borrowers_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="review-card" style="text-align: center; background: #FDFBF7 !important; border: 1px solid #C4B5A5 !important; padding: 20px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #5C3E21; letter-spacing: 0.5px;">STRUCTURED LOANS</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #1A1816; margin-top: 10px;">{loans_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="review-card" style="text-align: center; background: #FDFBF7 !important; border: 1px solid #C4B5A5 !important; padding: 20px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #5C3E21; letter-spacing: 0.5px;">SUCCESSFUL MEMOS</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #1A1816; margin-top: 10px;">{success_evals}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f"""
        <div class="review-card" style="text-align: center; background: #FDFBF7 !important; border: 1px solid #C4B5A5 !important; padding: 20px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #5C3E21; letter-spacing: 0.5px;">TOTAL AGENT EVENTS</div>
            <div style="font-size: 2.25rem; font-weight: 800; color: #1A1816; margin-top: 10px;">{events_count}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("---")

tab1, tab2 = st.tabs(["🕒 Multi-Agent Event Timeline", "🗄️ Database Explorer"])

with tab1:
    st.markdown("### 🕒 Relational Event Audit Logs")
    st.write("Browse the absolute, tamper-proof logs generated directly by your autonomous microservice agents during evaluation cycles.")
    
    # Query events from database
    events = []
    try:
        conn = sqlite3.connect("credit_intelligence.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM credit_intelligence_events ORDER BY created_at DESC LIMIT 50")
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        st.error(f"Failed to load audit events: {e}")
        
    if not events:
        st.info("No audit events logged yet. Submit a borrower + loan term sheet to trigger agent activity!")
    else:
        for ev in events:
            # Color-coded badges based on standard CSS
            etype = ev.get("event_type", "CREATED")
            if etype == "CREATED":
                badge_html = '<span class="badge-status badge-approve">CREATED</span>'
            elif etype == "DUPLICATE_SKIPPED":
                badge_html = '<span class="badge-status badge-review">DUPLICATE SKIPPED</span>'
            elif etype == "ERROR":
                badge_html = '<span class="badge-status badge-decline">SYSTEM ERROR</span>'
            elif etype == "RETRY":
                badge_html = '<span class="badge-status" style="background-color: #FFF2D6; color: #784F00; border: 1px solid #FCE4B3; padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">RETRY</span>'
            else:
                badge_html = f'<span class="badge-status" style="background-color: #E2EFE0; color: #1E4620; border: 1px solid #C4DFC0; padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 700;">{etype}</span>'

            # Clean timestamp format
            raw_time = ev.get("created_at", "")
            time_formatted = raw_time.split(".")[0].replace("T", " ") if "T" in raw_time else raw_time
            
            # Format custom timeline card
            st.markdown(
                f"""
                <div style="background: #FDFBF7; border: 1px solid #D5C8B8; border-radius: 8px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 6px rgba(26, 24, 22, 0.02); font-family: 'Inter', sans-serif;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E5DCD0; padding-bottom: 8px; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            {badge_html}
                            <span style="font-weight: 700; color: #5C3E21; font-size: 0.9rem;">Record: {ev.get('record_id', 'N/A')}</span>
                        </div>
                        <span style="font-size: 0.8rem; color: #666; font-weight: 500;">🕒 {time_formatted}</span>
                    </div>
                    <div style="display: flex; gap: 20px; font-size: 0.85rem; color: #4A4540; font-weight: 600; margin-bottom: 6px;">
                        <span>👤 Borrower ID: <code style="background:#E5DCD0; padding:2px 6px; border-radius:4px; font-size:0.8rem;">{ev.get('borrower_id') or 'N/A'}</code></span>
                        <span>📄 Loan ID: <code style="background:#E5DCD0; padding:2px 6px; border-radius:4px; font-size:0.8rem;">{ev.get('loan_id') or 'N/A'}</code></span>
                    </div>
                    <p style="color: #2D2A26; font-size: 0.9rem; line-height: 1.5; margin: 0; font-weight: 500;">
                        📝 {ev.get('message') or 'No details provided.'}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

with tab2:
    st.markdown("### 🗄️ Database Record Viewer")
    st.write("Browse row-by-row tables inside each microservice's independent, federated SQL database.")

    # 1. Borrowers Database Explorer
    st.markdown("#### 👤 Onboarded Borrowers (`borrower.db`)")
    try:
        import pandas as pd
        conn = sqlite3.connect("borrower.db")
        df_borrowers = pd.read_sql_query("SELECT * FROM borrowers ORDER BY created_at DESC", conn)
        conn.close()
        if not df_borrowers.empty:
            st.dataframe(df_borrowers, use_container_width=True)
        else:
            st.info("No borrowers saved in database.")
    except Exception as e:
        st.error(f"Could not load borrowers database: {e}")

    # 2. Loans Database Explorer
    st.markdown("#### 📄 Structured Loans (`loan.db`)")
    try:
        conn = sqlite3.connect("loan.db")
        df_loans = pd.read_sql_query("SELECT * FROM loans ORDER BY created_at DESC", conn)
        conn.close()
        if not df_loans.empty:
            st.dataframe(df_loans, use_container_width=True)
        else:
            st.info("No structured loans saved in database.")
    except Exception as e:
        st.error(f"Could not load loans database: {e}")
