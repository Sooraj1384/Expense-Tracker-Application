from flask import Flask, request, render_template, redirect, url_for
import psycopg2

from config import Config

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(Config.DATABASE_URL)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            expense_id SERIAL PRIMARY KEY,
            date TEXT,
            amount REAL,
            category TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_db()


def add_expense(date, amount, category, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (date, amount, category, description)
        VALUES (%s, %s, %s, %s)
    ''', (date, amount, category, description))
    conn.commit()
    conn.close()


# Get all expenses
def get_expenses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()
    conn.close()
    return expenses


# Update an expense
def update_expense(expense_id, date, amount, category, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE expenses
        SET date = %s, amount = %s, category = %s, description = %s
        WHERE expense_id = %s
    ''', (date, amount, category, description, expense_id))
    conn.commit()
    conn.close()


# Delete an expense
def delete_expense(expense_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE expense_id = %s', (expense_id,))
    conn.commit()
    conn.close()


# Calculate total expenses
def calculate_total_expenses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM expenses')
    total = cursor.fetchone()[0]
    conn.close()
    return total if total is not None else 0


@app.route('/')
def index():
    expenses = get_expenses()
    total_expenses = calculate_total_expenses()
    return render_template('index.html', expenses=expenses, total_expenses=total_expenses)


# Add, update, delete, and other route handlers...
@app.route('/add', methods=['POST'])
def add():
    date = request.form['date']
    amount = float(request.form['amount'])
    category = request.form['category']
    description = request.form['description']
    add_expense(date, amount, category, description)
    return redirect(url_for('index'))


# Route to update an expense
@app.route('/update/<int:expense_id>', methods=['POST'])
def update(expense_id):
    date = request.form['date']
    amount = float(request.form['amount'])
    category = request.form['category']
    description = request.form['description']
    update_expense(expense_id, date, amount, category, description)
    return redirect(url_for('index'))


# Route to delete an expense
@app.route('/delete/<int:expense_id>')
def delete(expense_id):
    delete_expense(expense_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
