import time
import pandas as pd
import Scraper as s



driver = s.init_driver("C:/Users/austi/Documents/Github_Repos/Imperial_Applied_Project/ChromeDriver/chromedriver.exe")

# Go to www.zillow.com/homes
s.navigate_to_website(driver, "https://www.zillow.com/homes/48126_rb/")




s.close_connection(driver)