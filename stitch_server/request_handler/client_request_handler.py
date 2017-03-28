import __init__
import time
import json
from flask import (jsonify, request)
from stitch_server import (app, the_master)

from models import models
from utils import httputil
import errors


@app.route("/master/get_job", methods=["POST"])
def master_get_job():
    try:
        payload = request.get_data()
        r = json.loads(payload)
        job_id = r.get("job_id", "xxxx")
        job = the_master.get_job(job_id)
        response = jsonify({"master":"get_job"})
    except Exception as e:
        print e.message
        response = httputil.http_creat_reponse(errors.SS_EC_INVALID_JSON_FORMAT)

    return response


@app.route("/master/get_jobs", methods=["POST"])
def master_get_job_list():
    return jsonify({"master":"get_jobs"})

@app.route("/master/add_job", methods=["POST"])
def master_add_job():
    job = models.StitchJob()
    job.id = time.time()
    job.src_filename = job.id
    job.src_file_id = "" 
    job.dst_dir = ""
    job.dst_format = "flv"
    job.map_filename = "" # map.offline.4k.map
    job.map_file_id = "" # md5 genearted by md5sum cmd
    job.state = models.STITCHJOB_STATE_READY
    the_master.add_job(job)

    return jsonify({"master":"add_job"})
