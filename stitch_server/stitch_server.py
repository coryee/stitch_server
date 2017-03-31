from flask import Flask, jsonify
from server import (master, worker)

app = Flask(__name__)
the_master = master.SSMaster()
the_worker = worker.SSWorker()

@app.route("/", methods=["GET"])
def get_index():
    return jsonify({"task":"hello world"})
