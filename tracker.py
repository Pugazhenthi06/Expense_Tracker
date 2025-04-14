import matplotlib.pyplot as plt
import csv
import os
from collections import defaultdict
from tabulate import tabulate
from datetime import datetime
from sys import exit


User_found = False

while not User_found:
    choice = input("Do you want to Login(L) or Signup(S): ").strip().lower()

    if choice == 'l':
        username = input("Enter Username: ").strip()
        password = input("Enter Password: ").strip()
        with open(r'C:\Soft Skills\Expense_tracker\Users.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] == username and row[1] == password:
                    print("Login successful")
                    User_found = True
                    break
            if not User_found:
                print("Invalid credentials. Try again.\n")

    elif choice == 's':
        username = input("Create a Username: ").strip()
        with open(r'C:\Soft Skills\Expense_tracker\Users.csv', 'r') as f:
            reader = csv.reader(f)
            existing_users = [row[0] for row in reader]

        if username in existing_users:
            print("Username already exists. Try a different one.\n")
        else:
            password = input("Create a strong password: ").strip()
            with open(r'C:\Soft Skills\Expense_tracker\Users.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([username, password])
                print("Signup successful! You are now logged in.")
                User_found = True

    else:
        print("Invalid choice. Please enter L or S.\n")


Expense_Tracker_File = fr'C:\Soft Skills\Expense_tracker\expenses_{username}.csv'

def add_expense():
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
                return
            headers = ["Date", "Amount", "Category", "Note"]
            print("\nExpense History:\n")
            print(tabulate(rows, headers=headers, tablefmt="grid"))
    except FileNotFoundError:
        print("No expenses file found.")

def total_spent():
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
    print("\n--- Expense Tracker ---")
    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Filters & Views")
    print("4. Totals")
    print("5. Edit & Delete Expense")
    print("6. Plot Expense")
    print("7. Exit")

    try:
        choice = int(input("Choose an option (1-7): "))

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
                choice=input("Enter the choice(a,b,c):")
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
        elif choice == 7:
            confirm = input("Are you sure you want to exit? (y/n): ").lower()
            if confirm == 'y':
                break
        else:
            print("Invalid choice. Try again.")
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 7.")




        
