from selenium import webdriver

PATH = "chromedriver.exe"
driver = webdriver.Chrome()

driver.get("https://www.maersk.com/schedules/pointToPoint")

time.sleep(2)
drive.close()
