# app.py
import os
from flask import Flask
from auth.routes import auth_bp
from expenses.routes import expenses_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') or 'your-secret-key'

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(expenses_bp, url_prefix="/expenses")

@app.route("/")
def home():
    return "Welcome to the Expense Tracker! Please log in or register."

if __name__ == "__main__":
    app.run(debug=True)
