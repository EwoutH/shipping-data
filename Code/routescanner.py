from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

PATH = "chromedriver.exe"
driver = webdriver.Chrome()

driver.get("https://www.routescanner.com/")
driver.implicitly_wait(4)
driver.find_element(By.CLASS_NAME,"acceptButton__P2szu").click()

origin = driver.find_element(By.ID,'origin')
origin.send_keys('Port of Santos')

destination = driver.find_element(By.ID,'destination')
destination.send_keys('Rotterdam')

driver.find_element(By.CLASS_NAME,"action__AmI8m large__bknlX floatRight__GXlT1 pulse__o5bSr").click()

time.sleep(5)
#driver.close()
