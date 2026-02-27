# %%
import requests


# SETUP
BASE_URL = "http://127.0.0.1:8000"

def check_services():
    return requests.get(f"{BASE_URL}/services").json()
# %%
check_services()
# %%
