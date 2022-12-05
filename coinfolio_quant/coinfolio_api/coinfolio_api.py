import os
import requests


coinfolio_base_url = os.environ["COINFOLIO_BASE_URL"]

def get_users():
    result = requests.get(coinfolio_base_url + "/api/clients")
    result_data = result.json()
    users = result_data["users"]
    return users
