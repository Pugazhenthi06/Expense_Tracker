import sqlite3

class DatabaseManager:
    def __init__(self, db_name="expense_tracker.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE,
                                password TEXT
                            )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                category TEXT,
                                amount REAL,
                                date TEXT,
                                description TEXT,
                                FOREIGN KEY (user_id) REFERENCES users(id)
                            )''')
        self.conn.commit()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
