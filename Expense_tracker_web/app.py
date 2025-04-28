from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_connection():
    conn = sqlite3.connect('data/expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_connection()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    conn.close()
    return render_template('expense_tracker.html', expenses=expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    date = request.form['date']
    amount = request.form['amount']
    category = request.form['category']
    note = request.form['note']

    conn = get_connection()
    conn.execute(
        "INSERT INTO expenses (date, amount, category, note) VALUES (?, ?, ?, ?)",
        (date, amount, category, note)
    )
    conn.commit()
    conn.close()

    return redirect('/')
