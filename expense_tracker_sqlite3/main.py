from database import DatabaseManager
from user import User
from expense_tracker import ExpenseTracker

def main():
    db = DatabaseManager()
    user_system = User(db)

    print("----- Welcome to Expense Tracker -----")

    current_user_id = None
    while not current_user_id:
        choice = input("\n1. Login\n2. Signup\nEnter choice: ")
        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            current_user_id = user_system.login(username, password)
        elif choice == "2":
            username = input("Choose Username: ")
            password = input("Choose Password: ")
            user_system.signup(username, password)
        else:
            print("Invalid choice.")

    expense_tracker = ExpenseTracker(db, current_user_id)

    while True:
        print("\n----- Expense Menu -----")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Update Expense")
        print("4. Delete Expense")
        print("5. Logout")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            category = input("Category: ")
            amount = float(input("Amount: "))
            date = input("Date (YYYY-MM-DD): ")
            description = input("Description: ")
            expense_tracker.add_expense(category, amount, date, description)
        elif choice == "2":
            expense_tracker.view_expenses()
        elif choice == "3":
            expense_id = int(input("Expense ID to update: "))
            category = input("New Category: ")
            amount = float(input("New Amount: "))
            date = input("New Date (YYYY-MM-DD): ")
            description = input("New Description: ")
            expense_tracker.update_expense(expense_id, category, amount, date, description)
        elif choice == "4":
            expense_id = int(input("Expense ID to delete: "))
            expense_tracker.delete_expense(expense_id)
        elif choice == "5":
            print("Logged out successfully.")
            current_user_id = None
            main()
            break
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

    db.close()

if __name__ == "__main__":
    main()
