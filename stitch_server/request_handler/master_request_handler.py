import sys
sys.path.append("..")

import time
from flask import jsonify
from stitch_server import app, the_master
from models import models

@app.route("/master/register", methods=["GET"])
def master_handle_register():
    worker = models.StitchWorker()
    worker.id = time.time()
    worker.ip = "10.10.10.187" # 
    worker.port = 9999
    worker.alive = False; # True
    worker.state = models.STITCHWORKER_STATE_IDLE
    the_master.register_worker(worker)

    return jsonify({"master":"/worker/register"})

@app.route("/master/unregister", methods=["GET"])
def master_handle_unregister():
    worker_id = ""
    the_master.unregister_worker(worker_id)

    return jsonify({"master":"/worker/register"})

@app.route("/master/set_task_result", methods=["POST"])
def master_set_task_result():
    return jsonify({"master":"set_task_result"})

@app.route("/master/heartbeat", methods=["POST"])
def master_handle_heartbeat():
    return jsonify({"master":"/heartbeat"})