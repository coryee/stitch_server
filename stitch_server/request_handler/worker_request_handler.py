import sys
sys.path.append("..")
from flask import (jsonify, request)
from stitch_server import (app, the_worker)
from models import models
from server import ssutils
from request_util import validate_json
import errors

@app.route("/worker/add_task", methods=["POST"])
@validate_json
def worker_add_task():
    err_code = errors.SS_EC_FAILURE
    data = request.get_data()
    payload = json.loads(data)
    if the_worker.add_task(payload):
        err_code = errors.SS_EC_OK
    
    return httputil.http_creat_reponse(err_code)


@app.route("/worker/get_task_info", methods=["POST"])
@validate_json
def worker_get_task_info():
    err_code = errors.SS_EC_OK
    data = request.get_data()
    payload = json.loads(str(data))
    task_id = payload.get("id", "")
    data = self.get_task_info(task.id)
    response["task"] = data
    return httputil.http_creat_reponse(err_code, response)


@app.route("/worker/cancel_task", methods=["POST"])
@validate_json
def worker_cancel_task():
    err_code = errors.SS_EC_FAILURE
    data = request.get_data()
    payload = json.loads(str(data))
    task_id = payload.get("id", "")
    if the_worker.cancel_task(task_id):
        err_code = errors.SS_EC_OK
    return jsonify({"work":"cancel_task"})