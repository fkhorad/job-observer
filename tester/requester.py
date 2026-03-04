# %%
import requests


# SETUP
SCHEDULER_LOCAL_URL = "http://127.0.0.1:8000"

def check_services(*, instance_type='local'):
    if instance_type=='local':
        return requests.get(f"{SCHEDULER_LOCAL_URL}/services").json()
    else:
        raise Exception('Not implemented yet!')
# %%
check_services()
# %%
requests.post('http://localhost:8000/add_job',
                headers = {
                "Content-Type": "application/json"
                },
                json = {
                    'job_id': '019cb9bc-9172-71d3-92f2-794cc0738634',
                    'service': 'eScriptorium',
                    'callback_url': 'http://localhost:3001/callback' # optional
                }
            )
# %%
