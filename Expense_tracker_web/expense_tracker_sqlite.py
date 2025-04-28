
import sqlite3, os
from datetime import datetime
from tabulate import tabulate

class ExpenseTracker:
    

    def __init__(self):
        try:
            self.db_path = "Data.db"
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    amount REAL,
                    category TEXT,
                    note TEXT
                )
            """)
            self.conn.commit()
        except Exception as e:
            print(f"Error Occured: {e}")

    def valid_month(self, month):
        try:
            return datetime.strptime(month, "%Y-%m").strftime("%Y-%m")
        except ValueError:
            print("Invalid month format. Use YYYY-MM.")
            return None

    def valid_date(self, date_str):
        try:
            if date_str:
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
            else:
                return datetime.now().strftime("%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return None

    def add_expense(self):
        try:
            amount = float(input("Enter the amount: "))
            input_date = input("Enter the date (YYYY-MM-DD) or press Enter for today: ")
            date = self.valid_date(input_date)
            if not date:
                return
            category = input("Enter the category: ")
            note = input("Enter a note (optional): ")

            self.cursor.execute("""
                INSERT INTO expenses ( date, amount, category, note)
                VALUES (?, ?, ?, ?)
            """, (date, amount, category, note))
            self.conn.commit()
            print("Expense added successfully.")
        except Exception as e:
            print(f"Error Occured: {e}")

    def view_expenses(self):
        try:
            self.cursor.execute("SELECT amount, date, category, note FROM expenses")
            rows = self.cursor.fetchall()
            headers = [ "Date","Amount","Category", "Note"]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"Error Occured: {e}")

    def filter_expense_by_amount(self):
        amount=float(input("Enter the amount"))
        self.cursor.execute("SELECT amount FROM expenses")
        amount_list=self.cursor.fetchall()
        for i in amount_list:
            if(amount==i):
                self.cursor.execute("SELECT * FROM expenses WHERE amount=i")
                filtered_list=self.cursor.fetchall()
                print(filtered_list)
            else:
                print("No expenses found for this amount")
                print(amount_list)
            

tracker = ExpenseTracker()
tracker.filter_expense_by_amount()

while True:
    print("\n1. Add Expense\n2. View Expenses\n3. Exit")
    choice = input("Choose an option: ")

    if choice == '1':
        tracker.add_expense()
    elif choice == '2':
        tracker.view_expenses()
    elif choice=='3':
        tracker.delete_expenses()
    elif choice == '3':
        break
    else:
        print("Invalid choice.")

        
