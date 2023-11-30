import asyncio
import importlib
import os
import sqlite3
from bots.tejarat_bot import tejarat_update_database 
script_directory = os.path.dirname(os.path.abspath(__file__))
bank_database_path = os.path.join(script_directory, 'bank_database.sqlite3')
database_path=os.path.join(script_directory, 'database.sqlite3')

async def login(desCard:str):
    bank_name = bank_finder(bank_database_path,desCard)
    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
      
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
        
        # Get the login functions dynamically
            login_function = getattr(bot_module, f"{bank_name.lower()}_login", None)
       
            if login_function:
                 login_function()
            else:
                print(f"No login function found for account name: {bank_name}")

        except ImportError:
            print(f"No bot module found for account name: {bank_name}")
    else:
        print(f"No record found for the card number {desCard}")

async def refresh(desCard:str):
    bank_name = bank_finder(bank_database_path,desCard)
    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
      
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
        
        # Get the refresh functions dynamically
            refresh_function = getattr(bot_module, f"{bank_name.lower()}_refresh", None)
       
            if refresh_function:
                 await refresh_function()
            else:
                print(f"No refresh function found for account name: {bank_name}")

        except ImportError:
            print(f"No bot module found for account name: {bank_name}")
    else:
        print(f"No record found for the card number {desCard}")

def check_login(desCard:str):
    bank_name = bank_finder(bank_database_path,desCard)
    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
      
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
        
        # Get the check_login functions dynamically
            check_login_function = getattr(bot_module, f"{bank_name.lower()}_check_login", None)
       
            if check_login_function:
                  check_login_function()
            else:
                print(f"No check_login function found for account name: {bank_name}")

        except ImportError:
            print(f"No bot module found for account name: {bank_name}")
    else:
        print(f"No record found for the card number {desCard}")

async def update_database(desCard:str,semaphore: asyncio.Semaphore, startDate: str, endDate: str, startTime: str, endTime: str):
    
    bank_name = bank_finder(database_path,desCard)

    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
      
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
        
        # Get the update_database functions dynamically
            
            update_function = getattr(bot_module, f"{bank_name.lower()}_update_database", None)
       

            if update_function:
                await update_function(semaphore,startDate,endDate,startTime,endDate)
            else:
                print(f"No update function found for account name: {bank_name}")

        except ImportError:
            print(f"No bot module found for account name: {bank_name}")
    else:
        print(f"No record found for the card number {desCard}")

def bank_finder(database_path, card_number):

    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Execute a query to find the account_name based on the card_number
    cursor.execute('SELECT account_number FROM accounts WHERE card_number = ?', (card_number,))

    # Fetch the result
    result = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Return the account_name if found, otherwise return None
    return result[0] if result else None


