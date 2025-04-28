import hashlib

class User:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.cursor = db_manager.cursor

    def hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def signup(self, username, password):
        hashed_pw = self.hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            self.db_manager.commit()
            print("Signup successful! You can now login.")
        except:
            print("Username already exists. Try another one.")

    def login(self, username, password):
        hashed_pw = self.hash_password(password)
        self.cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed_pw))
        result = self.cursor.fetchone()
        if result:
            print(f"Login successful! Welcome {username}")
            return result[0]  # return user_id
        else:
            print("Invalid username or password.")
            return None
