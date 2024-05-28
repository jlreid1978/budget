import bcrypt
import re
import sqlite3
import threading

# Create a thread-local storage for the SQLite connection
local = threading.local()

# Functions to connect to the SQLite database
def get_cursor():
    conn = get_connection()
    return conn.cursor()


def get_connection():
    if not hasattr(local, 'conn'):
        local.conn = sqlite3.connect('budget.db')
    return local.conn


def close_connection():
    if hasattr(local, 'conn'):
        local.conn.close()
        del local.conn


# Function to register new user
def register_user(name, username, password):
    conn = get_connection()
    cursor = conn.cursor()
    if not is_valid_password(password):
        close_connection()
        return "Password must be 8 characters and contain one of the following: Upper Case, Number, and Symbol"
    else:
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO users (name, username, password_hash) VALUES (?, ?, ?)", (name, username, password_hash))
            conn.commit()
            close_connection()
            return "Registration successful"
        except sqlite3.IntegrityError:
            close_connection()
            return "Username already exists"


# Function to validate password entries and changes
def is_valid_password(password):
    upper_regex = re.compile(r'[A-Z]')
    digit_regex = re.compile(r'\d')
    symbol_regex = re.compile(r'[!@#$%^&*()_+{}[\]:;<>,.?/~]')
    has_uppercase = bool(upper_regex.search(password))
    has_digit = bool(digit_regex.search(password))
    has_symbol = bool(symbol_regex.search(password))
    length_valid = len(password) >= 8
    return has_uppercase and has_digit and has_symbol and length_valid


# Function to verify password
def verify_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        if result:
            stored_hash = result[0]
            if isinstance(stored_hash, str): 
                stored_hash = stored_hash.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                return True
    finally:
        close_connection()
    return False


# Function to delete user
def delete_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    close_connection()


# Function to get name from database
def get_name(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    close_connection()
    if result:
        return result[0]
    else:
        return None


# Function to get user ID
def get_user_id(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    close_connection()
    if result:
        return result[0]
    return None


# Function for user to change password
def change_password(username, current_password, new_password):
    if not is_valid_password(new_password):
        raise ValueError("Password must be 8 characters and contain one of the following: Upper Case, Number, and Symbol")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if not result or not bcrypt.checkpw(current_password.encode('utf-8'), result[0].encode('utf-8')):
        close_connection()
        raise ValueError("Current password is incorrect")
    try:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_password, username))
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    conn.commit()
    close_connection()


# Function for admin to reset user's password to a default value
def reset_password(username):
    default_password = "Budget1!"
    hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if not result:
        close_connection()
        raise ValueError("Username does not exist")
    try:
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (hashed_password, username))
    except Exception as e:
        print(f"An error occurred: {e}")
        raise
    conn.commit()
    close_connection()
