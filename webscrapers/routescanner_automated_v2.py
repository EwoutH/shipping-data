import itertools
import pandas as pd
import requests
import pickle
from time import sleep
import random
from fake_useragent import UserAgent

# Define origin and destination countries
origin = ["BR", "CO", "VE", "SR", "CW", "GY", "GF", "UY", "AR", "CL", "PE", "EC", "VN", "PY", "GY", "KH"]
destination = ["NL", "BE"]

# Create DataFrames from UN-LOCODE CSVs
country_df = pd.read_csv("../utils/country-codes.csv")
country_df.set_index("CountryCode", inplace=True)
country_dict = country_df.to_dict()["CountryName"]

# Create dictionary with country codes and names
o_dict = {code: name for code, name in country_dict.items() if code in origin}
d_dict = {code: name for code, name in country_dict.items() if code in destination}

# Load MSC port codes
with open('../pickles/msc_country_port_codes.pickle', 'rb') as handle:
    country_port_codes = pickle.load(handle)

# Get all ports in origin and destination countries
o_ports = [port for port in country_port_codes["Ports"] if port["CountryIsoCode"] in origin]
d_ports = [port for port in country_port_codes["Ports"] if port["CountryIsoCode"] in destination]

# Create list of port IDs to scrape
o_ids = [port['PortId'] for port in o_ports]
d_ids = [port['PortId'] for port in d_ports]

# Create dictionary of port IDs and codes:
port_codes = {port['PortId']: port['LocationCode'] for port in o_ports + d_ports}

# Make list with all combinations
od_ids = list(itertools.product(o_ids, d_ids))
print(f"{(n_combs := len(od_ids))} combinations of ports ({len(o_ids)} origins * {len(d_ids)} destinations)")

# Use today's date, by default
from datetime import date
today = date.today()
print(today)

# Get random user agent
user_agent = UserAgent().random

# Get machine_token for device
def request_machine_token():
    token_url = "https://www.routescanner.com/home-vars"

    token_headers = {
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }
    response = requests.get(token_url, headers=token_headers)

    r = response.json()
    machine_token = r['machineToken']
    return machine_token

machine_token = request_machine_token()
print(f"Machine token: {machine_token}")


# Scrape RouteScanner
url = "https://api.routescanner.com/voyages/v1"

headers = {
    "User-Agent": user_agent,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,nl-NL;q=0.8,nl;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://www.routescanner.com",
    "machine_token": machine_token,
}

sort_by = "transfers"  # transfers, emission_co2, arrival or duration
modalities = "sea"     # rail, barge, and truck can be added

data = []
sleeptime = 3
for n, (o, d) in enumerate(od_ids):
    i = 1

    o_code = port_codes[int(o)]
    d_code = port_codes[int(d)]

    querystring = {"offset":"0","limit":"100","origin":o_code,"originType":"locode","destination":d_code,
                   "destinationType":"locode","destinationsNearby":"true","originsNearby":"true",
                   "minDeparture":today,"sort":sort_by,"modalities":modalities}

    while True:  # Keep trying until successfully scraped
        response = requests.get(url, headers=headers, params=querystring)

        # Check if request was successful
        if response.status_code != 200:
            print(f"Warning: Status code != 200 (on attempt {i} for {o_code} to {d_code}, #{n}). Sleeping {sleeptime+10} s.")
            i += 1
            sleeptime += 10
            sleep(random.uniform(sleeptime, sleeptime + 2))
            continue

        # If successful, save data
        rdict = response.json()
        new_data = rdict
        data.append(new_data)

        # Reduce sleeptime and sleep
        sleeptime = max(3, sleeptime - 3)
        sleep(random.uniform(sleeptime, sleeptime + 2))
        break  # break from the while True loop, and thus continue with the main for loop

    if n % 5 == 0:
        print(f"Scraped {n}/{n_combs}. Sleeptime {sleeptime} s.")

# Save list with dicts as Pickle
with open(f'../pickles/routescanner_daily_v2/connections_{today}.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Flatten route data
route_data = []
for d in data:
    od = {"Origin": d["origin"]["locode"],
          "Destination": d["destination"]["locode"]}
    for route in d["voyages"]:
        route_data.append(od | route)

# Save DataFrame
df = pd.DataFrame(route_data)
print(f"Done. DataFrame has {df.index.size} entries")
df.to_csv(f"../data/routescanner_daily_v2/connections_{today}.csv")
