from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import itertools
import pandas as pd
from time import sleep
from datetime import date
import os

# Create list of origin and destination ports
o_ports = ['BRFOR', 'BRSSZ', 'BRPEC', 'BRSSA', 'BRPNG', 'BRRIO', 'BRRIG', 'BRITJ', 'BRNAT', 'COCTG', 'COSMR', 'COTRB', 'SRPBM', 'CWWIL', 'UYMVD', 'ARBUE', 'CLCNL', 'CLSAI', 'CLVAP', 'PEPAI', 'PECLL', 'ECGYE', 'ECPBO', 'ECPSJ', 'VNVUT', 'VNCMT']
d_ports = ['NLRTM', 'BEANR', 'NLVLI', 'BEZEE', 'NLAMS']
# Make list with all combinations
od_ports = list(itertools.product(o_ports, d_ports))

# Define the base URL to search
url = "https://www.msc.com/en/search-a-schedule"

# Get today's date
today = date.today()
print(today)

# Define search criteria
direct = True


def get_soups(od_ports=od_ports, headless=True):
    n_od_ports = len(od_ports)

    # Instantiate options
    opts = Options()
    opts.binary_location = "/usr/bin/google-chrome"
    #opts.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    if headless:
        opts.headless = headless
    opts.add_argument('--remote-debugging-port=9222')
    opts.add_argument('--disable-gpu')
    opts.add_argument("--window-size=2160,2160")

    # Some options to make Chrome (hopefully) more
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Set the location of the webdriver
    os.environ["WDM_PROGRESS_BAR"] = '0'
    chrome_service = Service(ChromeDriverManager().install())

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts, service=chrome_service)

    # Load the HTML page
    driver.get(url)

    # Accept cookies
    driver.implicitly_wait(3)
    try:
        driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
    except:
        print("Cookies already accepted.")

    soups = []
    for n, od in enumerate(od_ports):
        o, d = od
        # Reload page
        driver.get(url)

        # Wait untill page is loaded
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "from")))
        sleep(0.5)

        # TODO: Replace page reload with proper scroll up and clearing the fields:
        # Scroll to top of page
        #ActionChains(driver).send_keys(Keys.PAGE_UP).perform()

        # Clear existing fields - TODO: Does not work yet
        #close_buttons = driver.find_elements(By.CSS_SELECTOR, "span.icon-close")
        #for btn in close_buttons:
        #    ActionChains(driver).send_keys(Keys.ENTER).perform()

        # Fill in and select the origin and destination port
        for label, port in [("from", o), ("to", d)]:
            elem = driver.find_element(By.ID, label)
            sleep(0.1)
            elem.send_keys(port)
            sleep(0.7)  # TODO make this a proper WebDriverWait
            ActionChains(driver).send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()

        # Select direct routing
        if direct:
            driver.find_element(By.ID, "directrouting").click()
        sleep(0.1)

        # Click search button
        driver.find_element(By.CSS_SELECTOR, "button.msc-cta").click()
        sleep(0.1)

        # Check if there are any connections
        no_connections = driver.find_elements(By.XPATH, "//*[contains(text(), 'no results available')]")
        if len(no_connections) >= 1:
            print(f"NO CONNECTIONS available for route {o} to {d}. {n + 1}/{n_od_ports}")
            continue

        # Check if connections are present
        try:
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "msc-search-schedule-result-details__result")))
        except:
            print(f"NO DATA scraped for route {o} to {d}. {n+1}/{n_od_ports}")
            continue

        # Find all buttons to open
        try:
            WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.msc-search-schedule-result-details__more-button")))
        except:
            print(f"NO BUTTONS founds for route {o} to {d}. {n + 1}/{n_od_ports}")
        sleep(0.05)
        buttons = driver.find_elements(By.CSS_SELECTOR, "button.msc-search-schedule-result-details__more-button")

        # Open the buttons that are displayed
        for btn in buttons:
            if btn.is_displayed():
                btn.click()
                sleep(0.05)
        sleep(0.1)

        # Create soup and append to soups list
        soups.append((BeautifulSoup(driver.page_source, features="html.parser"), od))
        print(f"SUCCESSFULLY scraped for route {o} to {d}. {n+1}/{n_od_ports}")

    # Close the browser and return soups list and n_results
    driver.close()
    driver.quit()
    return soups

# Returns connection data for input soups
def get_connection_data(soups):
    # Create empty list for the connection data
    connection_data = []

    # Split each soup in different connections
    for soup, od in soups:
        connections = soup.find_all("div", {"class": "msc-search-schedule-result-details__result"})
        o, d = od

        # For each connection, find data
        for connection in connections:
            transit_time = connection.find("span", {"x-text": "entry.TotalTransitTime"}).text
            co2_footprint = connection.find("span", {"x-text": "entry.CO2FootPrint"}).text

            departure_time = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'EstimatedDepartureTimeFormatted')"})[-1].text
            departure_port = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'DeparturePortName')"})[-1].text
            departure_terminal = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'DepartureEquipmentHandlingFacilityName')"})[-1].text

            service_name = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'MaritimeServiceName')"})[-1].text
            vessel_name = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'Vessel').VesselName"})[-1].text
            "getLegSequenceValue(entry, 'Vessel').VesselName"
            voyage_no = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'DepartureVoyageNo')"})[-1].text

            vessel_build_year = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'Vessel').VesselBuiltYear"})[-1].text
            vessel_flag = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'Vessel').VesselFlag"})[-1].text
            vessel_imo_code =  connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'Vessel').VesselImoCode"})[-1].text

            arrival_port = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'ArrivalPortName')"})[-1].text
            arrival_terminal = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'ArrivalEquipmentHandlingFacilityName')"})[-1].text
            arrival_time = connection.find_all("span", {"x-text": "getLegSequenceValue(entry, 'EstimatedArrivalTimeFormatted')"})[-1].text

            new_connection_data = [o, departure_port, departure_terminal, d, arrival_port, arrival_terminal, departure_time, arrival_time, transit_time, service_name, co2_footprint, vessel_name, voyage_no, vessel_build_year, vessel_flag, vessel_imo_code]
            connection_data.append(new_connection_data)

    return connection_data


# Define dict keys / dataframe columns
columns = ["Origin", "Departure port", "Departure terminal", "Destination", "Arrival port", "Arrival terminal", "Departure time", "Arrival time", "Transit time", "Service name", "CO2 footprint", "Vessel name", "Voyage no.", "Vessel build year", "Vessel flag", "Vessel imo code"]

# Scrape the webpage
soups_ods = get_soups(od_ports, headless=True)

# Get all the connection data, process them and add
connection_data = get_connection_data(soups_ods)

# Create a dataframe from all the route data
connection_df = pd.DataFrame(connection_data, columns=columns)
print(f"Done. DataFrame has {connection_df.index.size} entries")

# Save as Pickle and CSV
connection_df.to_pickle(f"../pickles/msc_daily/connections_{today}.pickle")
connection_df.to_csv(f"../data/msc_daily/connections_{today}.csv")
