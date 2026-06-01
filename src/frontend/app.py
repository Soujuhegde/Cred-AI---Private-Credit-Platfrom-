"""
Main entrypoint for the Private Credit Multi-Agent system frontend.
"""
import sys
from pathlib import Path
import streamlit as st

# Add src/frontend to sys.path so modules can be imported directly
frontend_dir = Path(__file__).resolve().parent
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

from styles.theme import inject_css
from components.header import render_header
from components.agent_card import render_agent_status
from utils.api import fetch_agent_cards

st.set_page_config(
    page_title="CredAI - Private Credit Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS styles
inject_css()

# Render top header
render_header()

# Connection setup in Sidebar
st.sidebar.header("🔌 Connection Configuration")
backend_url = st.sidebar.text_input("Concierge API URL", value="http://localhost:8000")
api_key = st.sidebar.text_input("Internal API Key", value="secret-internal-key", type="password")

# Save config to session state for other pages
st.session_state["backend_url"] = backend_url
st.session_state["api_key"] = api_key

# Home page body
st.write("---")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(
        """
        ### Welcome to CredAI
        This is a federated multi-agent orchestrator dashboard for private credit evaluation and loan origination workflows.
        
        Using this dashboard, you can:
        - **👤 Borrower Profile**: Onboard or simulate new borrower prospects.
        - **📄 Loan Application**: Structure a loan and submit it for real-time orchestrator evaluation.
        - **📊 Credit Intelligence & Report**: Inspect the final recommendation, risk analysis, default probability, and perform semantic RAG search over credit risk databases.
        
        Use the sidebar navigation to visit the respective workspace sections.
        """
    )

with col2:
    st.markdown("#### Discovered Agents")
    
    # Try fetching agent status from concierge
    try:
        agents = fetch_agent_cards(backend_url, api_key)
        if not agents:
            st.warning("No active agents found. Please ensure the concierge orchestrator backend is running.")
        else:
            for agent_id, agent_info in agents.items():
                name = agent_info.get("name", agent_id.replace("_", " ").title())
                description = agent_info.get("description", "No description provided.")
                render_agent_status(name, description, online=True)
    except Exception as e:
        st.error(f"Failed to connect to the backend agent orchestrator: {e}")
        st.info("Tip: Start the backend concierge app on port 8000 using: `uvicorn src.agents.concierge_agent.main:app --port 8000 --reload`")
