class ExpenseTracker:
    def __init__(self, db_manager, user_id):
        self.db_manager = db_manager
        self.cursor = db_manager.cursor
        self.user_id = user_id

    def add_expense(self, category, amount, date, description):
        self.cursor.execute('''INSERT INTO expenses (user_id, category, amount, date, description) 
                               VALUES (?, ?, ?, ?, ?)''', 
                               (self.user_id, category, amount, date, description))
        self.db_manager.commit()
        print("Expense added successfully.")

    def view_expenses(self):
        self.cursor.execute("SELECT id, category, amount, date, description FROM expenses WHERE user_id=?", (self.user_id,))
        expenses = self.cursor.fetchall()
        if expenses:
            print("\nYour Expenses:")
            for exp in expenses:
                print(f"ID: {exp[0]}, Category: {exp[1]}, Amount: {exp[2]}, Date: {exp[3]}, Description: {exp[4]}")
        else:
            print("No expenses found.")

    def delete_expense(self, expense_id):
        self.cursor.execute("DELETE FROM expenses WHERE id=? AND user_id=?", (expense_id, self.user_id))
        self.db_manager.commit()
        print("Expense deleted successfully.")

    def update_expense(self, expense_id, category, amount, date, description):
        self.cursor.execute('''UPDATE expenses SET category=?, amount=?, date=?, description=? 
                               WHERE id=? AND user_id=?''', 
                               (category, amount, date, description, expense_id, self.user_id))
        self.db_manager.commit()
        print("Expense updated successfully.")
