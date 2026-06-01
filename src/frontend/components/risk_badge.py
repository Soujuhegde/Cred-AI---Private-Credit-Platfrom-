"""
Component for displaying risk status badges.
"""
def render_risk_badge(status):

    status_classes = {
        "APPROVE": "badge-approve",
        "REVIEW": "badge-review",
        "DECLINE": "badge-decline"
    }

    cls = status_classes.get(status, "")

    if cls:
        return f"""
        <span class="badge-status {cls}">
            {status}
        </span>
        """
    else:
        return f"""
        <span class="badge-status" style="background-color: #FAF6F0; color: #1A1816; border: 1px solid #D5C8B8;">
            {status}
        </span>
        """