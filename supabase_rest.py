import os
import requests
from flask import session

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # anon/public key

def supabase_request(method, table, payload=None, filters=None):
    access_token = session.get("access_token")
    if not access_token:
        raise Exception("User not authenticated")

    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    params = {}
    if filters:
        for key, value in filters.items():
            params[key] = f"eq.{value}"

    response = requests.request(method, url, headers=headers, json=payload, params=params)
    response.raise_for_status()
    return response.json()
