import sys
sys.path.append("..")

import time
from flask import (jsonify, request)
from stitch_server import app, the_master
from request_util import validate_json
from models import models
import errors

@app.route("/master/register", methods=["POST"])
@validate_json
def master_handle_register():
    err_code = errors.SS_EC_FAILURE
    data = request.get_data()
    payload = json.loads(data)

    worker = models.StitchWorker()
    worker.ip = str(payload.get("ip", ""))
    worker.port = int(payload.get("port", 0))
    worker.state = int(payload.get("port", 0))
    if the_master.register_worker(worker):
        err_code = errors.SS_EC_OK

    return httputil.http_creat_reponse(err_code)


@app.route("/master/unregister", methods=["POST"])
@validate_json
def master_handle_unregister():
    err_code = errors.SS_EC_FAILURE
    data = request.get_data()
    payload = json.loads(data)
    worker_id = str(payload.get("worker_id", ""))

    if the_master.unregister_worker(worker_id):
        err_code = errors.SS_EC_OK
    return httputil.http_creat_reponse(err_code)


@app.route("/master/set_task_result", methods=["POST"])
@validate_json
def master_set_task_result():
    err_code = errors.SS_EC_FAILURE
    data = request.get_data()
    payload = json.loads(data)
    task_id = str(payload.get("task_id", ""))
    task_state = int(payload.get("task_state", -1))
    task_result = int(payload.get("task_result", 99999))
    if task_state == -1 or task_result == 99999:
        err_code = errors.SS_EC_INVALID_REQUEST
    else:
        if the_master.set_task_state(task_id, task_state, task_result):
            err_code = errors.SS_EC_INVALID_OK

    return httputil.http_creat_reponse(err_code)


@app.route("/master/heartbeat", methods=["POST"])
@validate_json
def master_handle_heartbeat():
    err_code = errors.SS_EC_FAILURE
    data = request.get_data()
    payload = json.loads(data)
    worker_id = str(payload.get("worker_id", ""))
    worker_state = int(payload.get("worker_state", 0))

    if the_master.worker_heartbeat(worker_id, worker_state):
        err_code = err_code = errors.SS_EC_OK
    return httputil.http_creat_reponse(err_code)