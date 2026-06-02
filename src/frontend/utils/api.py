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

        response = requests.get(
            f"{base_url}/query",
            params={"q": query},
            headers={"X-API-Key": api_key}
        )

        if response.status_code != 200:
            try:
                err_detail = response.json().get("detail")
                if err_detail:
                    return {"error": err_detail}
            except:
                pass
            return {"error": f"Server error (status {response.status_code})"}

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
