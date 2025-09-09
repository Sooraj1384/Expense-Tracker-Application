# budget/routes.py
from flask import Blueprint, render_template
from auth.utils import login_required, get_current_user

budget_bp = Blueprint('budget', __name__)

@budget_bp.route("/budget")
@login_required
def budget_list():
    user = get_current_user()
    # You would fetch budget data related to `user`
    budget_data = {
        "monthly_limit": 50000,
        "spent": 25000,
        "remaining": 25000
    }
    return render_template("budget/budget_list.html", budget=budget_data)
