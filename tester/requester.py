# %%
import requests


# SETUP
BASE_URL = "http://127.0.0.1:8000"

def check_status():
    resp = requests.post(f"{BASE_URL}/jobs", json={'job_id': '100', 'service': 'mock'})
# %%
check_status()
# %%
