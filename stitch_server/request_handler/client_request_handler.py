import sys
sys.path.append("..")

import time
from flask import jsonify
from stitch_server import app, the_master

from models import models

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