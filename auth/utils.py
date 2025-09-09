from flask import session, redirect, url_for
from functools import wraps

def get_current_user():
    return session.get("user")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function
