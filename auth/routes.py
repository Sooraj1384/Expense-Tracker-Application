# auth/routes.py
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash, get_flashed_messages
import requests
import os
from auth.utils import sync_supabase_user_to_db

auth_bp = Blueprint('auth', __name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_AUTH_URL = f"{SUPABASE_URL}/auth/v1"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            flash("Email and password required", "danger")
            return render_template("auth/register.html")

        response = requests.post(
            f"{SUPABASE_AUTH_URL}/signup",
            json={'email': email, 'password': password},
            headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'}
        )
        if response.status_code in (200, 201):
            flash("Registration successful. Please check your email to confirm your account.", "success")
            return redirect(url_for('auth.login'))
        else:
            error_json = response.json()
            flash(error_json.get('error_description', 'Registration failed'), "danger")
            return render_template("auth/register.html")

    return render_template("auth/register.html")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        get_flashed_messages()


    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            flash("Email and password required", "danger")
            return render_template("auth/login.html")

        response = requests.post(
            f"{SUPABASE_AUTH_URL}/token?grant_type=password",
            json={'email': email, 'password': password},
            headers={'apikey': SUPABASE_KEY, 'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            resp_json = response.json()
            session['access_token'] = resp_json.get('access_token')
            session['refresh_token'] = resp_json.get('refresh_token')
            session['user'] = resp_json.get('user')
            sync_supabase_user_to_db(session.get("user"))
            if session['access_token'] and session['user']:
                # Flash login success message only here
                # flash("successful", "success")
                return redirect(url_for('expenses.expenses_list'))
            else:
                flash("Login failed: Invalid response from server", "danger")
                return render_template("auth/login.html")
        else:
            error_json = response.json()
            flash(error_json.get('error_description', 'Login failed'), "danger")
            return render_template("auth/login.html")

    return render_template("auth/login.html")


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.login'))
