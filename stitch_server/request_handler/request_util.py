import __init__
from functools import wraps
import json
from flask import (jsonify, request)
from stitch_server import (app, the_master)
from utils import httputil
from models import models
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



def jobs_to_dict(jobs):
    result = {}
    dict_list = []

    for job in jobs:
        dict_list.append(job.to_dict())

    result["jobs"] = dict_list
    return result

def job_to_dict(job):
    result = {}
    result["job"] = job.to_dict()
    return result

