# 🧾 Python Expense Tracker

A terminal-based expense tracker written in Python that lets you log, view, edit, and visualize your personal spending easily with CSV files.

---

## 🚀 Features

- ✅ User login & signup system
- 💸 Add, view, and manage expenses by category/date/month
- 📊 Visualize spending with pie charts using Matplotlib
- 🧮 View totals by category, date, or month
- ✏️ Modify and delete individual expenses
- 🔥 Clear all expenses at once
- 📁 Automatically creates a per-user CSV file for tracking

---

## 📂 Files

- `tracker.py`: The main script
- `Users.csv`: Stores registered usernames and passwords
- `expenses_<username>.csv`: Individual user expense logs
- `.gitignore`: Tells Git which files to ignore
- `README.md`: Project overview (this file)

---

## 💻 How to Run

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Pugazhenthi06/Expense_Tracker.git
   cd Expense_Tracker

 ## 👥 Multiple User Support

- Each user signs up with a username and password
- A personal CSV file is created: `expenses_<username>.csv`
- Your data stays separate from others

This app supports multiple users with their own separate CSV files:

- 🔐 Users can **Login or Signup** from the terminal.
- 📁 When a user signs up, a new file like `expenses_<username>.csv` is created.
- 🧾 Each user’s expenses are saved in their own file.
- 💻 Data is **local-only** (not stored in a shared database or uploaded).
- 🧪 You can test it by using the included `sample_expenses.csv`.

> 📌 Real CSV files (like `expenses_demoname.csv`) are now excluded from the repository using `.gitignore`.

## 🧪 Demo Data

A file named `sample_expenses.csv` is included for testing.

You can open it to see how expenses are stored and formatted:
```csv
2025-04-01,250,food,Lunch at local restaurant
2025-04-02,80,travel,Bus fare to office
...



## 👨‍💻 Author

Built with 💚 by [Pugazhenthi](https://github.com/Pugazhenthi06)
