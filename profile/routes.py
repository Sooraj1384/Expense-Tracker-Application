# profile/routes.py
from flask import Blueprint, render_template
from auth.utils import login_required, get_current_user

profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/profile")
@login_required
def profile_page():
    user = get_current_user()
    # For example, pass user data to template
    return render_template("profile/profile_page.html", user=user)
