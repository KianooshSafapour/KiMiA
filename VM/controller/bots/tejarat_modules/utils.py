
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ES


def set_date(driver , startdate_element_locator,enddate_elemet_locator , start,end):
    WebDriverWait(driver, 30).until(ES.element_to_be_clickable(startdate_element_locator))
    startdate_element = driver.find_element(*startdate_element_locator)
    ES.element_to_be_clickable(enddate_elemet_locator)
    enddate_element = driver.find_element(*enddate_elemet_locator)
    startdate_element.clear()
    startdate_element.send_keys(f"{start}")
    enddate_element.clear()
    enddate_element.send_keys(f"{end}")

def set_time(driver , starttime_element_locator,endtime_elemet_locator , start,end):
    WebDriverWait(driver, 30).until(ES.element_to_be_clickable(starttime_element_locator))
    starttime_element = driver.find_element(*starttime_element_locator)
    ES.element_to_be_clickable(endtime_elemet_locator)
    endtime_element = driver.find_element(*endtime_elemet_locator)
    starttime_element.clear()
    starttime_element.send_keys(f"{start}")
    endtime_element.clear()
    endtime_element.send_keys(f"{end}")