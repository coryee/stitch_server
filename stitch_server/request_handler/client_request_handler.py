import __init__
import time
from pprint import pprint
import json
from flask import (jsonify, request)
from stitch_server import (app, the_master)

from models import models
from utils import httputil
import request_util
from request_util import validate_json
from models.sqlutil import job_db_operator
import errors

@app.route("/master/get_job", methods=["POST"])
@validate_json
def master_get_job():
    data = request.get_data()
    payload = json.loads(data)
    err_code = errors.SS_EC_FAILURE
    job_id = str(payload.get("job_id", ""))
    result = {}
    try:
        job = job_db_operator.query_by_id(job_id)
        if job:
            result = request_util.job_to_dict(job)
        else:
            result["job"] = {}
        err_code = errors.SS_EC_OK
    except Exception as e:
        print e.message
    
    return httputil.http_creat_reponse(err_code, result)


@app.route("/master/get_job_state", methods=["POST"])
@validate_json
def master_get_job_state():
    data = request.get_data()
    payload = json.loads(data)
    job_id = str(payload.get("job_id", ""))

    err_code = errors.SS_EC_OK
    response = {}
    result, state = the_master.get_job_state(job_id)
    if result is None or state is None:
        err_code = errors.SS_EC_INVALID_VALUE
    else:
        response["state"] = state 
        response["result"] = result
    
    return httputil.http_creat_reponse(err_code, response)



@app.route("/master/get_jobs", methods=["POST"])
@validate_json
def master_get_jobs():
    jobs_dict = {}
    try:
        jobs = job_db_operator.query("create_time", 0, 1)
        jobs_dict = request_util.jobs_to_dict(jobs)
        err_code = errors.SS_EC_OK
    except Exception as e:
        print e.message
        err_code = errors.SS_EC_FAILURE
    
    pprint(jobs_dict)
    return httputil.http_creat_reponse(err_code, jobs_dict)


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


@app.route("/master/remove_job", methods=["POST"])
@validate_json
def master_remove_job():
    data = request.get_data()
    payload = json.loads(data)
    job_id = str(payload.get("job_id", ""))

    err_code = errors.SS_EC_OK
    result = the_master.remove_job(job_id)
    if request is False:
        err_code = errors.SS_EC_FAILURE
    
    return httputil.http_creat_reponse(err_code)
