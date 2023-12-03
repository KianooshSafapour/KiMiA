from cgi import print_directory
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ES
import asyncio
from .tejarat_modules.csv_handler import Transaction, TransactionDB
from bots.tejarat_modules.utils import set_date ,set_time
    
async def tejarat_login(driver):
    
    driver.get("https://ib.tejaratbank.ir/web/ns/login?execution=e1s1")
    driver.maximize_window()

    element =driver.find_element(By.CSS_SELECTOR,'span.ui-icon-closethick')
    element.click()
    user_name_box =driver.find_element(By.ID,'loginForm:userName')
    user_name_box.send_keys("0015440222")
    password=driver.find_element(By.ID,"loginForm:password")
    password.send_keys("@@K!4N00$h")
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

async def tejarat_refresh(driver):
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
    dropdown_item = WebDriverWait(driver, 10).until(ES.element_to_be_clickable(dropdown_items_locator))
    if dropdown_item:
        return {"status": "success", "message": "refresh successful"}
    else : return {"status": "failure", "message": "re faild , couldnt reach required steps"}
    
def tejarat_check_login(driver):
    dropdown_locator = (By.XPATH, "//a[contains(text(), 'اطلاعات حساب')]")
    WebDriverWait(driver, 100).until(ES.element_to_be_clickable(dropdown_locator))

        # Locate the dropdown element
    dropdown = driver.find_element(*dropdown_locator)

        # Click on the dropdown to open the options
    dropdown.click()

    driver.execute_script("window.scrollTo(0, 0);")
    dropdown_items_locator = (By.XPATH, "//a[contains(text(), 'صورت حساب متمرکز (نسخه آزمایشی)')]")
    status =ES.element_to_be_clickable(dropdown_items_locator)
    if status:
        return {"status": "success", "message": "bank account is logined successfully"}
    else: return {"status": "failure", "message": "bank account functions are note reachable"}

async def tejarat_update_database(driver, semaphore: asyncio.Semaphore, from_date: str, from_time: str, to_date: str, to_time: str):
    try:
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

        script_directory = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(script_directory, 'database.sqlite3')

        # Retrieve existing transactions from the database
        async with semaphore:
            db = TransactionDB(database_path)
            async with db.execute("SELECT tcn FROM transactions") as cursor:
                tcn_list = await cursor.fetchall()
            db.connection.close()

        # Remove duplicate transactions
        filtered_transactions = [trans for trans in transaction_list if trans.payment_id not in tcn_list]

        # Add new transactions to the database
        async with semaphore:
            db = TransactionDB(database_path)
            for transact in filtered_transactions:
                await db.execute('INSERT INTO transaction_table (from_card, to_card, payment_id, pay_date, pay_time) VALUES (?, ?, ?, ?, ?)',
                                 (transact.from_card, transact.to_card, transact.payment_id, transact.pay_date, transact.pay_time))
            db.connection.close()
            return {'status': 'success','message':'successfully database updated'}
    except Exception as e:
        # Handle exceptions and log the error
        print(f"An error occurred: {e}")
        return {'status': 'failure','message':f'{e}'}
        # You can add more specific exception handling based on the type of exception if needed
