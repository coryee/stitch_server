import __init__
import time
import pprint
import json
from flask import (jsonify, request)
from stitch_server import (app, the_master)

from models import models
from utils import httputil
from request_util import validate_json
import errors

@app.route("/master/get_job", methods=["POST"])
@validate_json
def master_get_job():
    payload = request.get_data()
    r = json.loads(payload)
    job_id = r.get("job_id", "xxxx")
    job = the_master.get_job(job_id)
    response = jsonify({"master":"get_job"})

    return response


@app.route("/master/get_jobs", methods=["POST"])
@validate_json
def master_get_jobs():
    print "get_jobs"
    return jsonify({"master":"get_jobs"})


@app.route("/master/add_job", methods=["POST"])
@validate_json
def master_add_job():
    data = request.get_data()
    payload = json.loads(data)
    # search db to find out the corresponding offline.map
    job_dict = payload.get("job", {})
    job_id = None
    print "filename = %s" % job_dict.get("src_filename", "")
    job_id = the_master.add_job(job_dict)
    
    if job_id:
        response = httputil.http_creat_reponse(errors.SS_EC_OK, {"job_id":job_id})
    else:
        response = httputil.http_creat_reponse(errors.SS_EC_INVALID_REQUEST)

    return response
