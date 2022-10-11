from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

PATH = "chromedriver.exe"
driver = webdriver.Chrome()

driver.get("https://www.maersk.com/schedules/pointToPoint?from=1JUKNJGWHQBNJ&to=1BX66GARX9UAH&containerIsoCode=42G1&fromServiceMode=CY&toServiceMode=CY&numberOfWeeks=4&dateType=D&date=2022-10-12&vesselFlag=")
driver.implicitly_wait(2)
driver.find_element(By.XPATH,"//*[@id='coiPage-1']/div[2]/button[3]").click()

time.sleep(5)
#driver.close()
