import __init__
from functools import wraps
import json
from flask import (jsonify, request)
from stitch_server import (app, the_master)
from utils import httputil
import errors


def invalid_json():
    response = httputil.http_creat_reponse(errors.SS_EC_INVALID_JSON_FORMAT)
    return response

def validate_json(func):
    @wraps(func)
    def decorator():
        try:
            payload = request.get_data()
            r = json.loads(payload)
            return func()
        except Exception as e:
            print e.message
            return invalid_json()
    return decorator