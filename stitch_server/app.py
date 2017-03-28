#!flask/bin/python
import threading
from stitch_server import (app, the_master, the_worker)
from request_handler import client_request_handler
from request_handler import worker_request_handler
from request_handler import master_request_handler
from server import (master, worker)

from initdb import init_db

if __name__ == "__main__":
    init_db()

    the_worker = worker.SSWorker("0.0.0.0", 10000, None)

    the_master.start()
    app.run(debug=True);
    the_master.stop()