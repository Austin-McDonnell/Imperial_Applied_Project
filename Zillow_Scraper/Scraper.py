import re as re
import numpy as np
import time
#import zipcode
import zipcodes
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


def init_driver(file_path):
    # Starting maximized fixes https://github.com/ChrisMuir/Zillow/issues/1
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(executable_path=file_path,
                              chrome_options=options)
    driver.wait = WebDriverWait(driver, 10)
    return(driver)

# Helper function for checking for the presence of a web element.
def _is_element_displayed(driver, elem_text, elem_type):
    if elem_type == "class":
        try:
            out = driver.find_element_by_class_name(elem_text).is_displayed()
        except (NoSuchElementException, TimeoutException):
            out = False
    elif elem_type == "css":
        try:
            out = driver.find_element_by_css_selector(elem_text).is_displayed()
        except (NoSuchElementException, TimeoutException):
            out = False
    else:
        raise ValueError("arg 'elem_type' must be either 'class' or 'css'")
    return(out)


# If captcha page is displayed, this function will run indefinitely until the
# captcha page is no longer displayed (checks for it every 30 seconds).
# Purpose of the function is to "pause" execution of the scraper until the
# user has manually completed the captcha requirements.
def _pause_for_captcha(driver):
    while True:
        time.sleep(30)
        if not _is_element_displayed(driver, "captcha-container", "class"):
            break

# Check to see if the page is currently stuck on a captcha page. If so, pause
# the scraper until user has manually completed the captcha requirements.
def check_for_captcha(driver):
    if _is_element_displayed(driver, "captcha-container", "class"):
        print("\nCAPTCHA!\n"\
              "Manually complete the captcha requirements.\n"\
              "Once that's done, if the program was in the middle of scraping "\
              "(and is still running), it should resume scraping after ~30 seconds.")
        _pause_for_captcha(driver)

def navigate_to_website(driver, site):
    driver.get(site)
    # Check to make sure a captcha page is not displayed.
    check_for_captcha(driver)

def get_html(driver):
    output = []
    keep_going = True
    while keep_going:
        # Pull page HTML
        try:
            output.append(driver.page_source)
        except TimeoutException:
            pass
        # Check to see if a "next page" link exists.
        keep_going = _is_element_displayed(driver, "zsg-pagination-next",
                                           "class")
        if keep_going:
            # Test to ensure the "updating results" image isnt displayed.
            # Will try up to 5 times before giving up, with a 5 second wait
            # between each try.
            tries = 5
            cover = _is_element_displayed(driver,
                                          "list-loading-message-cover",
                                          "class")
            while cover and tries > 0:
                time.sleep(5)
                tries -= 1
                cover = _is_element_displayed(driver,
                                              "list-loading-message-cover",
                                              "class")
            # If the "updating results" image is confirmed to be gone
            # (cover == False), click next page. Otherwise, give up on trying
            # to click thru to the next page of house results, and return the
            # results that have been scraped up to the current page.
            if not cover:
                try:
                    driver.wait.until(EC.element_to_be_clickable(
                        (By.CLASS_NAME, "zsg-pagination-next"))).click()
                    time.sleep(3)
                    # Check to make sure a captcha page is not displayed.
                    check_for_captcha(driver)
                except TimeoutException:
                    keep_going = False
            else:
                keep_going = False
    return(output)

# Teardown webdriver.
def close_connection(driver):
    driver.quit()