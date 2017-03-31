#!/usr/bin/python
import threading
import argparse
import json
from stitch_server import (app, the_master, the_worker)
from request_handler import client_request_handler
from request_handler import worker_request_handler
from request_handler import master_request_handler
from server import (master, worker)
import constants

from initdb import init_db

if __name__ == "__main__":
    print "start main"
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", 
                        type = str,
                        help = "specify the config file")
    args = parser.parse_args()

    config = {}
    with open(args.config_file, 'r') as f:
        read_data = f.read()
        config = json.loads(read_data)

    is_master = True
    if config["stitch_server_type"] == constants.STITCH_SERVER_TYPE_MASTER:
        print "master running..."
        init_db()
        the_master.start()
    else:
        print "worker running..."
        is_master = False
        master = worker.StitchMaster()
        master.ip = config["stitch_server_master_ip"]
        master.port = config["stitch_server_master_port"]
        the_worker.set_url(config["stitch_server_ip"], config["stitch_server_port"])
        the_worker.set_master(master)
        the_worker.start()

    app.run(debug=True, host=config["stitch_server_ip"], port=config["stitch_server_port"])
    if is_master:
        the_master.stop()
    else:
        the_worker.stop()