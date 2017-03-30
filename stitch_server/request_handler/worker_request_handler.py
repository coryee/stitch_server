import sys
sys.path.append("..")
from flask import jsonify
from stitch_server import (app, the_worker)
from models import models
from server import ssutils
from request_util import validate_json
import errors

@app.route("/worker/add_task", methods=["POST"])
def worker_add_task():
    task = models.StitchTask()
    the_worker.add_task(task)
    return jsonify({"work":"add_task"})

@app.route("/worker/get_task_info", methods=["POST"])
def worker_get_task_info():
    task_id = "1111"
    data = self.get_task_info(task.id)
    return ss_create_response(data)

@app.route("/worker/cancel_task", methods=["POST"])
def worker_cancel_task():
    task_id = "11111"
    the_worker.cancel_task(task_id)
    return jsonify({"work":"cancel_task"})