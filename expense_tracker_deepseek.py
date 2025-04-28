import matplotlib.pyplot as plt
import csv, sys, os, hashlib, warnings, time
from collections import defaultdict
from tabulate import tabulate
from datetime import datetime, timedelta
from getpass import getpass
import json
from typing import List, Dict, Optional, Tuple

# Constants and Configuration
CONFIG = {
    "BASE_DIR": os.path.join(os.path.expanduser("~"), "ExpenseTracker"),
    "DATA_ENCRYPTION": False,  # Placeholder for future encryption
    "VALID_CATEGORIES": ["food", "travel", "bills", "health", "entertainment", "shopping", "others"],
    "DATE_FORMAT": "%Y-%m-%d",
    "MONTH_FORMAT": "%Y-%m",
    "PASSWORD_MIN_LENGTH": 8,
    "INACTIVITY_TIMEOUT": 300  # 5 minutes in seconds
}

# Ensure base directory exists
os.makedirs(CONFIG["BASE_DIR"], exist_ok=True)

class UserManager:
    """Handles user authentication and management"""
    
    def __init__(self):
        self.user_file = os.path.join(CONFIG["BASE_DIR"], "users.json")
        self. _initialize_user_file()
    
    def _initialize_user_file(self):
        if not os.path.exists(self.user_file):
            with open(self.user_file, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self) -> Dict:
        with open(self.user_file, 'r') as f:
            return json.load(f)
    
    def _save_users(self, users: Dict):
        with open(self.user_file, 'w') as f:
            json.dump(users, f, indent=4)
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        if len(password) < CONFIG["PASSWORD_MIN_LENGTH"]:
            return False, f"Password must be at least {CONFIG['PASSWORD_MIN_LENGTH']} characters"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        if not any(c.isalpha() for c in password):
            return False, "Password must contain at least one letter"
        return True, ""
    
    def register_user(self, username: str, password: str) -> bool:
        users = self._load_users()
        if username in users:
            print("Username already exists")
            return False
        
        valid, msg = self.validate_password(password)
        if not valid:
            print(msg)
            return False
        
        users[username] = {
            "password_hash": self.hash_password(password),
            "budgets": {category: 0 for category in CONFIG["VALID_CATEGORIES"]},
            "created_at": datetime.now().strftime(CONFIG["DATE_FORMAT"])
        }
        self._save_users(users)
        return True
    
    def authenticate_user(self, username: str, password: str) -> bool:
        users = self._load_users()
        user_data = users.get(username)
        if not user_data:
            return False
        return user_data["password_hash"] == self.hash_password(password)
    
    def update_password(self, username: str, new_password: str) -> bool:
        users = self._load_users()
        if username not in users:
            return False
        
        valid, msg = self.validate_password(new_password)
        if not valid:
            print(msg)
            return False
        
        users[username]["password_hash"] = self.hash_password(new_password)
        self._save_users(users)
        return True
    
    def set_budget(self, username: str, category: str, amount: float) -> bool:
        users = self._load_users()
        if username not in users:
            return False
        if category not in CONFIG["VALID_CATEGORIES"]:
            return False
        
        users[username]["budgets"][category] = amount
        self._save_users(users)
        return True
    
    def get_budgets(self, username: str) -> Dict[str, float]:
        users = self._load_users()
        return users.get(username, {}).get("budgets", {})

class ExpenseManager:
    """Handles all expense-related operations"""
    
    def __init__(self, username: str):
        self.username = username
        self.expense_file = os.path.join(CONFIG["BASE_DIR"], f"expenses_{username}.csv")
        self._initialize_expense_file()
    
    def _initialize_expense_file(self):
        if not os.path.exists(self.expense_file):
            with open(self.expense_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["date", "amount", "category", "note"])
    
    def add_expense(self, date: str, amount: float, category: str, note: str = "") -> bool:
        try:
            valid_date = self._validate_date(date)
            valid_category = self._validate_category(category)
            valid_amount = float(amount)
            
            with open(self.expense_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([valid_date, valid_amount, valid_category, note])
            return True
        except (ValueError, Exception) as e:
            print(f"Error adding expense: {e}")
            return False
    
    def get_expenses(self, filters: Optional[Dict] = None) -> List[Dict]:
        expenses = []
        try:
            with open(self.expense_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if self._matches_filters(row, filters):
                        expenses.append(row)
        except FileNotFoundError:
            pass
        return expenses
    
    def _matches_filters(self, expense: Dict, filters: Optional[Dict]) -> bool:
        if not filters:
            return True
        
        for key, value in filters.items():
            if key == "month":
                if not expense["date"].startswith(value):
                    return False
            elif key == "category":
                if expense["category"].lower() != value.lower():
                    return False
            elif key == "date":
                if expense["date"] != value:
                    return False
            elif key == "min_amount":
                if float(expense["amount"]) < float(value):
                    return False
            elif key == "max_amount":
                if float(expense["amount"]) > float(value):
                    return False
        return True
    
    def delete_expense(self, expense_to_delete: Dict) -> bool:
        expenses = self.get_expenses()
        updated_expenses = [e for e in expenses if e != expense_to_delete]
        
        if len(updated_expenses) == len(expenses):
            return False
        
        self._write_all_expenses(updated_expenses)
        return True
    
    def update_expense(self, old_expense: Dict, new_expense: Dict) -> bool:
        expenses = self.get_expenses()
        updated = False
        
        for i, expense in enumerate(expenses):
            if expense == old_expense:
                expenses[i] = new_expense
                updated = True
                break
        
        if updated:
            self._write_all_expenses(expenses)
        return updated
    
    def _write_all_expenses(self, expenses: List[Dict]):
        with open(self.expense_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "amount", "category", "note"])
            writer.writeheader()
            writer.writerows(expenses)
    
    def _validate_date(self, date_str: str) -> str:
        if not date_str:  # Use today if empty
            return datetime.now().strftime(CONFIG["DATE_FORMAT"])
        try:
            return datetime.strptime(date_str, CONFIG["DATE_FORMAT"]).strftime(CONFIG["DATE_FORMAT"])
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
    
    def _validate_category(self, category: str) -> str:
        category = category.lower()
        if category not in CONFIG["VALID_CATEGORIES"]:
            raise ValueError(f"Invalid category. Valid categories are: {', '.join(CONFIG['VALID_CATEGORIES'])}")
        return category

class ExpenseTracker:
    """Main application class"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.current_user = None
        self.expense_manager = None
        self.last_activity = time.time()
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def check_inactivity(self):
        if time.time() - self.last_activity > CONFIG["INACTIVITY_TIMEOUT"]:
            print("\nSession timed out due to inactivity")
            self.logout()
            return True
        return False
    
    def update_activity(self):
        self.last_activity = time.time()
    
    def login(self):
        self.clear_screen()
        while True:
            print("\n--- Expense Tracker Login ---")
            print("1. Login")
            print("2. Register")
            print("3. Exit")
            
            choice = input("Choose an option (1-3): ")
            
            if choice == "1":
                username = input("Username: ").strip()
                password = self._get_password_input("Password: ")
                
                if self.user_manager.authenticate_user(username, password):
                    self.current_user = username
                    self.expense_manager = ExpenseManager(username)
                    print(f"\nWelcome back, {username}!")
                    time.sleep(1)
                    return True
                else:
                    print("\nInvalid credentials. Please try again.")
                    time.sleep(1)
            
            elif choice == "2":
                username = input("Choose a username: ").strip()
                password = self._get_password_input("Choose a password: ")
                confirm = self._get_password_input("Confirm password: ")
                
                if password != confirm:
                    print("\nPasswords don't match!")
                    time.sleep(1)
                    continue
                
                if self.user_manager.register_user(username, password):
                    print("\nRegistration successful! You are now logged in.")
                    self.current_user = username
                    self.expense_manager = ExpenseManager(username)
                    time.sleep(1)
                    return True
                else:
                    time.sleep(1)
            
            elif choice == "3":
                return False
            
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
    
    def logout(self):
        self.current_user = None
        self.expense_manager = None
        print("\nLogged out successfully.")
        time.sleep(1)
    
    def _get_password_input(self, prompt: str) -> str:
        if 'idlelib' in sys.modules or not sys.stdin.isatty():
            print("\nWarning: Password may be visible in this environment")
            return input(prompt)
        else:
            return getpass(prompt)
    
    def main_menu(self):
        while True:
            if self.check_inactivity():
                break
            
            self.clear_screen()
            print(f"\n--- Expense Tracker (Logged in as {self.current_user}) ---")
            print("1. Add Expense")
            print("2. View/Filter Expenses")
            print("3. Reports & Analytics")
            print("4. Budget Management")
            print("5. Account Settings")
            print("6. Logout")
            
            choice = input("\nChoose an option (1-6): ")
            self.update_activity()
            
            if choice == "1":
                self.add_expense_flow()
            elif choice == "2":
                self.view_expenses_flow()
            elif choice == "3":
                self.reports_flow()
            elif choice == "4":
                self.budget_flow()
            elif choice == "5":
                self.account_settings_flow()
            elif choice == "6":
                if input("Are you sure you want to logout? (y/n): ").lower() == 'y':
                    self.logout()
                    break
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
    
    def add_expense_flow(self):
        while True:
            self.clear_screen()
            print("\n--- Add New Expense ---")
            
            try:
                amount = float(input("Amount: "))
                print("\nCategories: " + ", ".join(CONFIG["VALID_CATEGORIES"]))
                category = input("Category: ").lower()
                date = input(f"Date [{CONFIG['DATE_FORMAT']}] (leave blank for today): ")
                note = input("Note (optional): ")
                
                if self.expense_manager.add_expense(date, amount, category, note):
                    print("\nExpense added successfully!")
                else:
                    print("\nFailed to add expense. Please try again.")
                
                if input("\nAdd another expense? (y/n): ").lower() != 'y':
                    break
            except ValueError as e:
                print(f"\nError: {e}")
                time.sleep(1)
    
    def view_expenses_flow(self):
        while True:
            self.clear_screen()
            print("\n--- View Expenses ---")
            print("1. View All Expenses")
            print("2. Filter by Category")
            print("3. Filter by Date")
            print("4. Filter by Month")
            print("5. Back to Main Menu")
            
            choice = input("\nChoose an option (1-5): ")
            self.update_activity()
            
            if choice == "1":
                expenses = self.expense_manager.get_expenses()
                self._display_expenses(expenses)
            elif choice == "2":
                category = input("Enter category: ").lower()
                expenses = self.expense_manager.get_expenses({"category": category})
                self._display_expenses(expenses)
            elif choice == "3":
                date = input(f"Enter date ({CONFIG['DATE_FORMAT']}): ")
                try:
                    valid_date = datetime.strptime(date, CONFIG["DATE_FORMAT"]).strftime(CONFIG["DATE_FORMAT"])
                    expenses = self.expense_manager.get_expenses({"date": valid_date})
                    self._display_expenses(expenses)
                except ValueError:
                    print("Invalid date format")
                    time.sleep(1)
            elif choice == "4":
                month = input(f"Enter month ({CONFIG['MONTH_FORMAT']}): ")
                try:
                    valid_month = datetime.strptime(month, CONFIG["MONTH_FORMAT"]).strftime(CONFIG["MONTH_FORMAT"])
                    expenses = self.expense_manager.get_expenses({"month": valid_month})
                    self._display_expenses(expenses)
                except ValueError:
                    print("Invalid month format")
                    time.sleep(1)
            elif choice == "5":
                break
            else:
                print("Invalid choice")
                time.sleep(1)
    
    def _display_expenses(self, expenses: List[Dict]):
        if not expenses:
            print("\nNo expenses found")
            input("\nPress Enter to continue...")
            return
        
        print("\nExpenses:")
        print(tabulate(expenses, headers="keys", tablefmt="grid"))
        
        total = sum(float(e["amount"]) for e in expenses)
        print(f"\nTotal: Rs. {total:.2f}")
        
        input("\nPress Enter to continue...")
    
    def reports_flow(self):
        while True:
            self.clear_screen()
            print("\n--- Reports & Analytics ---")
            print("1. Monthly Summary")
            print("2. Category Breakdown")
            print("3. Monthly Trends")
            print("4. Budget vs Actual")
            print("5. Back to Main Menu")
            
            choice = input("\nChoose an option (1-5): ")
            self.update_activity()
            
            if choice == "1":
                self._monthly_summary_report()
            elif choice == "2":
                self._category_breakdown_report()
            elif choice == "3":
                self._monthly_trends_report()
            elif choice == "4":
                self._budget_vs_actual_report()
            elif choice == "5":
                break
            else:
                print("Invalid choice")
                time.sleep(1)
    
    def _monthly_summary_report(self):
        month = input(f"Enter month ({CONFIG['MONTH_FORMAT']}): ")
        try:
            valid_month = datetime.strptime(month, CONFIG["MONTH_FORMAT"]).strftime(CONFIG["MONTH_FORMAT"])
            expenses = self.expense_manager.get_expenses({"month": valid_month})
            
            if not expenses:
                print("\nNo expenses found for this month")
                input("\nPress Enter to continue...")
                return
            
            # Calculate totals by category
            category_totals = defaultdict(float)
            for e in expenses:
                category_totals[e["category"]] += float(e["amount"])
            
            # Display summary
            print(f"\nMonthly Summary for {valid_month}")
            print(tabulate(
                [(cat, f"Rs. {amt:.2f}") for cat, amt in category_totals.items()],
                headers=["Category", "Amount"],
                tablefmt="grid"
            ))
            
            total = sum(category_totals.values())
            print(f"\nTotal Expenses: Rs. {total:.2f}")
            
            # Show pie chart
            if input("\nShow chart? (y/n): ").lower() == 'y':
                plt.figure(figsize=(8, 6))
                plt.pie(
                    category_totals.values(),
                    labels=category_totals.keys(),
                    autopct='%1.1f%%',
                    startangle=90
                )
                plt.title(f"Expense Breakdown for {valid_month}")
                plt.show()
            
            input("\nPress Enter to continue...")
        except ValueError:
            print("Invalid month format")
            time.sleep(1)
    
    def _category_breakdown_report(self):
        expenses = self.expense_manager.get_expenses()
        
        if not expenses:
            print("\nNo expenses found")
            input("\nPress Enter to continue...")
            return
        
        category_totals = defaultdict(float)
        for e in expenses:
            category_totals[e["category"]] += float(e["amount"])
        
        print("\nCategory Breakdown:")
        print(tabulate(
            [(cat, f"Rs. {amt:.2f}") for cat, amt in category_totals.items()],
            headers=["Category", "Amount"],
            tablefmt="grid"
        ))
        
        if input("\nShow chart? (y/n): ").lower() == 'y':
            plt.figure(figsize=(8, 6))
            plt.pie(
                category_totals.values(),
                labels=category_totals.keys(),
                autopct='%1.1f%%',
                startangle=90
            )
            plt.title("Overall Expense Breakdown")
            plt.show()
        
        input("\nPress Enter to continue...")
    
    def _monthly_trends_report(self):
        expenses = self.expense_manager.get_expenses()
        
        if not expenses:
            print("\nNo expenses found")
            input("\nPress Enter to continue...")
            return
        
        # Group by month
        monthly_totals = defaultdict(float)
        for e in expenses:
            month = datetime.strptime(e["date"], CONFIG["DATE_FORMAT"]).strftime(CONFIG["MONTH_FORMAT"])
            monthly_totals[month] += float(e["amount"])
        
        # Sort by month
        sorted_months = sorted(monthly_totals.keys())
        sorted_amounts = [monthly_totals[m] for m in sorted_months]
        
        print("\nMonthly Trends:")
        print(tabulate(
            [(month, f"Rs. {amt:.2f}") for month, amt in zip(sorted_months, sorted_amounts)],
            headers=["Month", "Total"],
            tablefmt="grid"
        ))
        
        if input("\nShow chart? (y/n): ").lower() == 'y':
            plt.figure(figsize=(10, 5))
            plt.plot(sorted_months, sorted_amounts, marker='o')
            plt.xlabel("Month")
            plt.ylabel("Total Expenses (Rs.)")
            plt.title("Monthly Expense Trends")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            plt.show()
        
        input("\nPress Enter to continue...")
    
    def _budget_vs_actual_report(self):
        budgets = self.user_manager.get_budgets(self.current_user)
        expenses = self.expense_manager.get_expenses()
        
        if not budgets:
            print("\nNo budgets set up yet")
            input("\nPress Enter to continue...")
            return
        
        # Calculate actual spending by category
        actual_spending = defaultdict(float)
        for e in expenses:
            actual_spending[e["category"]] += float(e["amount"])
        
        # Prepare comparison data
        comparison_data = []
        for category in CONFIG["VALID_CATEGORIES"]:
            budget = budgets.get(category, 0)
            actual = actual_spending.get(category, 0)
            difference = budget - actual
            comparison_data.append([
                category.capitalize(),
                f"Rs. {budget:.2f}",
                f"Rs. {actual:.2f}",
                f"Rs. {difference:.2f}",
                "Under" if difference >= 0 else "Over"
            ])
        
        print("\nBudget vs Actual Spending:")
        print(tabulate(
            comparison_data,
            headers=["Category", "Budget", "Actual", "Difference", "Status"],
            tablefmt="grid"
        ))
        
        input("\nPress Enter to continue...")
    
    def budget_flow(self):
        while True:
            self.clear_screen()
            print("\n--- Budget Management ---")
            print("1. View Budgets")
            print("2. Set Budget")
            print("3. Back to Main Menu")
            
            choice = input("\nChoose an option (1-3): ")
            self.update_activity()
            
            if choice == "1":
                self._view_budgets()
            elif choice == "2":
                self._set_budget()
            elif choice == "3":
                break
            else:
                print("Invalid choice")
                time.sleep(1)
    
    def _view_budgets(self):
        budgets = self.user_manager.get_budgets(self.current_user)
        
        print("\nYour Budgets:")
        print(tabulate(
            [(cat.capitalize(), f"Rs. {amt:.2f}") for cat, amt in budgets.items() if amt > 0],
            headers=["Category", "Budget"],
            tablefmt="grid"
        ))
        
        input("\nPress Enter to continue...")
    
    def _set_budget(self):
        print("\nCategories: " + ", ".join(CONFIG["VALID_CATEGORIES"]))
        category = input("Enter category: ").lower()
        
        if category not in CONFIG["VALID_CATEGORIES"]:
            print("Invalid category")
            time.sleep(1)
            return
        
        try:
            amount = float(input("Enter budget amount: "))
            if self.user_manager.set_budget(self.current_user, category, amount):
                print("\nBudget updated successfully!")
            else:
                print("\nFailed to update budget")
            time.sleep(1)
        except ValueError:
            print("Invalid amount")
            time.sleep(1)
    
    def account_settings_flow(self):
        while True:
            self.clear_screen()
            print("\n--- Account Settings ---")
            print("1. Change Password")
            print("2. View Account Info")
            print("3. Back to Main Menu")
            
            choice = input("\nChoose an option (1-3): ")
            self.update_activity()
            
            if choice == "1":
                self._change_password()
            elif choice == "2":
                self._view_account_info()
            elif choice == "3":
                break
            else:
                print("Invalid choice")
                time.sleep(1)
    
    def _change_password(self):
        current = self._get_password_input("Current password: ")
        if not self.user_manager.authenticate_user(self.current_user, current):
            print("\nIncorrect current password")
            time.sleep(1)
            return
        
        new = self._get_password_input("New password: ")
        confirm = self._get_password_input("Confirm new password: ")
        
        if new != confirm:
            print("\nPasswords don't match")
            time.sleep(1)
            return
        
        if self.user_manager.update_password(self.current_user, new):
            print("\nPassword changed successfully!")
        else:
            print("\nFailed to change password")
        time.sleep(1)
    
    def _view_account_info(self):
        print("\nAccount Information:")
        print(f"Username: {self.current_user}")
        print(f"Expense file: {self.expense_manager.expense_file if self.expense_manager else 'Not loaded'}")
        input("\nPress Enter to continue...")

def main():
    tracker = ExpenseTracker()
    if tracker.login():
        tracker.main_menu()

if __name__ == "__main__":
    main()
