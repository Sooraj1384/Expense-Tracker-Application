# auth/utils.py
from flask import session, redirect, url_for
from functools import wraps
from supabase_rest import supabase_request
import logging


def get_current_user():
    return session.get("user")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


def sync_supabase_user_to_db(user):
    if not user:
        logging.error("No user data to sync")
        return

    user_id = user.get("id")
    email = user.get("email")
    username = user.get("user_metadata", {}).get("username", "") or ""

    if not user_id or not email:
        logging.error("Missing user ID or email for syncing user")
        return

    user_payload = {
        "id": user_id,
        "email": email,
        "username": username,
        "password_hash": "supabase-auth-managed"
    }
    try:
        supabase_request("POST", "users", payload=user_payload)
    except Exception as e:
        logging.error(f"Failed to sync user {user_id} to DB: {e}")
