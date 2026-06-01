"""
Card component for showing individual agent status.
"""
import streamlit as st

def render_agent_status(
    name,
    card,
    online=True
):

    status = "🟢 Online" if online else "🔴 Offline"

    st.markdown(
        f"""
        ### {name}

        {status}

        {card}
        """
    )