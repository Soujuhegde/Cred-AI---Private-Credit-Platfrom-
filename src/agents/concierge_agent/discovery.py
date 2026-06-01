# Agent discovery — fetches Agent Cards and validates capabilities
import logging
from shared.a2a_client import A2AClient
from shared.config import BORROWER_AGENT_URL, LOAN_AGENT_URL, CREDIT_AGENT_URL

logger = logging.getLogger(__name__)


async def discover_agents() -> dict[str, dict]:
    """
    Discover all registered agents by fetching their Agent Cards.
    Returns a map of agent_id -> card.
    """
    agents = {
        "borrower": A2AClient(BORROWER_AGENT_URL),
        "loan":     A2AClient(LOAN_AGENT_URL),
        "credit":   A2AClient(CREDIT_AGENT_URL),
    }
    cards = {}
    for name, client in agents.items():
        try:
            card = await client.fetch_agent_card()
            cards[name] = card
            logger.info("Discovered agent: %s v%s", card["name"], card["version"])
        except Exception as e:
            logger.error("Failed to discover %s agent: %s", name, e)
            raise RuntimeError(f"Agent discovery failed for '{name}': {e}")
    return cards