from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import itertools
import pandas as pd
from numpy import random
from time import sleep
from datetime import date
import os

# Create list of origin and destination ports
o_ports = ['BRFOR', 'BRSSZ', 'BRPEC', 'BRSSA', 'BRPNG', 'BRRIO', 'BRRIG', 'BRITJ', 'BRNAT', 'COCTG', 'COSMR', 'COTRB', 'SRPBM', 'CWWIL', 'UYMVD', 'ARBUE', 'CLCNL', 'CLSAI', 'CLVAP', 'PEPAI', 'PECLL', 'ECGYE', 'ECPBO', 'ECPSJ', 'VNVUT', 'VNCMT']
d_ports = ['NLRTM', 'BEANR', 'NLVLI', 'BEZEE', 'NLAMS']
# Make list with all combinations
od_ports = list(itertools.product(o_ports, d_ports))

today = date.today()
print(today)

# Define search criteria
limit = 100
sort_on = "transfers"
modalities = "sea"
date = today

# Create list of URLs to scrape
def generate_urls2(od_ports=od_ports):
    return [f"https://www.routescanner.com/voyages?limit={limit}&from={o_port}&fromType=locode&originsNearby=1&to={d_port}&toType=locode&destinationsNearby=1&departure={date}&sort={sort_on}&modalities={modalities}" for o_port, d_port in od_ports]


def get_webpages2(od_ports, headless=False):
    urls = generate_urls2(od_ports)
    u_od_zip = list(zip(urls, od_ports))

    # Instantiate options
    opts = Options()
    opts.binary_location = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    opts.add_argument("window-size=2880,2160")
    if headless:
        opts.headless = True
    # Some options to make Chrome (hopefully) more
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])

    # Set the location of the webdriver
    s = Service(os.getcwd() + "/drivers/chromedriver.exe")

    # Instantiate a webdriver
    driver = webdriver.Chrome(options=opts, service=s)

    def start_browser(url):
        print("(Re)starting browser")
        # Instantiate a webdriver
        driver = webdriver.Chrome(options=opts, service=s)
        # Load the HTML page
        driver.get(url)
        already_got = True
        # Accept cookies
        driver.implicitly_wait(5)
        driver.find_element(By.CLASS_NAME,"acceptButton__P2szu").click()
        return driver

    start_browser(urls[0])

    soups = []
    sleeptime = 20
    driver_age = 0
    for n, (url, od) in enumerate(u_od_zip):
        i = 1
        while True: # Keep trying until successfully scraped
            try:
                # Load the HTML page, if not done earlier by a browser start
                if not already_got:
                    driver.get(url)
                already_got = False

                # Wait until route data is loaded
                elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "voyages__NVlid ")))

                # Parse processed webpage with BeautifulSoup and append to list
                soups.append((BeautifulSoup(driver.page_source), od))

                # Increase the driver age and decrease the sleeptime
                driver_age += 1
                sleeptime = max(10, sleeptime - 3)
                # Print
                print(f"Scraped route {n+1}/{len(u_od_zip)}, took {i} tries (sleeptime {sleeptime})")

                # If the driver is old, refresh it and sleep, otherwise only sleep
                if driver_age >= 4:
                    driver.quit
                    driver_age = 0
                    sleep(random.uniform(sleeptime, sleeptime+2))
                    driver = start_browser()
                else:
                    sleep(random.uniform(sleeptime, sleeptime+2))
            except:
                if i > 6 or sleeptime > 120:
                    print(f"Stopped after {i} sequential failed attempts. {n} routes successfully collected.")
                    return soups
                sleeptime = sleeptime + 10
                print(f"Failed attempt {i} on route {n+1}, trying again (sleeptime {sleeptime})")

                i += 1
                # Restart browser after 2 unsuccessful tries, or if the driver gets old
                if i >= 3 and i % 3 == 0 or driver_age >= 4:
                    driver.quit()
                    sleep(random.uniform(sleeptime, sleeptime+2))
                    start_browser()
                else:
                    sleep(random.uniform(sleeptime, sleeptime+2))
                continue
            #print(f"Done {n}, iteration {i}, sleeping {sleeptime}")
            break

    # Close the browser and return soups list and n_results
    driver.close()
    driver.quit()
    return soups


# Returns route data for list of routes
def get_route_data2(soups):
    # Create empty list for the route data
    route_data = []

    for soup, od in soups:
        # Create a list with all route cards
        routes = soup.find_all("li", class_="voyage voyage__e0GtV")
        o, d = od

        # For each route, find the company, origin, destination, service code, duration and if known frequency
        for route in routes:
            lead = route.find("li", class_="voyageMetaColumn__qkBJv").text

            small = route.find_all("li", class_="voyageMetaColumn__qkBJv voyageMetaColumnSmall__QMXjZ", limit=2)
            transfers, co2 = small[0].text, small[1].text

            time_fields = route.find_all("li", class_="voyageMetaColumn__qkBJv smallerText__ED-90", limit=2)
            dep = [span.text for span in time_fields[0].find_all("span") if span.text != ' - ']
            arr = [span.text for span in time_fields[1].find_all("span") if span.text != ' - ']

            c = route.find_all("span", class_="carrierNames__Dn5bC")
            companies = [n.text for n in c]

            # Split the rout in different legs, and get the ports and companies for each
            legs = route.find_all("ul", class_="leg__9DiZ9")
            ports = []
            for leg in legs:
                # Get the origin, in between, and destination ports for each leg
                o_port = [leg.find("li", class_="origin__Vu5JN").text]
                stop_ports = leg.find_all("span", class_="stopLocode__V9cgh")
                stop_ports = [n.text for n in stop_ports]
                d_port = [leg.find("li", class_="destination__lN9tN").text]
                # Combine all ports in one list, and append that to the ports list
                ports.append(o_port + stop_ports + d_port)

            # Validate number of legs collected:
            if len(ports) != int(transfers)+1:
                print("Warning: Ports data may be incomplete")

            # Add everything to the route_data list
            route_data.append([lead, transfers, o, d, dep, arr, co2, ports, companies])
    return route_data

# Define dict keys / dataframe columns
columns2 = ["Lead time", "Transfers", "Origin", "Destination", "Departure", "Arrival", "kg CO2e/TEU", "Ports", "Carriers"]

# Empty list for data and len
connection_data = []

# Scrape the webpage
soups_ods_2 = get_webpages2(od_ports, headless=True)
# Get all the connection data, process them and add
connection_data = get_route_data2(soups_ods_2)

# Create a dataframe from all the route data
connection_df = pd.DataFrame(connection_data, columns=columns2)
print(f"Done. DataFrame has {connection_df.index.size} entries")

# Save as Pickle and CSV
connection_df.to_pickle(f"pickles/connections_{date}.pickle")
connection_df.to_csv(f"data/connections_{date}.csv")
