# ftchr.py

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

class BankBot:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.driver = webdriver.Chrome()  # You might need to adjust the webdriver
        self.last_activity_time = time.time()

    def login(self):
        self.driver.get(self.url)
        # Your login logic here
        # ...

    def download_csv(self):
        # Logic to download the CSV file
        # ...

    def stay_logged_in(self):
        while True:
            elapsed_time = time.time() - self.last_activity_time

            if elapsed_time >= 900:  # 15 minutes
                self.driver.find_element_by_link_text("Home").click()
                self.last_activity_time = time.time()

            # Check for commands from ctrl.py
            # If ctrl.py has sent a command, reset the timer
            if self.check_for_ctrl_command():
                self.last_activity_time = time.time()
                self.download_csv()  # Run download_csv function
                    self.stay_logged_in()  # After download_csv, run stay_logged_in

            time.sleep(60)  # Sleep for 1 minute to avoid excessive polling

    def run_sequence(self):
        self.login()
        self.download_csv()
        self.stay_logged_in()

    def ctrl_download_csv(self):
        # Method to be called by ctrl.py to trigger download_csv function
        self.last_activity_time = time.time()
        self.download_csv()
        self.stay_logged_in()  # Run stay_logged_in after download_csv

# Example usage:
# bot = BankBot("https://bank.com", "your_username", "your_password")
# bot.run_sequence()
# To use download_csv from ctrl.py:
# bot.ctrl_download_csv()
