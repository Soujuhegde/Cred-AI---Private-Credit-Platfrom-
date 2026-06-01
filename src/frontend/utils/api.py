"""
API client and integration helper utilities.
"""
import requests

def submit_application(
    base_url,
    api_key,
    borrower,
    loan
):

    try:

        response = requests.post(
            f"{base_url}/applications",
            json={
                "borrower": borrower,
                "loan": loan
            },
            headers={
                "X-API-Key": api_key
            }
        )

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def query_rag(
    base_url,
    api_key,
    query
):

    try:

        response = requests.post(
            f"{base_url}/query",
            json={"query": query},
            headers={"X-API-Key": api_key}
        )

        return response.json()

    except Exception as e:
        return {"error": str(e)}


def fetch_agent_cards(
    base_url,
    api_key
):

    try:

        response = requests.get(
            f"{base_url}/agents",
            headers={"X-API-Key": api_key}
        )

        return response.json()

    except Exception:
        return {}
