import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ES
import asyncio
from .tejarat_modules.csv_handler import Transaction, TransactionDB
from bots.tejarat_modules.utils import set_date ,set_time

async def tejarat_login(driver,bank_url,account_username,account_pass):
    


    try:
        driver.get(bank_url)
        driver.maximize_window()

        element =driver.find_element(By.CSS_SELECTOR,'span.ui-icon-closethick')
        element.click()
        user_name_box =driver.find_element(By.ID,'loginForm:userName')
        user_name_box.send_keys(account_username)
        password=driver.find_element(By.ID,"loginForm:password")
        password.send_keys(account_pass)
        dropdown_locator = (By.XPATH, "//a[contains(text(), 'اطلاعات حساب')]")
        WebDriverWait(driver, 100).until(ES.element_to_be_clickable(dropdown_locator))

            # Locate the dropdown element
        dropdown = driver.find_element(*dropdown_locator)

            # Click on the dropdown to open the options
        dropdown.click()

        dropdown_items_locator = (By.XPATH, "//a[contains(text(), 'صورت حساب متمرکز (نسخه آزمایشی)')]")
        dropdown_item = WebDriverWait(driver, 10).until(ES.element_to_be_clickable(dropdown_items_locator))
            # Click on the dropdown item
        dropdown_item.click()
        
        return {"status": "success", "message": "Login successful"}
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return  {"status": "failure", "message": "bank page error"}
        
async def tejarat_refresh(driver):
    try:
        WebDriverWait(driver, 30).until(
        ES.invisibility_of_element_located((By.ID, "progressAnimator_start"))
        )
        dropdown_locator = (By.XPATH, "//a[contains(text(), 'اطلاعات حساب')]")
        WebDriverWait(driver, 5).until(ES.element_to_be_clickable(dropdown_locator))

            # Locate the dropdown element
        dropdown = driver.find_element(*dropdown_locator)

            # Click on the dropdown to open the options
        dropdown.click()

        dropdown_items_locator = (By.XPATH, "//a[contains(text(), 'صورت حساب متمرکز (نسخه آزمایشی)')]")
        dropdown_item = WebDriverWait(driver, 10).until(ES.element_to_be_clickable(dropdown_items_locator))
            # Click on the dropdown item
        dropdown_item.click()
        dropdown_item = WebDriverWait(driver, 10).until(ES.element_to_be_clickable(dropdown_items_locator))
        
        return {"status": "success", "message": "refresh successful"}
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return  {"status": "failure", "message": "re faild , couldnt reach required steps"}

async def tejarat_check_login(driver):
    try:
        WebDriverWait(driver, 30).until(
            ES.invisibility_of_element_located((By.ID, "progressAnimator_start"))
        )
        dropdown_locator = (By.XPATH, "//a[contains(text(), 'اطلاعات حساب')]")
        dropdown_status=WebDriverWait(driver, 9).until(ES.element_to_be_clickable(dropdown_locator))
        
        if dropdown_status:
            print(dropdown_status)
        else:return {"status": "failure", "message": "bank account functions are note reachable"}

        driver.execute_script("window.scrollTo(0, 0);")
        dropdown_items_locator = (By.XPATH, "//a[contains(text(), 'صورت حساب متمرکز (نسخه آزمایشی)')]")
        ES.element_to_be_clickable(dropdown_items_locator)
       
        return {"status": "success", "message": "bank account is logined successfully"}
     
    except Exception as e:
        # Handle exceptions and log the error
        print(f"An error occurred: {e}")
        return {'status': 'failure','message':f'{e}'}

async def tejarat_update_database(driver, from_date: str, from_time: str, to_date: str, to_time: str):
    print("################################################tejarat_update_database##################################")
    try:
        WebDriverWait(driver, 30).until(
        ES.invisibility_of_element_located((By.ID, "progressAnimator_start"))
        )
        driver.execute_script("window.scrollTo(0, 0);")
        fromDate_locator = (By.ID, "pageForm:fromDate")
        toDate_locator = (By.ID, "pageForm:toDate")

        # Format the date as a string
        set_date(driver, fromDate_locator, toDate_locator, from_date, to_date)

        fromTime_locator = (By.ID, "pageForm:fromTime_input")
        toTime_locator = (By.ID, "pageForm:toTime_input")

        set_time(driver, fromTime_locator, toTime_locator, from_time, to_time)

        show_transaction_btn = (By.ID, "pageForm:j_id1971464148_2_52dad71c")  # Replace with the actual ID
        button = WebDriverWait(driver, 10).until(ES.element_to_be_clickable(show_transaction_btn))
        button.click()

        transaction = Transaction()
        transaction_list = await transaction.csv_handler(driver)
        print("#################before getting tcn")
        script_directory = os.path.dirname(os.path.abspath(__file__))
        controller_directory = os.path.dirname(script_directory)
        database_path = os.path.join(controller_directory, 'database.sqlite3')


        # Retrieve existing transactions from the database
        
        
        async with TransactionDB(database_path) as db:
            async with await db.execute("SELECT tcn FROM transactions") as cursor:
                tcn_list = await cursor.fetchall()

        print("#################tcn gotten")
        print(f"#################{tcn_list}")

        # Remove duplicate transactions
        # Assuming transaction_list is defined somewhere in your code
        filtered_transactions = [trans for trans in transaction_list if trans.payment_id not in tcn_list]
        print(f"##########################filtered_transactions:::::{filtered_transactions}")

        # Add new transactions to the database
        async with TransactionDB(database_path) as db:
            for transact in filtered_transactions:
                await db.execute('INSERT INTO transactions (ccn, acn, tcn, date, time) VALUES (?, ?, ?, ?, ?)',
                                (transact.from_card, transact.to_card, transact.payment_id, transact.pay_date, transact.pay_time))

        return {'status': 'success','message':'successfully database updated'}
    except Exception as e:
        # Handle exceptions and log the error
        print(f"An error occurred: {e}")
        return {'status': 'failure','message':f'{e}'}
        # You can add more specific exception handling based on the type of exception if needed
