import json
from fastapi import HTTPException

from observer.config import JSON_SERVICES_FOLDER, JSON_SERVICES_FILE


WHITELIST = {'name', 'method', 'url', 'query_params', 'body', 'static_headers', 'timeout', 'status_field', 'terminal_states', 'max_concurrency', 'auth_type'}
BLACKLIST = {'auth_config'}

def branch_aware_filter(obj):
    new_dict = {}
    for k, v in obj.items():
        # 0. If blacklisted, skip immediately
        if k in BLACKLIST:
            continue
        # 1. Is it a whitelisted keyword?
        # 2. Is it a dictionary? (Keep the branch so we can see what's inside)
        # 3. Is it a list? (Usually we want to keep lists to check objects inside them)
        if k in WHITELIST or isinstance(v, (dict, list)):
            new_dict[k] = v
    #
    return new_dict


def init_db():

    JSON_SERVICES_FOLDER.mkdir(parents=True, exist_ok=True)

    # Checks if services file exists and is readable; else inits empty file
    try:
        with open(JSON_SERVICES_FILE, 'r') as json_in:
            json.load(json_in)
    except (FileNotFoundError, json.JSONDecodeError):
        default_data = {}
        with open(JSON_SERVICES_FILE, 'w') as f:
            json.dump(default_data, f)


def get_services_filtered():
    with open(JSON_SERVICES_FILE, 'r') as json_in:
        service_json = json.load(json_in, object_hook=branch_aware_filter)
    #
    return service_json


def get_services():
    with open(JSON_SERVICES_FILE, 'r') as json_in:
        service_json = json.load(json_in)
    #
    return service_json


def add_services(body: dict, overwrite: bool):

    # Get service definitions
    with open(JSON_SERVICES_FILE, 'r') as json_db:
        service_json = json.load(json_db)

    # Add or replace individual services
    for k, v in body.items():
        if service_json.get(k) is None or overwrite:
            service_json[k] = v
        else:
            raise HTTPException(
                status_code=409,
                detail=f"Service '{k}' already exists. Set 'overwrite=true' in request body to replace it."
            )

    # Overwrite service definitions with new object
    with open(JSON_SERVICES_FILE, 'w') as json_db:   
        json.dump(service_json, json_db)
        return service_json

