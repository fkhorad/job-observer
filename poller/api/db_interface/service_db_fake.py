import json

from poller.config import JSON_SERVICES

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


def get_services_filtered():
    with open(JSON_SERVICES, 'r') as json_in:
        service_json = json.load(json_in, object_hook=branch_aware_filter)
    #
    return service_json

def get_services():
    with open(JSON_SERVICES, 'r') as json_in:
        service_json = json.load(json_in)
    #
    return service_json