from flask import Flask, render_template
from auth.routes import auth_bp
from expenses.routes import expenses_bp
from budget.routes import budget_bp
from profile.routes import profile_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'your-secret-key'

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(expenses_bp, url_prefix="/expenses")
app.register_blueprint(budget_bp)
app.register_blueprint(profile_bp)

@app.route("/")
def home():
    return render_template("index.html")
