import itertools
import pandas as pd
import requests
import pickle

# Define origin and destination countries
origin = ["BR", "CO", "VE", "SR", "CW", "GY", "GF", "UY", "AR", "CL", "PE", "EC", "VN"]
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

url = "https://www.msc.com/api/feature/tools/SearchSailingRoutes"

headers = {
    "authority": "www.msc.com",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "x-requested-with": "XMLHttpRequest"
}

data = []
for n, (o, d) in enumerate(od_ids):
    o_code = port_codes[int(o)]
    d_code = port_codes[int(d)]

    payload = {
        "FromDate": str(today),
        "fromPortId": o,
        "toPortId": d,
        "isDirectRouteOnly": False,
        "language": "en"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # Check if request was succesfull
    rdict = response.json()
    succes = rdict["IsSuccess"]
    if not succes:
        print(f"Warning: No succes on request {n} {o_code, d_code}")
        continue

    # Save data
    new_data = rdict["Data"][0]
    for i in range(len(new_data["Routes"])):
        new_data["Routes"][i]["Origin"] = o_code
        new_data["Routes"][i]["Destination"] = d_code
    data.append(new_data)

    if n % 5:
        print(f"Scraped {n}/{n_combs}")

# Save list with dicts as Pickle
with open(f'../pickles/msc_daily_v2/connections_{today}.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Flatten trip route data
route_data = []
for d in data:
    for route in d["Routes"]:
        route_data.append(route)

# Create dataframe
df = pd.DataFrame(route_data)
print(f"Done. DataFrame has {df.index.size} entries")

# Move the origin and destination columns to the start
cols = df.columns.tolist()
cols = cols[-2:] + cols[:-2]
df = df[cols]

# Save as CSV
df.to_csv(f"../data/msc_daily_v2/connections_{today}.csv")
