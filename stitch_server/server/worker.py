import sys
sys.path.append("..")
from collections import defaultdict
import time
import threading
import subprocess

import ssutils
import constants
from models import models



class StitchMaster(object):
    """docstring for StitchTask"""
    def __init__(self):
        self.ip = "" # 
        self.port = 0
        self.alive = False; # True
        self.heartbeat_time = 0 # in seconds
        self._return_code = None

class Stitcher(threading.Thread):
    def __init__(self, id, task):
        threading.Thread.__init__(self)
        self.id = id
        self.task = task

    def run(self):
        print "start to stich"
        self._return_code = subprocess.call(["ls", "-l"])

    def get_progress():
        # send udp message to state_server
        return

    def get_result():
        if self._return_code < 0:
            return models.STITCHTASK_RESULT_FAILURE
        return models.STITCHTASK_RESULT_OK

class SSWorker(object):
    """docstring for SSMaster"""
    def __init__(self, ip, port, master):
        super(SSWorker, self).__init__()
        self._ip = ip
        self._port = port
        self._master = master
        self._keep_runing = True
        self._tasks = [] # [task1, task2]
        self._completed_tasks = [] # [task_id, task_id]
        self._stitchers = {} # {stitcher_id: stitcher}
        self._task_stitcher_map = {} # {task_id: stitcher_id}
        self._state = models.STITCHWORKER_STATE_IDLE
        self._is_registered = False

        
    def send_request(self, data):
        result, response = ss_send_request(self._master.ip, self._master.port, data)
        if result != 0:
            return None
        return response


    def register(self):
        print "worker:register to %s:%d" %(self._master.ip, self._master.port)
        # update hearbeat_time only if get response from master, 
        id = self.get_id()
        data = {"worker_id":id, 
                "worker_id": self._ip,
                "worker_port": self._port,
                "state":0# 0: idle; 1: busy
                } 
        response = self.send_request(data)
        if response:
            return 0
        return -1


    def unregister(self):
        print "worker:unregister to %s:%d" %(self._master.ip, self._master.port)
        # update hearbeat_time only if get response from master, 
        id = self.get_id()
        data = {"worker_id":id} 
        self.send_request(data)
        return


    def get_id():
        return time.time()


    def send_heartbeat(self):
        # update hearbeat_time only if get response from master, 
        data = {"worker_id":"11111", "state":0} # 0: idle; 1: busy
        response = self.send_request(data)
        if response:
            self._master.heartbeat_time = time.time()
        
        return


    ''' update the basic information about worker. 
        e.g. online/offline, idle/in progress
        worker_state: {
            alive:true,
            status: idle/in-progress/completed
        }
    '''
    def update_master_state(self):
        print "update_master_state"
        cur_time = time.time()
        if cur_time - self._master.heartbeat_time > constants.SS_AVAILABILITY_CHECKING_INTERVAL_TIME:
            self._master.alive = False
        return


    ''' handle worker request '''
    def add_task(self, task):
        task.state = models.STITCHTASK_STATE_READY
        print "add_task, state: %d" %(task.state)
        self._tasks.append(task)
        return


    def remove_task(self, task_id):
        task = self.get_task(task_id)
        print "remove_task"
        self._tasks.remove(task)
        return


    def update_task(self, task_id, stitcher_id):
        task = self.get_task(task_id)
        stitcher = self._stitchers[stitcher_id]

        task.progress = stitcher.get_progress()
        if not stitcher.isAlive():
            self._state == models.STITCHWORKER_STATE_IDLE
            self._stitchers.pop(stitcher_id, None)
            self._task_stitcher_map.pop(task_id, None)

            task.state = models.STITCHTASK_STATE_COMPLETED
            task.result = stitcher.get_result()
            task.end_time = time.time()
            data = self.get_task_info(task.id)
            self.send_request(data)

        return


    def get_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None


    def get_task_info(self, task_id):
        task = self.get_task(task_id)
        data = {
            "task_id": task.id,
            "start_time": task.start_time,
            "progress": self.progress,
            "state": self.state,
            "result": self.result
        }
        return data


    def stitch_task(self, task):
        task.start_time = time.time()
        task.state = models.STITCHJOB_STATE_INPROGRESS;

        stitcher = Stitcher(task.id, task)
        self._stitchers[stitcher.id] = stitcher
        self._task_stitcher_map[task_id] = stitcher_id
        self._state == models.STITCHWORKER_STATE_INPROGRESS
        stitcher.start()


    def start(self):
        t = threading.Thread(target=SSWorker.serve, args=(self,))
        t.start()


    def serve(self):
        last_avail_checking_time = 0
        last_send_heartbeat_time = 0
        last_status_updating_time = 0
        while self._keep_runing:
            if not self._is_registered:
                if self.register() == 0:
                    self._is_registered = True
                    last_avail_checking_time == time.time()
                else:
                    time.sleep(1)
                    continue

            num_assigned_tasks = 0
            for task in self._tasks:
                if self._state == models.STITCHWORKER_STATE_IDLE and task.state == models.STITCHTASK_TASK_READY:
                    stitch_task(task)
                    num_assigned_tasks += 1

            cur_time = time.time()
            if cur_time - last_send_heartbeat_time > constants.SS_HEARTBEAT_INTERVAL_TIME:
                self.send_heartbeat()
                last_send_heartbeat_time = cur_time

            if cur_time - last_avail_checking_time > constants.SS_AVAILABILITY_CHECKING_INTERVAL_TIME:
                self.update_master_state()
                last_avail_checking_time = cur_time

            if cur_time - last_status_updating_time > constants.SS_WORKER_TASK_STATE_UPDATING_INTERVEL_TIME:
                for tid, sid in self._task_stitcher_map.items():
                    self.update_task(tid, sid)

            if num_assigned_tasks == 0:    
                time.sleep(0.1)

        self.unregister()
