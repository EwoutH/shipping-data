from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

#list of ports in south america
list_ports_sa = ['1BX66GARX9UAH']
#list of ports in EU
list_ports_eu = ['1JUKNJGWHQBNJ']

PATH = "chromedriver.exe"
driver = webdriver.Chrome()

#Open Maersk point to point site from SA to EU
driver.get("https://www.maersk.com/schedules/pointToPoint?from=1BX66GARX9UAH&to=1JUKNJGWHQBNJ&containerIsoCode=42G1&fromServiceMode=CY&toServiceMode=CY&numberOfWeeks=4&dateType=D&date=2022-10-12&vesselFlag=")
driver.implicitly_wait(2)
#Click to allow cookies
driver.find_element(By.XPATH,"//*[@id='coiPage-1']/div[2]/button[3]").click()

driver.implicitly_wait(2)
#This list contains all the Xpaths to the buttons that expand the route details
list_xpath_routedetails =["//*[@id='app']/div[2]/div[1]/div[3]/div/div[4]/button/span","//*[@id='app']/div[2]/div[1]/div[4]/div/div[4]/button/span","//*[@id='app']/div[2]/div[1]/div[5]/div/div[4]/button/span",
                          "//*[@id='app']/div[2]/div[1]/div[6]/div/div[4]/button/span","//*[@id='app']/div[2]/div[1]/div[7]/div/div[4]/button/span"]

#Clicks the buttons to expand the route details
for i in list_xpath_routedetails:
    driver.find_element(By.XPATH,i).click()

#Copy's the page to use in Beautifulsoup
page_source = driver.page_source

#Closes the webdriver after a few seconds
time.sleep(5)
driver.quit()

soup = BeautifulSoup(page_source)

print(soup)

