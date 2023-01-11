from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
import itertools
from datetime import date

# Some definitions in explanation of the code:
# Connection: ALl possibilities from the origin port to the destination port
# Route: A specific possibility from origin to destination on a specific departure date
# Transfer: Within a route, the container can switch from one vessel to the other and continue journey

#sets up the options of the chromedriver
opts = Options()
opts.add_argument("window-size=1280,720") #locks the window size
opts.add_argument("user-agent=Chrome/106.0.5249.119") #Prevents sites from blocking traffic
headless = True

if headless: #if True, open chrome on the background without window
    opts.headless = True

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

#!!! Instructions on port selection start
# The same ports and methods as for scraping_routscanner_v2 were used.
#           origin = ["BR", "CO", "VE", "SR", "CW", "GY", "GF", "UY", "AR", "CL", "PE", "EC", "VN", "PY", "GY", "KH"]
#           destination = ["NL", "BE"]
# The UN-LOCODES were picked from the following CSV: (contains country codes
#           country_df = pd.read_csv("../utils/country-codes.csv")
# Furthermore the ports in South-America, Vietnam and Benelux were selected
#        with open('../pickles/msc_country_port_codes.pickle', 'rb') as handle:
#                country_port_codes = pickle.load(handle)

# However unlike scraping_routescanner_v2, the site of Maersk doesn't accept port-codes such as NLRTM
# Therefore, the correct port names that work in the site of Maersk were selected by hand
# Using both the port name according to the list above and the latitude and longitude
#!!! Instructions on port selection end

o_names = ["Arica, Chile","Belem (Para), Brazil","Buenaventura (Valle Del Cauca), Colombia","Buenos Aires (Buenos Aires), Argentina","Asuncion, Paraguay","Pilar, Paraguay","Callao, Peru","Campana (Buenos Aires), Argentina","Cartagena (Bolivar), Colombia","Coronel, Chile","Da Nang (Da Nang), Vietnam","Encarnacion, Paraguay","Georgetown, Guyana","Guayaquil, Ecuador","Haiphong (Hai Phong), Vietnam","Ho Chi Minh city - ICD Phuoc Long (Ho Chi Minh), Vietnam","Iquique, Chile","Itajai (Santa Catarina), Brazil","Itapoa (Santa Catarina), Brazil","Sihanoukville, Cambodia","La Guaira, Venezuela","Lirquen, Chile","Manaus (Amazonas), Brazil","Montevideo, Uruguay","Navegantes (Santa Catarina), Brazil","Nueva Palmira, Uruguay","Paita, Peru","Paramaribo, Suriname","Paranagua (Parana), Brazil","Pecem (Ceara), Brazil","Phnom Penh, Cambodia","Porto Velho (Rondonia), Brazil","Posorja - Guayas, Ecuador","Puerto Angamos, Chile","Puerto Bolivar - El Oro, Ecuador","Puerto Cabello, Venezuela","Villeta, Paraguay","Qui Nhon (Binh Dinh), Vietnam","Rio de Janeiro (Rio de Janeiro), Brazil","Rio Grande (Rio Grande do Sul), Brazil","Rosario (Santa Fe), Argentina","Salvador (Bahia), Brazil","San Antonio, Chile","San Vicente, Chile","Santarem (Para), Brazil","Santos (Sao Paulo), Brazil","Suape (Pernambuco), Brazil","Terport, Paraguay","Turbo (Antioquia), Colombia","Ushuaia (Tierra del Fuego), Argentina","Valparaiso, Chile","Vila do Conde (Para), Brazil","Vitoria (Espirito Santo), Brazil","Vung Tau (Ba Ria - Vung Tau), Vietnam","ZARATE (Buenos Aires), Argentina"]
# Puerto seguro flavial has been moved to villeta. This place seemed more logical according to lat and long
# Terport villeta paraguay had no latitude or longitude to check,
# But luckily there was only one port called Terport in Maersk

d_names = ["Amsterdam (Noord-Holland), Netherlands","Antwerp (Antwerp), Belgium","Moerdijk (Noord-Brabant), Netherlands","Rotterdam (Zuid-Holland), Netherlands","Vlissingen (Zeeland), Netherlands","Zeebrugge (West Flanders), Belgium"]

od_names = list(itertools.product(o_names, d_names))

def open_routes():
    # All if statements check if a route has been found
    # First button can already be clicked because that was already checked before opening this process
    driver.find_element(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[3]/div/div[4]/button/span").click()
    if len(driver.find_elements(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[4]/div/div[4]/button/span")) > 0:
        driver.find_element(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[4]/div/div[4]/button/span").click()
        if len(driver.find_elements(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[5]/div/div[4]/button/span")) > 0:
            driver.find_element(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[5]/div/div[4]/button/span").click()

            if len(driver.find_elements(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[6]/div/div[4]/button/span")) > 0:
                driver.find_element(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[6]/div/div[4]/button/span").click()

                if len(driver.find_elements(By.XPATH,"//*[@id='app']/div[2]/div[1]/div[7]/div/div[4]/button/span")) > 0:
                    driver.find_element(By.XPATH, "//*[@id='app']/div[2]/div[1]/div[7]/div/div[4]/button/span").click()
    soup_page() # Soup the page

def soup_page():
    #Soup the page
    page_source = driver.page_source
    soup = BeautifulSoup(page_source)
    soups.append(soup)

### This part fills in all the origin destination locations and saves the soup which will be processed later on
soups = []

def open_webpages(od_names):
    print(f"Starting to scrape {len(od_names)} harbor combinations.")
    #Open Maersk point to point site
    driver.get("https://www.maersk.com/schedules/pointToPoint")
    time.sleep(3)
    #Click to allow cookies
    driver.find_element(By.XPATH,"//*[@id='coiPage-1']/div[2]/button[3]").click()

    for i in od_names:
        #Open the site again
        driver.get("https://www.maersk.com/schedules/pointToPoint")
        time.sleep(3)

        #fill in the origin location
        originloc = driver.find_element(By.ID,'originLocation')
        originloc.send_keys(i[0])

        #a dropdown menu has to be clicked in order to confirm the origin location. This clicks the correct port
        time.sleep(4) #Makes sure that the element is actually clickable
        action = ActionChains(driver)
        action.move_to_element_with_offset(originloc, 0, 50)
        action.click()
        action.perform()

        #Fills in the destination location automatically.
        destinationloc = driver.find_element(By.ID,'destinationLocation')
        destinationloc.send_keys(i[1])

        #a dropdown menu has to be clicked in order to confirm the origin location. This clicks the correct port
        time.sleep(3)
        action = ActionChains(driver)
        action.move_to_element_with_offset(destinationloc, 0, 50)
        action.click()
        action.perform()

        #Click the search button
        search_button = driver.find_element(By.XPATH,'//*[@id="app"]/div[2]/span/form/div[6]/button')
        search_button.click()

        # There are 2 known possibilities that result in not finding routes:
        # 1: There is no route
        # 2: Sometimes Maersk site gives an error for either origin or destination
        #    even when the names are correctly filled in. Error seems to appear randomly
        # Try makes sure the code doesn't fail even if a route is not found
        # It works by checking if the first button for 'show route details' can be clicked. If not, no route has been found
        time.sleep(5)
        if len(driver.find_elements(By.XPATH,"//*[@id='app']/div[2]/div[1]/div[3]/div/div[4]/button/span")) > 0:
            open_routes() #Expand all the show route details buttons
            time.sleep(5)
            if len(driver.find_elements(By.CLASS_NAME,"load-more__text")) > 0: #Check if even more routes have been found than just appearing on the first page
                driver.find_elements(By.CLASS_NAME,"load-more__text")[1].click() #Click to open second page with routes
                                                                                 # 'Earlier sailings' and 'Later sailings' have same class. We want to click 'Later sailings'
                time.sleep(5) #Make sure that all buttons can open
                if len(driver.find_elements(By.XPATH,"//*[@id='app']/div[2]/div[1]/div[3]/div/div[4]/button/span")) > 0:
                    open_routes() #if statement above is not necessarily needed. It checks again if at least 1 route can be found.
                                  # That should be the case because we are on the second page of routes. More of a failsafe.
        #In the notebook something will be printed here in an else:

    #Closes the webdriver after a few seconds
    driver.stop_client()
    driver.quit()

open_webpages(od_names)

def process_data_route(route,list_ports,route_data):
    #The origin port is the first port in the list, destination the last
    origin = list_ports[0]
    destination = list_ports[-1]

    # The information about the destination and therefore arrival date can be found in the last box
    info_destination = route.find(class_="ptp-results__transport-plan--item-final")
    arrival_date = info_destination.find(class_="transport-label font--small")
    arrival_date = arrival_date.find_all(class_="font--small")
    arrival_date = arrival_date[1].text

    info_departure = route.find(class_="transport-label font--small")

    departure_date = info_departure.find(class_="font--small").text

    # Make an empty list for all used vessels. If only 1 vessel is used only 1 item will be in this list
    vessels = []

    # The following code only works for the first vessel that is being stored
    # Either 2 things can occur: ' Departing on [shipname]' or ' Transport via barge '
    # If a ship is used, the shipname will be stored
    # If barge is used, 'barge' will be stored (literally)
    vessel_name = info_departure.find(class_="rich-text").text
    if vessel_name[:13] != ' Departing on': #If false: ' Transport via barge'
        vessel_name = vessel_name.removeprefix(' Transport via ')
        vessel_name = vessel_name.removesuffix(' ')
    else: # If a ship is used
        # The vessel name is intially given as ie. "Departing on CAP SAN LORENZO / 249S"
        # This makes sure that only the Cap San Lorenzo part is stored
        vessel_name = vessel_name.removeprefix(' Departing on ')
        vessel_name = vessel_name.split()
        if len(vessel_name) >= 2 and "/" in vessel_name:
            vessel_name.remove("/")
            vessel_name.pop(-1)
            vessel_name = ' '.join(vessel_name)

    vessel_info = route.find(class_="vessel")
    if vessel_info is not None:
        imo = vessel_info.find(class_="imo").text
        imo = imo.removeprefix('IMO Number')

        service = vessel_info.find(class_="service").text
        service = service.removeprefix('Service')

        flag = vessel_info.find(class_="flag").text
        flag = flag.removeprefix('Flag')

        callsign = vessel_info.find(class_="callsign").text
        callsign = callsign.removeprefix('Call Sign')

        built_year_ship = vessel_info.find(class_="built").text
        built_year_ship = built_year_ship.removeprefix('Built')

        # Store the information about the first used vessel as a list
        # If other vessels are also used, these will be also be stored as a list
        vessels.append([vessel_name,imo,service,flag,callsign,built_year_ship])
    # In the notebook something will be printed here in an else:

    if len(list_ports)>2: # If there is a transfer, store data and also run process_data_transfer
        route_data.append([origin,destination,departure_date,arrival_date])
        process_data_transfer(route,list_ports,route_data,vessels)
    # In the notebook something will be printed here in an else:
        # Just store the route_data
        route_data.append([origin,destination,departure_date,arrival_date,[origin,destination],vessels,[departure_date,arrival_date,]])
        return route_data

def process_data_transfer(route,list_ports,route_data,vessels):
    transfer_arrival_departure =[]

    for i in range(1,len(list_ports)-1):
        #item 1 is a port, 2 a ship, 3 a port and so on
        #The following if statement makes sure that data of a port
        #is actually read as a port
        if (i % 2) == 1:
            transfer_port = route.find_all(class_="ptp-results__transport-plan--item")[i]

            info_arrival = transfer_port.find(class_="transport-label font--small")

            arrival_date = info_arrival.find_all(class_="font--small")[1].text

            transfer_arrival_departure.append(arrival_date)

            transfer_ship = route.find_all(class_="ptp-results__transport-plan--item")[i+1]

            info_departure = transfer_ship.find(class_="transport-label font--small")
            departure_date = info_departure.find(class_="font--small").text

            transfer_arrival_departure.append(departure_date)

            # Similar as for 1 ship, read description in process_data_route if unclear  
            vessel_name = info_departure.find(class_="rich-text").text
            if vessel_name[:13] != ' Departing on':
                vessel_name = vessel_name.removeprefix(' Transport via ')
                vessel_name = vessel_name.removesuffix(' ')
            else:
                vessel_name = vessel_name.removeprefix(' Departing on ')
                vessel_name = vessel_name.split()
                if len(vessel_name) >= 2 and "/" in vessel_name:
                    vessel_name.remove("/")
                    vessel_name.pop(-1)
                    vessel_name = ' '.join(vessel_name)

            vessel_info = transfer_ship.find(class_="vessel")

            if vessel_info is not None:
                imo = vessel_info.find(class_="imo").text
                imo = imo.removeprefix('IMO Number')

                service = vessel_info.find(class_="service").text
                service = service.removeprefix('Service')

                flag = vessel_info.find(class_="flag").text
                flag = flag.removeprefix('Flag')

                callsign = vessel_info.find(class_="callsign").text
                callsign = callsign.removeprefix('Call Sign')

                built_year_ship = vessel_info.find(class_="built").text
                built_year_ship = built_year_ship.removeprefix('Built')

                vessels.append([vessel_name,imo,service,flag,callsign,built_year_ship])
            # In the notebook something will be printed here in an else:

    # This part is quite complicated
    # The data on the origin, destination and first vessel were already stored in route_data in process_data_route
    # We will alter this data by adding the information about the transfer ports and vessels

    # We first store the data on departure date that was already stored in process_data_route somewhere else
    arrival_departure = []
    arrival_departure.append(route_data[-1][2])

    # Then store all the transfer arrival and departure date
    for i in transfer_arrival_departure:
        arrival_departure.append(i)

    # Last store the arrival date for the whole route
    arrival_departure.append(route_data[-1][3])

    # Store the other transfer data in route_data
    route_data[-1].append(list_ports)
    route_data[-1].append(vessels)
    # Store the data on all departure and arrival dates (including transfer) in the route_data
    route_data[-1].append(arrival_departure)
    return route_data

### Process_data_route, process_data_transfer and initialize_processing
### all process the soups into usable data
### First initialize_processing selects a soup and prepares it for processing
### Then process_data_route will process the information about the origin, destination, arrival data en departure date and the first vessel
### Last process_data_transfer will be used if a transfer takes place.
### A transfer means that the container is moved from one vessel to the another and continues the journey

# Make a list in which all the data of all routes can be stored
route_data = []

def initialize_processing(soups):
    for i in range(len(soups)):
        #Lists all the data on routes. The data on routes is already grouped.
        routes = soups[i].find_all("div", class_="ptp-results__transport-plan")

        #The Maersk site does not show all ports that are on the route
        #It only provides information on ports which are either origin, destination or transfer ports
        #Transfer in this context means a port where the container is moved to a different ship.
        #The following few lines detects all ports in a route

        for route in routes:
            ports = route.find_all("div", class_="location")
            list_ports =[]
            for p in ports:
                city = p.find("div", class_="font--default--bold").text
                terminal = p.find("div", class_="font--small").text
                port = city + ' ' + terminal
                list_ports.append(port)

            process_data_route(route,list_ports,route_data)

initialize_processing(soups)

# This turns the processed data into a Pandas dataframe
columns = ["Origin","Destination","Departure time", "Arrival time","Ports","Vessels","Dates"]

connection_df = pd.DataFrame(route_data, columns=columns)

# Store as both pickle and CSV
today = date.today()
connection_df.to_pickle(f"../pickles/maersk_daily/connections_{today}.pickle")
connection_df.to_csv(f"../data/maersk_daily/connections_{today}.csv")
