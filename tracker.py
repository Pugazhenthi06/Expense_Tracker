import matplotlib.pyplot as plt
import csv,sys,os,hashlib,warnings,time
from collections import defaultdict
from tabulate import tabulate
from datetime import datetime
from sys import exit
from getpass import getpass



Expense_Tracker_File = ""


base_dir = os.path.join(os.path.expanduser("~"), "ExpenseTracker")
os.makedirs(base_dir, exist_ok=True)


user_file_path = os.path.join(base_dir, "Users.csv")
if not os.path.exists(user_file_path):
    
    with open(user_file_path, 'w', newline='') as f:
        pass

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_secure_password(prompt="Enter password:"):
    
    if 'idlelib' in sys.modules or not sys.stdin.isatty():
        input("\nWarning: Password may be visible due to limitations in this environment. Press Enter to continue...")
        warnings.filterwarnings("ignore")
        return getpass(prompt)
    else:
        input("\n[Security Notice] Your password will not appear on screen while typing. Press Enter to continue...")
        return getpass(prompt)


def authenticate_user():     
    User_found = False

    while not User_found:
        choice = input("Do you want to Login(L) or Signup(S) or exit: ").strip().lower()

        if choice == 'l':
            username = input("Enter Username: ").strip()
        
            password = get_secure_password("Enter Password:").strip()

            with open(user_file_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    hashed_input=hash_password(password)
                    if row[0].strip()==username and row[1].strip() == hashed_input:
                        print("Login successful\n")
                        input("Press Enter to Continue")
                        User_found=True
                        return username
    
                else:
                    print("Invalid credentials. Try again.\n")

        elif choice == 's':
            username = input("Create a Username: ").strip()
            with open(user_file_path, 'r') as f:
                existing_users = [row[0] for row in csv.reader(f)]

            if username in existing_users:
                print("Username already exists. Try a different one.\n")
            else:
                while  not User_found:
                    print("Note: Password should be atleast 8characters long, contains atleast one number, letter!")
                
                    password = get_secure_password("Enter Password:").strip()

                    if len(password)<8:
                        print("Password should be at least 8 characters long.")
                    elif not any(char.isdigit() for char in password):
                        print("Password should contain at least one number.")
                    elif not any(char.isalpha() for char in password):
                        print("Password should contain at least one letter.")
                    else:
                        confirm_password=get_secure_password("Confirm password:").strip()
                    
                        if password!=confirm_password:
                            print("passwords mismatch.  Please try again.")
                        else:
                            hashed_password=hash_password(password.strip())
                            with open(user_file_path, 'a', newline='') as f:
                                csv.writer(f).writerow([username.strip(), hashed_password.strip()])
                                print("Signup successful! You are now logged in.")
                                User_found = True
                                return username
                
    
        elif choice == 'exit':
            exit()

        else:
            print("Invalid choice. Please enter L or S.\n")


def file_path():
    clear_screen()
    print("The folder where all user data is stored:",base_dir)
    print("The File where their expenses are saved:",Expense_Tracker_File)

def clear_screen():
    if 'idlelib' not in sys.modules:
        os.system('cls' if os.name=='nt' else 'clear')
    
def add_expense():
    clear_screen()
    while True:
        try:
            amt = float(input("Enter amount spent: Rs."))
            category = input("Enter category (food, travel, bills, health, others): ").lower()
            date = input("Enter date (YYYY-MM-DD) or press Enter for today: ")
            if date:
                try:
                    valid_date=datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")

                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD")
                    return
            else:
                valid_date = datetime.now().strftime("%Y-%m-%d")
                
            note = input("Optional note: ")
            with open(Expense_Tracker_File, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([valid_date, amt, category, note])
            print("Expense recorded.")

            choice=input("Want to Continue(a) or Exit(b):")
            if choice=='a':
                continue
            elif choice=='b':
                break
            else:
                print("Invalid Choice. Please select 'a' to continue or 'b' to exit")
               
        except ValueError:
            print("Invalid amount. Try again.")

        

def view_expense():
    try:
        with open(Expense_Tracker_File, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                print("\nNo expenses recorded yet.")
                
                input("\n\n\tPress Enter to Continue")
                return
            headers = ["Date", "Amount", "Category", "Note"]
            print("\nExpense History:\n")
            print(tabulate(rows, headers=headers, tablefmt="grid"))
            
            input("\n\n\tPress Enter to Continue")
    except FileNotFoundError:
        print("No expenses file found.")
        
        input("\n\n\tPress Enter to Continue")

def total_spent():
    clear_screen()
    total = 0
    try:
        with open(Expense_Tracker_File, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    total += float(row[1])
        print(f"\nTotal Spent: Rs {total:,.2f}")
    except FileNotFoundError:
        print("No expenses file found.")
    except Exception as e:
        print(f"Error reading file: {e}")

def filter_by_field(field_index, search_value):
    matching_rows = []
    try:
        with open(Expense_Tracker_File, 'r') as f:
            reader = list(csv.reader(f))
            for i,row in enumerate(reader):
                if row and row[field_index][:len(search_value)] == search_value:
                    matching_rows.append(row)
        return matching_rows
    except FileNotFoundError:
        print("Expense file not found.")
        return []

def filter_by_category():
 
    clear_screen()
    category_input = input("Enter the Category: ").lower()

    try:
        
        with open(Expense_Tracker_File, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if not rows:
                print("No expenses recorded yet.")
                return

            all_categories = set(row[2].lower() for row in rows if row)

            if category_input in all_categories:
                filtered = [row for row in rows if row[2].lower() == category_input]
                if filtered:
                    print(tabulate(filtered, headers=["Date", "Amount", "Category", "Note"], tablefmt="grid"))
                else:
                    print("No expenses found for this category.")
            else:
                print("Invalid category. No expenses found.")
                other_categories = all_categories - set(category_input)
                if other_categories:
                    print("Other categories found in data:", ", ".join(sorted(other_categories)))
                else:
                    print("No other categories found in data either.")

    except FileNotFoundError:
        print("Expense file not found.")

def total_by_category():
    clear_screen()
    category = input("Enter the Category: ").strip()
    total = 0
    found = False
    all_categories=set()
    try:
        with open(Expense_Tracker_File, 'r') as f:
            reader = list(csv.reader(f))
            for row in reader:
                if row:
                    row_category=row[2].lower()
                    all_categories.add(row_category)

                    if row_category == category.lower():
                        total += float(row[1])
                        found = True
           
        if found:
            print(f"Total spent on {category}: Rs {total:,.2f}")
        else:
            print("No expenses found for this category.")
            print("Other Categories found in this date are...",','.join(all_categories-set(category)))
            
    except FileNotFoundError:
        print("Expense file not found.")

def filter_by_date():
    clear_screen()
    date = input("Enter the Date (YYYY-MM-DD): ")
    if date:
            try:
                valid_date=datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
                
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")
                return
       
    rows = filter_by_field(0,valid_date)
    if rows:
        headers=["Date", "Amount", "Category", "Note"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print("No expenses found on this date.")

def total_by_date():
    clear_screen()
    date = input("Enter the Date (YYYY-MM-DD): ")
    if date:
            try:
                valid_date=datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
                
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")
                return
        
    total = 0
    found = False
    try:
        with open(Expense_Tracker_File, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0][:10] == valid_date:
                    total += float(row[1])
                    found = True
        if found:
            print(f"Total spent on {date}: Rs {total:,.2f}")
        else:
            print("No expenses recorded on this date.")
    except FileNotFoundError:
        print("Expense file not found.")

def filter_by_month():
    clear_screen()
    month = input("Enter the Month (YYYY-MM): ")
    if month:
            try:
                valid_month=datetime.strptime(month, "%Y-%m").strftime("%Y-%m")
               
            except ValueError:
                print("Invalid date format. Please use YYYY-MM")
                return
       
    rows = filter_by_field(0,valid_month)
    if rows:
        headers=["date", "Amount", "Category", "Note"]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
    else:
        print("No expenses found in this month.")

def total_by_month():
    clear_screen()
    month = input("Enter the Month (YYYY-MM): ")
    if month:
            try:
                valid_month=datetime.strptime(month, "%Y-%m").strftime("%Y-%m")
                 
            except ValueError:
                print("Invalid date format. Please use YYYY-MM")
                return
        
    total = 0
    found = False
    try:
        with open(Expense_Tracker_File, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0][:7] == valid_month:
                    total += float(row[1])
                    found = True
        if found:
            print(f"Total spent in {month}: Rs {total:,.2f}")
        else:
            print("No expenses recorded in this month.")
    except FileNotFoundError:
        print("Expense file not found.")

def filter_expenses():
    clear_screen()
    print("\nChoose a filter to narrow down the expenses:")
    print("1. Filter by Category")
    print("2. Filter by Date")
    print("3. Filter by Month")
    filter_choice = input("Enter filter choice (1/2/3): ").strip()

    filtered_expenses = []

    if filter_choice == "1":
        category = input("Enter the category (food, travel, etc.): ").lower()
        filtered_expenses = filter_by_field(2, category)
    elif filter_choice == "2":
        date = input("Enter the date (YYYY-MM-DD): ").strip()
        if date:
            try:
                valid_date=datetime.strptime(date, "%Y-%m-%d")
                
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")
                return    
        filtered_expenses = filter_by_field(0, valid_date)
    elif filter_choice == "3":
        month = input("Enter the month (YYYY-MM): ")
        if month:
            try:
                valid_month=datetime.strptime(month, "%Y-%m")
                
            except ValueError:
                print("Invalid date format. Please use YYYY-MM")
                return
        filtered_expenses = filter_by_field(0, valid_month)
    else:
        print("Invalid choice. No filter applied.")
        return []

    if not filtered_expenses:
        print("No expenses found matching your filter.")
        return []

    print("\nFiltered Expenses:")
    for i,(idx,row) in enumerate(filtered_expenses):
        print(f"{i + 1}. {row[2]} - Rs {row[1]} on {row[0]} ({row[3]})")

    return [row for (idx,row) in filtered_expenses]

def delete_expense():
    clear_screen()
    filtered_expenses = filter_expenses()
    
    if not filtered_expenses:
        print("No expenses found to delete.")
        return
    
    try:
        choice = int(input("Enter the number of the expense you want to delete: ")) - 1
        if choice < 0 or choice >= len(filtered_expenses):
            print("Invalid choice. No such expense found.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    # Assume filtered_expenses[choice] is already in [date, amount, category, note] format
    row_to_delete = filtered_expenses[choice]
    print("You chose to delete:", row_to_delete)
    
    try:
        with open(Expense_Tracker_File, 'r') as f:
            rows = list(csv.reader(f))
    except FileNotFoundError:
        print("Expense file not found.")
        return

    # Directly compare rows (no normalization needed)
    updated_rows = [row for row in rows if row != row_to_delete]
    
    if len(updated_rows)<len(rows):
        with open(Expense_Tracker_File, 'w', newline='') as f:
            csv.writer(f).writerows(updated_rows)
        print( "Expense deleted successfully.")
    else:
        print( "Expense not found in file.")

               
def clear_expense():
    clear_screen()
    command=input("Are you sure, want to delete all the expenses(y,n):").lower()
    if command=='y':
        try:
            with open(Expense_Tracker_File,'w',newline='')as f:
                 writer=csv.writer(f)
                 print("Expense Cleared Successfully")
        except FileNotFoundError:
            print("Expense File Not Found")
    
    
    elif command=='n':
        return
    else:
        print("Invalid Choice. Please select(y/n)")
        

def modify_expense():
    clear_screen()
    filtered = filter_expenses()

    if not filtered:
        return
    
    try:
        choice = int(input("Enter the number on which the expense you want to modify: ")) - 1
        if choice < 0 or choice >= len(filtered):
            print("Invalid choice. No such expense found.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    selected_expense = filtered[choice].copy()
    original_expense = filtered[choice].copy()
    
    print(f"\nYou selected: {selected_expense[2]} - Rs {selected_expense[1]} on {selected_expense[0]} ({selected_expense[3]})")
    while(True):
        print("\nWhat would you like to modify?")
        print("1. Amount")
        print("2. Category")
        print("3. Date")
        print("4. Note")
        print("5. Exit")
        modify_choice = input("Enter your choice (1/2/3/4/5): ").strip()

        if modify_choice == "1":
            try:
                new_amount = float(input("Enter the new amount: Rs. "))
                selected_expense[1] = str(new_amount)
            except ValueError:
                print("Invalid input. Please enter a valid amount.")
                continue
        elif modify_choice == "2":
            new_category = input("Enter the new category: ").lower()
            selected_expense[2] = new_category
        elif modify_choice == "3":
            new_date = input("Enter the new date (YYYY-MM-DD): ")
            try:
                date_obj=datetime.strptime(new_date,"%Y-%m-%d")
                selected_expense[0] = date_obj.strftime("%Y-%m-%d")
            
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                continue
        elif modify_choice == "4":
            new_note = input("Enter the new note: ")
            selected_expense[3] = new_note
        elif modify_choice=="5":
            break
        else:
            print("Invalid choice. No modifications made.")
            return

        try:
            with open(Expense_Tracker_File, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except FileNotFoundError:
            print("Expense file not found.")
            continue
        
        updated=False
        for i,row in enumerate(rows):
            if row == original_expense:
                rows[i]=selected_expense
                updated=True
                break
        if updated:

            with open(Expense_Tracker_File, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
    
                print("Expense modified successfully.")
        else:
            print("Error: Expense not found in file.")
            continue
    

        

def plot_expenses():
    clear_screen()
    categories = defaultdict(float)

    try:
        with open(Expense_Tracker_File, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    categories[row[2].lower()] += float(row[1])
    except FileNotFoundError:
        print("Expense file not found.")

    if categories:
        # Create the pie chart
        plt.figure(figsize=(8, 8))  # Optional: Adjust the size of the pie chart
        plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%',wedgeprops={'edgecolor':'black'}, colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'])
        plt.axis('equal')
        # Title for the pie chart
        plt.title('Expense Distribution by Category')
        
        # Display the chart
        plt.show()
    else:
        print("No data to plot.")


while True:
    clear_screen()
    
    username=authenticate_user()
    Expense_Tracker_File = os.path.join(base_dir, f"expenses_{username}.csv")

    while True:
        print("\n--- Expense Tracker ---")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. Filters & Views")
        print("4. Totals")
        print("5. Edit & Delete Expense")
        print("6. Plot Expense")
        print("7. File path ")
        print("8. Log Out")
        
        try:
            choice = int(input("Choose an option (1-8): "))

            if choice == 1:
                add_expense()
            elif choice == 2:
                view_expense()
            elif choice == 3:
                while True:
                
                    print("\n-- Filter Options --")
                    print("a. Filter by Category")
                    print("b. Filter by Date")
                    print("c. Filter by Month")
                    print("d. Exit")
                    sub_choice = input("Choose a filter (a-d): ").lower()
                    if sub_choice == 'a':
                        filter_by_category()
                    elif sub_choice == 'b':
                        filter_by_date()
                    elif sub_choice == 'c':
                        filter_by_month()
                    elif sub_choice=='d':
                        break
                    else:
                        print("Invalid filter option.")
            elif choice == 4:
                while True:
                    print("\n-- Totals --")
                    print("a. Total by Category")
                    print("b. Total by Date")
                    print("c. Total by Month")
                    print("d. Total Spent")
                    print("e. Exit")
                    sub_choice = input("Choose a total option (a-e): ").lower()
                    if sub_choice == 'a':
                        total_by_category()
                    elif sub_choice == 'b':
                        total_by_date()
                    elif sub_choice == 'c':
                        total_by_month()
                    elif sub_choice == 'd':
                        total_spent()
                    elif sub_choice=='e':
                        break
                    else:
                        print("Invalid total option.")
            elif choice == 5:
                while True:
                    print("\nOptions")
                    print("a. Delete")
                    print("b. Modify")
                    print("c. Clear(Delete all the expenses)")
                    print("d. Exit")
                    choice=input("Enter the choice(a,b,c,d):")
                    if choice=='a':
                        delete_expense()
                    elif choice=='b':
                        modify_expense()
                    elif choice=='c':
                        clear_expense()
                    elif choice=='d':
                        break
                    else:
                        print("Invalid option.")
            elif choice == 6:
                plot_expenses()
            elif choice==7:
                file_path()
            
            elif choice == 8:
                confirm = input("Are You Sure want to log out (y/n): ").lower()
                if confirm == 'y':
                    print("Log Out Successful, Wait a second")
                    time.sleep(2)
                    break
                elif confirm =='n':
                    print("Log Out Unsuccessful, Wait a second")
                    time.sleep(2)
                   
                else:
                    print("Invalid choice. Please enter (y/n)")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 8.")




        
