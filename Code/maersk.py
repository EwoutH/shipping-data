from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

list_ports_sa = ['1BX66GARX9UAH']
list_ports_eu = ['1JUKNJGWHQBNJ']

PATH = "chromedriver.exe"
driver = webdriver.Chrome()

driver.get("https://www.maersk.com/schedules/pointToPoint?from=1BX66GARX9UAH&to=1JUKNJGWHQBNJ&containerIsoCode=42G1&fromServiceMode=CY&toServiceMode=CY&numberOfWeeks=4&dateType=D&date=2022-10-12&vesselFlag=")
driver.implicitly_wait(2)
driver.find_element(By.XPATH,"//*[@id='coiPage-1']/div[2]/button[3]").click()

driver.implicitly_wait(2)
buttons = driver.find_elements(By.CLASS_NAME, 'button button--link show-details-link')
print(buttons)
for button in buttons:
    print(1)
    button.click()

page_source = driver.page_source

time.sleep(3)
#driver.close()

soup = BeautifulSoup(page_source)

print(soup)

