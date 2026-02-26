import json

from poller.config import JSON_SERVICES


def get_services():
    return json.load(JSON_SERVICES)