
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
from selenium.common.exceptions import TimeoutException
import time
from jdatetime import date
from jdatetime import datetime, timedelta
import asyncio
from .tejarat_modules.csv_handler import Transaction, TransactionDB
from bots.tejarat_modules.utils import set_date ,set_time

chrome_driver_path = './chromedriver.exe'
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(executable_path=chrome_driver_path)

def tejarat_login():
    driver.get("https://ib.tejaratbank.ir/web/ns/login?execution=e1s1")
    driver.maximize_window()

    element =driver.find_element(By.CSS_SELECTOR,'span.ui-icon-closethick')
    element.click()
    user_name_box =driver.find_element(By.ID,'loginForm:userName')
    user_name_box.send_keys("4360425678")
    password=driver.find_element(By.ID,"loginForm:password")
    password.send_keys("Milad@1937")
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

async def tejarat_refresh():
    dropdown_items_locator = (By.XPATH, "//a[contains(text(), 'صورت حساب متمرکز (نسخه آزمایشی)')]")
    dropdown_item = WebDriverWait(driver, 10).until(ES.element_to_be_clickable(dropdown_items_locator))
        # Click on the dropdown item
    dropdown_item.click()
    dropdown_item =await WebDriverWait(driver, 10).until(ES.element_to_be_clickable(dropdown_items_locator))
    
def tejarat_check_login():
    driver.execute_script("window.scrollTo(0, 0);")
    dropdown_items_locator = (By.XPATH, "//a[contains(text(), 'صورت حساب متمرکز (نسخه آزمایشی)')]")
    status =ES.element_to_be_clickable(dropdown_items_locator)
    return status

async def tejarat_update_database(semaphore: asyncio.Semaphore, startDate: str, endDate: str, startTime: str, endTime: str):
    driver.execute_script("window.scrollTo(0, 0);")
    fromDate_locator = (By.ID, "pageForm:fromDate")
    toDate_locator = (By.ID, "pageForm:toDate")
    

    # Format the date as a string
    
    set_date(driver, fromDate_locator,toDate_locator,startDate,endDate)
                


    fromTime_locator = (By.ID, "pageForm:fromTime_input")
    toTime_locator = (By.ID, "pageForm:toTime_input")
    

    
    

    set_time(driver, fromTime_locator,toTime_locator,startTime,endTime)
    show_transaction_btn = (By.ID, "pageForm:j_id1971464148_2_52dad71c")  # Replace "your_button_id" with the actual ID of the button
    button = WebDriverWait(driver, 10).until(ES.element_to_be_clickable(show_transaction_btn))
    button.click()
    taction = Transaction()
    transaction_list =await taction.csv_handner(driver)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(script_directory, 'database.sqlite3')
    #get tcn list from db to check for dublicated transactions in transaction_list
    async with semaphore:
        db = TransactionDB(database_path)
        async with db.execute("SELECT tcn FROM transactions") as cursor:
            # Fetch all transactions
            tcn_list = await cursor.fetchall()
        db.connection.close()
    #remove dublocate transactions
    filtered_transactions=[trans for trans in transaction_list if trans.payment_id not in tcn_list]
    #add new transactions to db
    async with semaphore:
        db = TransactionDB(database_path)
        for transact in filtered_transactions:
            await db.execute('INSERT INTO transaction_table (from_card, to_card, payment_id, pay_date, pay_time) VALUES (?, ?, ?, ?, ?)',
                   (transact.from_card, transact.to_card, transact.payment_id, transact.pay_date, transact.pay_time))
        db.connection.close()

        
