from flask import Blueprint, request, redirect, url_for, render_template, flash
from auth.utils import get_current_user, login_required
import requests
from supabase_rest import supabase_request

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route("/add", methods=["POST"])
@login_required
def add_expense():
    user = get_current_user()
    user_id = user.get("id") if user else None
    if not user_id:
        return "Unauthorized", 401

    date = request.form["date"]
    amount = float(request.form["amount"])
    description = request.form.get("description", "")
    new_category_name = request.form.get("new_category_name", "").strip()
    category_id = request.form.get("category_id")

    if category_id == "new":
        if not new_category_name:
            return "New category name required", 400

        cat_payload = {
            "user_id": user_id,
            "category_name": new_category_name
        }

        try:
            new_cat = supabase_request("POST", "categories", payload=cat_payload)
            category_id = new_cat[0]["category_id"]
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 409:
                existing = supabase_request(
                    "GET",
                    "categories",
                    filters={"user_id": user_id, "category_name": new_category_name}
                )
                if existing and len(existing) > 0:
                    category_id = existing[0]["category_id"]
                else:
                    # Category does not exist despite conflict error — handle gracefully
                    return "Category conflict error, but no existing record found", 500
            else:
                return "Error creating category", 500

    else:
        category_id = int(category_id)

    expense_payload = {
        "user_id": user_id,
        "date": date,
        "amount": amount,
        "category_id": category_id,
        "description": description
    }
    supabase_request("POST", "expenses", payload=expense_payload)

    flash("Expense added successfully", "success")
    return redirect(url_for("expenses.expenses_list"))



@expenses_bp.route("/")
@login_required
def expenses_list():
    user = get_current_user()
    user_id = user.get("id") if user else None
    if not user_id:
        return "Unauthorized", 401

    # Fetch only this user's expenses
    expenses = supabase_request("GET", "expenses", filters={"user_id": user_id})

    # Fetch categories belonging to this user
    categories = supabase_request("GET", "categories", filters={"user_id": user_id})

    # Build a lookup of category_id to category_name
    category_dict = {cat["category_id"]: cat["category_name"] for cat in categories}

    # Annotate each expense with its category name
    for exp in expenses:
        exp["category_name"] = category_dict.get(exp["category_id"], "Unknown")

    return render_template("expenses/expenses_list.html", expenses=expenses, categories=categories)
