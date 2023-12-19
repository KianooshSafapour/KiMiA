import asyncio
import importlib
import os
import sqlite3
from utils.bank_finder import bank_finder

script_directory = os.path.dirname(os.path.abspath(__file__))
bank_database_path = os.path.join(script_directory, 'bank_database.sqlite3')
database_path=os.path.join(script_directory, 'database.sqlite3')

async def login(driver,card_number):

    connection = sqlite3.connect(bank_database_path)  
    cursor = connection.cursor()

    try:
        # Step 1: Get account_number from accounts table
        cursor.execute("SELECT * FROM accounts WHERE card_number = ?", (card_number,))
        account_row = cursor.fetchone()

        if account_row:
            account_number = account_row[1]
            account_username =account_row[3]
            account_pass = account_row[4]

            # Step 2: Get bank_name from bank table using account_number
            cursor.execute("SELECT * FROM banks WHERE id = ?", (account_number,))
            bank_row = cursor.fetchone()

            if bank_row:
                bank_name = bank_row[1]
                bank_url = bank_row[2]
                bank_config = bank_row[3]

                
            else:
                print(f"No bank record found for account_number {account_number}")
                return {'status':'failure','message':'No bank record found'}
                
        else:
            print(f"No account record found for card_number {card_number}")
            return {'status':'failure','message':'No account record found'}
            

    except sqlite3.Error as e:
        print("SQLite error:", e)
        return {'status':'failure','message':'database error'}
        

    finally:
        # Close the database connection
        connection.close()    
    
    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
      
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
        
        # Get the login functions dynamically
            login_function = getattr(bot_module, f"{bank_name.lower()}_login", None)
       
            if login_function:
                 print("####################################login_function ok")
                 reuslt =await login_function(driver,bank_url,account_username,account_pass)
                 return reuslt
            else:
                print(f"No login function found for account name: {bank_name}")
                return {"status": "failure", "message": "No bank found for this card number"}


        except ImportError:
            print(f"No bot module found for account name: {bank_name}")
    else:
        return {"status": "failure", "message": "No record found for the card number"}
        print(f"No record found for the card number {desCard}")

async def refresh(driver,desCard):
   
    bank_name = bank_finder(desCard)
    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
      
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
        
        # Get the refresh functions dynamically
            refresh_function = getattr(bot_module, f"{bank_name.lower()}_refresh", None)
       
            if refresh_function:
                result = await refresh_function(driver)
                return result
            else:
                print(f"No refresh function found for account name: {bank_name}")

        except ImportError:
            print(f"No bot module found for account name: {bank_name}")
    else:
        print(f"No record found for the card number {desCard}")

async def check_login(driver,card_number):
    
    bank_name = bank_finder(card_number)
    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
      
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
        
        # Get the check_login functions dynamically
            check_login_function = getattr(bot_module, f"{bank_name.lower()}_check_login", None)
       
            if check_login_function:
                result= await check_login_function(driver)
                return result
            else:
                print( f"No check_login function found for account name: {bank_name}")
                return {'status':'failure','message':'No check_login function found for account name'}

        except ImportError:
            print(f"No bot module found for account name: {bank_name}")
            return {'status':'failure','message':'No bot module found for account name'}
    else:
        print(f"No record found for the card number {card_number}")
        return {'status':'failure','message':'No record found for the card number'}

async def update_database(driver, desCard:str, from_date: str, from_time: str, to_date: str, to_time: str):
    print("###############update_database####################")
    bank_name = bank_finder(desCard)

    if bank_name:
        bot_module_name = f"{bank_name.lower()}_bot"
        try:
            # Import the module dynamically
            bot_module = importlib.import_module(f"bots.{bot_module_name}")
            # Get the update_database functions dynamically
            update_function = getattr(bot_module, f"{bank_name.lower()}_update_database", None)
            if update_function:
                print(f"########################################update_functionupdate_functionupdate_function##{from_date}##{to_date}##{to_time}")
                result = await update_function(driver, from_date, from_time, to_date, to_time)
                return result
            else:
                return {"status":"failure","message":f"No update function found for account name: {bank_name}"}
        except ImportError:
            return {"status":"failure","message":f"No bot module found for account name: {bank_name}"}

    else:
        return {"status":"failure","message":f"No record found for the card number {desCard}"}
 



