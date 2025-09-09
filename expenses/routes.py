from flask import Blueprint, request, redirect, url_for, render_template, flash, session, jsonify, send_file
from auth.utils import get_current_user, login_required
import requests
from supabase_rest import supabase_request
from flask import current_app as app
import traceback
import csv
import io

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route("/add", methods=["POST"])
@login_required
def add_expense():
    try:
        user = get_current_user()
        user_id = user.get("id") if user else None
        app.logger.debug(f"add_expense called with user_id: {user_id}, session_access_token: {session.get('access_token')}")
        app.logger.debug(f"User data: {user}")

        if not user_id:
            flash("Unauthorized access", "danger")
            return "Unauthorized", 401

        date = request.form.get("date")
        amount_str = request.form.get("amount")
        description = request.form.get("description", "").strip()
        new_category_name = request.form.get("new_category_name", "").strip()
        category_id = request.form.get("category_id")

        # Input validation
        if not date:
            flash("Date is required", "danger")
            return redirect(url_for("expenses.expenses_list"))

        if not amount_str:
            flash("Amount is required", "danger")
            return redirect(url_for("expenses.expenses_list"))

        try:
            amount = float(amount_str)
            if amount <= 0:
                flash("Amount must be positive", "danger")
                return redirect(url_for("expenses.expenses_list"))
        except ValueError:
            flash("Invalid amount entered", "danger")
            return redirect(url_for("expenses.expenses_list"))

        if not category_id:
            flash("Please select a category", "danger")
            return redirect(url_for("expenses.expenses_list"))

        # Handle new category creation
        if category_id == "new":
            if not new_category_name:
                flash("New category name is required", "danger")
                return redirect(url_for("expenses.expenses_list"))

            cat_payload = {
                "user_id": user_id,
                "category_name": new_category_name
            }

            try:
                # Adding Prefer header to return created record
                new_cat = supabase_request("POST", "categories", payload=cat_payload,
                                           extra_headers={"Prefer": "return=representation"})
                if isinstance(new_cat, list) and len(new_cat) > 0:
                    category_id = new_cat[0]["category_id"]
                elif isinstance(new_cat, dict) and "category_id" in new_cat:
                    category_id = new_cat["category_id"]
                else:
                    existing = supabase_request(
                        "GET",
                        "categories",
                        filters={"user_id": user_id, "category_name": new_category_name}
                    )
                    if existing and len(existing) > 0:
                        category_id = existing[0]["category_id"]
                    else:
                        flash("Failed to create or retrieve new category", "danger")
                        return redirect(url_for("expenses.expenses_list"))

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
                        flash("Category conflict error, but no existing record found", "danger")
                        return redirect(url_for("expenses.expenses_list"))
                else:
                    error_msg = err.response.text
                    app.logger.error(f"Category creation failed: {error_msg}")
                    flash(f"Error creating category: {error_msg}", "danger")
                    return redirect(url_for("expenses.expenses_list"))

            try:
                category_id = int(category_id)
            except Exception:
                flash("Invalid category ID received", "danger")
                return redirect(url_for("expenses.expenses_list"))

        else:
            try:
                category_id = int(category_id)
            except Exception:
                flash("Invalid category selected", "danger")
                return redirect(url_for("expenses.expenses_list"))

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

    except Exception as e:
        app.logger.error(f"Exception in add_expense: {e}\n{traceback.format_exc()}")
        flash("An error occurred while adding the expense.", "danger")
        return redirect(url_for("expenses.expenses_list"))


@expenses_bp.route("/")
@login_required
def expenses_list():
    try:
        user = get_current_user()
        user_id = user.get("id") if user else None

        if not user_id:
            flash("Unauthorized access", "danger")
            return "Unauthorized", 401

        # Fetch all expenses (no order or limit args in supabase_request)
        expenses = supabase_request("GET", "expenses", filters={"user_id": user_id})

        # Sort expenses by date descending
        expenses_sorted = sorted(expenses, key=lambda x: x["date"], reverse=True)

        # Take latest 5 expenses
        latest_expenses = expenses_sorted[:5]

        categories = supabase_request("GET", "categories", filters={"user_id": user_id})

        category_dict = {cat["category_id"]: cat["category_name"] for cat in categories}

        for exp in latest_expenses:
            exp["category_name"] = category_dict.get(exp["category_id"], "Unknown")

        return render_template("expenses/expenses_list.html", expenses=latest_expenses, categories=categories)

    except Exception as e:
        app.logger.error(f"Exception in expenses_list: {e}\n{traceback.format_exc()}")
        flash("An error occurred while fetching expenses.", "danger")
        return render_template("expenses/expenses_list.html", expenses=[], categories=[])


@expenses_bp.route("/all")
@login_required
def all_expenses():
    user = get_current_user()
    user_id = user.get("id") if user else None

    expenses = supabase_request("GET", "expenses", filters={"user_id": user_id})

    categories = supabase_request("GET", "categories", filters={"user_id": user_id})
    category_dict = {cat["category_id"]: cat["category_name"] for cat in categories}
    for exp in expenses:
        exp["category_name"] = category_dict.get(exp["category_id"], "Unknown")

    return jsonify(expenses)


@expenses_bp.route("/download")
@login_required
def download():
    user = get_current_user()
    user_id = user.get("id") if user else None

    expenses = supabase_request("GET", "expenses", filters={"user_id": user_id})

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Amount', 'Category', 'Description'])

    for exp in expenses:
        writer.writerow([
            exp.get('date', ''),
            exp.get('amount', ''),
            exp.get('category_name', ''),
            exp.get('description', '')
        ])

    output.seek(0)

    return send_file(
        io.BytesIO(output.read().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="expenses.csv"
    )
