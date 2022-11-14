import requests
import pickle
import os
from fake_useragent import UserAgent

env_file = os.getenv('GITHUB_ENV')
print(f"Env_file: {env_file}")

# Get machine_token for device
def request_machine_token():
    token_url = "https://www.routescanner.com/home-vars"

    user_agent = UserAgent().random
    print(user_agent)

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
print(machine_token)

#with open('machine_token.pickle', 'wb') as handle:
#    pickle.dump(machine_token, handle, protocol=pickle.HIGHEST_PROTOCOL)
