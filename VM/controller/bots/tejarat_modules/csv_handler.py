import csv
import os
import sqlite3
import pandas as pd
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import aiosqlite

class TransactionModel():
   def __init__(self, from_card, to_card, payment_id, pay_date, pay_time):
        self.from_card = from_card
        self.to_card = to_card
        self.payment_id = payment_id
        self.pay_date = pay_date
        self.pay_time = pay_time

'''
class TransactionDB:
    
    def __init__(self,database_path):
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        # Create a table if it doesn't exist
        self.cursor.execute(
            CREATE TABLE IF NOT EXISTS transactions (
                "id" INTEGER NOT NULL,
	            "ccn" VARCHAR(16) NOT NULL DEFAULT '',
	            "acn" VARCHAR(16) NOT NULL DEFAULT '',
	            "tcn" VARCHAR(20) NOT NULL DEFAULT '',
	            "date" VARCHAR(10) NOT NULL DEFAULT '',
	            "time" VARCHAR(10) NOT NULL DEFAULT '',
	            PRIMARY KEY ("id")
            )
        )
        self.connection.commit()

    def __del__(self):
        # Close the database connection when the object is deleted
        self.connection.close()
'''
class TransactionDB:
    
    def __init__(self, database_path):
        self.connection = None
        self.cursor = None
        self.database_path = database_path

    async def __aenter__(self):
        self.connection = await aiosqlite.connect(self.database_path)
        self.cursor = await self.connection.cursor()
        return self.cursor

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.connection.commit()
        await self.connection.close()


class Transaction():
    
    fromCard=""
    toCard=""
    paymentID=0
    payDate=""
    payTime=""


    def description_handler(self,des):
        
        fromCard_patern = r"از کارت:(\d+)"
        toCard_patern = r"به کارت:(\d+)"
        paymentID_patern = r"شماره‌پي‌گيري:(\d+)"
    # Print the unique values
        
            
        # Find matches using regular expressions
        if "انتقال کارت به کارت" in des:
            search_fromCard= re.search(fromCard_patern, des)
            search_toCard= re.search(toCard_patern, des)
            search_paymentID = re.search(paymentID_patern, des)

        # Extract numbers from matches
            self.fromCard = str(int(search_fromCard.group(1))) if search_fromCard else None
            if self.fromCard==None: return False
            self.toCard  = str(int(search_toCard.group(1))) if search_toCard else None
            self.paymentID  = str(int(search_paymentID.group(1))) if search_paymentID else None
            return True
        else:
            return False



    async def csv_handler(self,driver):
        WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.ID, "progressAnimator_start"))
    )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        button_locator = (By.ID, "pageForm:j_id1971464148_2_52dadad1_exportToCsv")
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button_locator))
    
    # Click the button
        button.click()

        time.sleep(3)

        home_directory = os.path.expanduser("~")

    # Specify the path to your CSV file in the Downloads folder
        downloads_folder = os.path.join(home_directory, 'Downloads')

    # List all files in the Downloads folder
        all_files = os.listdir(downloads_folder)

    # Filter only CSV files
        csv_files = [file for file in all_files if file.endswith('.csv')]

    # If there are CSV files
        if csv_files:
            # Get the latest CSV file based on modification time
            latest_csv_file = max(csv_files, key=lambda x: os.path.getmtime(os.path.join(downloads_folder, x)))

            # Specify the path to the latest CSV file
            csv_file_path = os.path.join(downloads_folder, latest_csv_file)

            # Read CSV file into a pandas DataFrame
            df = pd.read_csv(csv_file_path, header=None)
            

            # Remove empty rows
            df = df.dropna(how='all')

            # Remove extra spaces
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Remove empty columns
            df = df.dropna(axis=1, how='all')
            
            # Print the cleaned DataFrame
            columns_to_extract = [ 1, 8, 14, 19,21]
            
            transaction = df.iloc[:, columns_to_extract]

            transaction = transaction.dropna(how='all')

           
            new_column_names = ['کد رهگیری', 'توضیح عملیات', 'واریز', 'زمان', 'تاریخ']
            transaction.columns = new_column_names

            transaction = transaction.iloc[1:, :]
            transaction_list=[]
            
            
            for invoice in transaction.iloc:
                print(invoice["زمان"])
                status = self.description_handler(invoice["توضیح عملیات"])
                self.payDate =invoice["تاریخ"]
                self.payTime =invoice["زمان"]
                self.paymentID =invoice["کد رهگیری"]

                if status :
                    transaction_list.append(TransactionModel(from_card=self.fromCard,to_card=self.toCard,payment_id=self.paymentID,pay_date=self.payDate,pay_time=self.payTime))
                    
            print(f"###############{transaction_list[0].from_card}::::{transaction_list[0].to_card}")
            print(f"###############transaction_list len:::::{len(transaction_list)}")
            return transaction_list
                    #db = TransactionDB(database_path)
                    #db.save_to_db(ccn=self.fromCard,acn=self.toCard,tcn=self.paymentID,time=self.payTime,date=self.payDate,paymentID=self.paymentID)
            
