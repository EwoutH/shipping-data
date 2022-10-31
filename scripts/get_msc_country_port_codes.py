# A simple script that retrieves and saves the list of country and port codes from MSC

import requests
import pickle

url = "https://www.msc.com/api/feature/tools/GetAllAvailableCountriesAndPorts"

headers = {
    "authority": "www.msc.com",
    "accept": "application/json, text/plain, */*",
    "x-requested-with": "XMLHttpRequest"
}

response = requests.request("GET", url, headers=headers)

data = response.json()

with open('../pickles/msc_country_port_codes.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
