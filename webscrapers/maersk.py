from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys #currently not used
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

#chromedriver is started once.
#The browser version is stored. This will be used for the user agent in the actual driver
opts = Options()
opts.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
version = driver.capabilities['browserVersion']
driver.quit()

#sets up the options of the chromedriver
opts = Options()
opts.add_argument("window-size=1280,720") #locks the window size
version = driver.capabilities['browserVersion']
opts.add_argument("user-agent=Chrome/version {}") #Prevents sites from blocking traffic
headless = True
if headless: #if True, open chrome on the background without window
    opts.headless = True

driver.quit()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

#Open Maersk point to point site
driver.get("https://www.maersk.com/schedules/pointToPoint")
driver.implicitly_wait(2)
#Click to allow cookies
driver.find_element(By.XPATH,"//*[@id='coiPage-1']/div[2]/button[3]").click()

#fill in the origin location
originloc = driver.find_element(By.ID,'originLocation')
originloc.send_keys("Santos (Sao Paulo), Brazil")

#a dropdown menu has to be clicked. This clicks the correct port
time.sleep(2) #Makes sure that the element is actually clickable
action = ActionChains(driver)
action.move_to_element_with_offset(originloc, 0, 50)
action.click()
action.perform()

destinationloc = driver.find_element(By.ID,'destinationLocation')
destinationloc.send_keys("Rotterdam")

time.sleep(2)
action = ActionChains(driver)
action.move_to_element_with_offset(destinationloc, 0, 50)
action.click()
action.perform()

#Click the search button
search_button = driver.find_element(By.XPATH,'//*[@id="app"]/div[2]/span/form/div[6]/button')
search_button.click()

#This list contains all the Xpaths to the buttons that expand the route details
list_xpath_routedetails =["//*[@id='app']/div[2]/div[1]/div[3]/div/div[4]/button/span","//*[@id='app']/div[2]/div[1]/div[4]/div/div[4]/button/span","//*[@id='app']/div[2]/div[1]/div[5]/div/div[4]/button/span",
                          "//*[@id='app']/div[2]/div[1]/div[6]/div/div[4]/button/span","//*[@id='app']/div[2]/div[1]/div[7]/div/div[4]/button/span"]

time.sleep(3)
#Clicks the buttons to expand the route details
for i in list_xpath_routedetails:
    driver.find_element(By.XPATH,i).click()

#Copy's the page to use in Beautifulsoup
page_source = driver.page_source
soup = BeautifulSoup(page_source)

#Closes the webdriver after a few seconds
#driver.quit()

routes = soup.find_all("div", class_="ptp-results__transport-plan")
route = routes[0]

origin = route.find("div", class_="ptp-results__transport-plan--item")

origin = origin.find(class_="font--small").text

print(origin)

destination = route.find(class_="ptp-results__transport-plan--item-final")

destination = destination.find(class_="font--small").text

print(destination)