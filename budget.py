from dateutil.relativedelta import relativedelta

import datetime
import sqlite3
import threading



# Create a thread-local storage for the SQLite connection
local = threading.local()


# Functions to connect to the SQLite database
def get_connection():
    if not hasattr(local, 'conn'):
        local.conn = sqlite3.connect('budget.db')
    return local.conn


def close_connection():
    if hasattr(local, 'conn'):
        local.conn.close()
        del local.conn


# Function to add entry into budget
def add_budget(user_id, description, amount, type, frequency, date):
    if (type == 'debit'):
        amount = -abs(amount)
    print(f"user id = {user_id} \ndescription = {description} \namount = {amount} \ntype = {type} \nfrequency = {frequency} \ndate = {date}")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO budget (user_id, description, amount, frequency, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, description, amount, frequency, date))
        conn.commit()
    except Exception:
        print("An error has occured inserting database")
        raise 500
    finally:
        close_connection()


# Function to pull user's budget for the view page
def get_user_budget(user_id):
    print(f"Pulling budget for {user_id}")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        print(f'SELECT description, amount, frequency, date FROM budget WHERE user_id = {user_id};')
        cursor.execute('''
            SELECT description, amount, frequency, date
            FROM budget
            WHERE user_id = ?
        ''', (user_id,))
        data_transaction = cursor.fetchall()
        budget_data = calculate_budget(data_transaction)
        return budget_data

    except Exception as e:
        print(f"An error has occured pulling from database\n {e}")
        raise 404
    finally:
        close_connection()


# Function to help organize budget data for viewing
def calculate_budget(data_transactions):
    budget_data = []

    def add_transactions(description, amount, start_date, frequency):
        date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.datetime.now() + relativedelta(years=1)

        while date <= end_date:
            budget_data.append({
                'description': description,
                'amount': amount,
                'date': date.strftime('%Y-%m-%d')
            })
            # Setting math values for frequency entries
            if frequency == 'weekly':
                date += datetime.timedelta(weeks=1)
            elif frequency == 'monthly':
                date += relativedelta(months=1)
            elif frequency == 'quarterly':
                date += relativedelta(months=3)
            elif frequency == 'yearly':
                date += relativedelta(years=1)
            else:
                break  # For one-time transactions

    for transaction in data_transactions:
        description, amount, frequency, start_date = transaction
        add_transactions(description, amount, start_date, frequency)

    return budget_data


# Function to pull SQL entries from the budget table
def get_user_budget_entries(user_id):
    print(f"Pulling budget for {user_id}")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        print(f'SELECT description, amount, frequency, date FROM budget WHERE user_id = {user_id};')
        cursor.execute('''
            SELECT description, amount, frequency, date, id
            FROM budget
            WHERE user_id = ?
        ''', (user_id,))
        budget_entries = cursor.fetchall()
        return budget_entries

    except Exception as e:
        print(f"An error has occured pulling from database\n {e}")
        raise 404
    finally:
        close_connection()


# Function to delete budget entry from database
def delete_budget_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM budget WHERE id = ?", (entry_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"An error occurred while deleting budget entry: {e}")
        return False
    finally:
        close_connection()


# Function to update an edited budget entry
def update_budget_entry(entry_id, updated_description, updated_amount, updated_frequency, updated_date):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE budget
            SET description = ?, amount = ?, frequency = ?, date = ?
            WHERE id = ?
        ''', (updated_description, updated_amount, updated_frequency, updated_date, entry_id))
        conn.commit()
    except Exception as e:
        print(f"An error occurred while updating entry {entry_id}: {e}")
        raise
    finally:
        close_connection()
