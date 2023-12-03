import sqlite3
import random
from datetime import datetime, timedelta

# Connect to the SQLite database (create it if it doesn't exist)
conn = sqlite3.connect('database.sqlite3')
cursor = conn.cursor()

# Create a transactions table (modify this based on your actual table structure)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        customer_card INTEGER,
        account_card INTEGER,
        transaction_confirmation INTEGER,
        transaction_time TEXT,
        transaction_date TEXT
    )
''')

# Create a log table (modify this based on your actual table structure)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS log (
        id INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        status TEXT,
        log_message TEXT
    )
''')

# Function to generate a random 16-digit integer
def generate_random_16_digit():
    return random.randint(10**15, 10**16 - 1)

# Function to generate a random 12-digit integer
def generate_random_12_digit():
    return random.randint(10**11, 10**12 - 1)

# Function to generate a random time in HH:MM:SS format
def generate_random_time():
    return (datetime.min + timedelta(minutes=random.randint(0, 24*60-1))).time().strftime('%H:%M:%S')

# Function to generate a random date in DD/MM/YYYY format
def generate_random_date():
    return datetime.today().strftime('%d/%m/%Y')

# Function to insert a transaction and log entry
def insert_transaction_and_log():
    customer_card = generate_random_16_digit()
    account_card = generate_random_16_digit()
    transaction_confirmation = generate_random_12_digit()
    transaction_time = generate_random_time()
    transaction_date = generate_random_date()

    # Insert into transactions table
    cursor.execute('''
        INSERT INTO transactions
        (customer_card, account_card, transaction_confirmation, transaction_time, transaction_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (customer_card, account_card, transaction_confirmation, transaction_time, transaction_date))

    # Insert into log table
    cursor.execute('''
        INSERT INTO log (date, time, status, log_message)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().strftime('%d/%m/%Y'), datetime.now().strftime('%H:%M:%S'), 'Success', 'Transaction added successfully'))

    # Commit changes
    conn.commit()

# Insert 5 transactions with logs for each
for _ in range(100):
    insert_transaction_and_log()

# Close the connection
conn.close()
