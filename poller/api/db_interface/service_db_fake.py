import json

from poller.config import JSON_SERVICES


def get_services():
    with open(JSON_SERVICES, 'r') as json_in:
        return json.load(json_in)