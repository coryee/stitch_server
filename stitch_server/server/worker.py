import __init__
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

class Stitcher(object):
    def __init__(self, id, task):
        threading.Thread.__init__(self)
        self.id = id
        self.task = task
        self._process = None

    def process(self):
        print "start to stich"
        FNULL = open(os.devnull, 'w')
        # do not print output on terminal window
        self._process = subprocess.Popen(["ls", "-l", "/tmp"], stdout=FNULL, stderr=subprocess.STDOUT)


    def is_running(self):
        ret_code = self._popen.poll()
        if ret_code is None:
            return True
        return False

    def cancel(self):
        self._process.kill()
        return True

    def get_progress(self):
        # send udp message to state_server
        return

    def get_result(self):
        '''
        The child return code, set by poll() and wait()(and indirectly by communicate()),
        A None value indicates that the process hasn't terminated yet.
        A negative value -N indicates that the child was terminated by signal N (Unix only)
        0 succeed; > 0, error; -1 terminated by signal
        '''
        ret_code = self._popen.poll()
        if ret_code is None or ret_code != 0:

        #if self._return_code < 0:
            return models.STITCH_RESULT_FAILURE

        return models.STITCH_RESULT_OK


class SSWorker(object):
    """docstring for SSMaster"""
    def __init__(self):
        super(SSWorker, self).__init__()
        self._ip = ""
        self._port = 0
        self._master = None
        self._keep_runing = True
        self._tasks = [] # [task1, task2]
        self._completed_tasks = [] # [task_id, task_id]
        self._stitchers = {} # {stitcher_id: stitcher}
        self._task_stitcher_map = {} # {task_id: stitcher_id}
        self._state = models.STITCHWORKER_STATE_IDLE
        self._is_registered = False
        self._thread = None


    def set_master(self, master):
        self._master = master

    def set_url(self, ip, port):
        self._ip = ip
        self._port = port

        
    def send_request(self, api, data):
        print "send_reqeust: %s:%d%s" % (self._master.ip, self._master.port, api)
        result, response = ssutils.ss_send_request(self._master.ip, self._master.port, api, data)
        if result != 0:
            return None
        return response


    def register(self):
        # update hearbeat_time only if get response from master, 
        id = self.get_id()
        data = {"worker_id":id, 
                "worker_id": self._ip,
                "worker_port": self._port,
                "state":0# 0: idle; 1: busy
                } 
        response = self.send_request(constants.MASTER_API_REGISTER, data)
        if response:
            print "worker:register to %s:%d" %(self._master.ip, self._master.port)
            return True
        return False


    def unregister(self):
        print "worker:unregister to %s:%d" %(self._master.ip, self._master.port)
        # update hearbeat_time only if get response from master, 
        id = self.get_id()
        data = {"worker_id":id} 
        self.send_request(constants.MASTER_API_UNREGISTER, data)
        return


    def get_id(self):
        return time.time()


    def send_heartbeat(self):
        # update hearbeat_time only if get response from master, 
        data = {"worker_id":"11111", "state":0} # 0: idle; 1: busy
        response = self.send_request(constants.MASTER_API_HEARTBEAT, data)
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
    def add_task(self, task_dict):
        task = models.StitchTask()
        task.id = str(payload.get("id", ""))
        task.src_filename = str(payload.get("src_filename", ""))
        task.src_file_id = str(payload.get("src_file_id", ""))
        task.dst_dir = str(payload.get("dst_dir", ""))
        task.dst_format = str(payload.get("dst_format", ""))
        task.map_filename = str(payload.get("map_filename", ""))
        task.map_file_id = str(payload.get("map_file_id", ""))
        if task.id == "" or task.src_filename == "" or \
            task.src_file_id == "" or task.dst_dir == "" or \
            task.dst_format == "" or task.map_filename == "" or \
            task.map_file_id == "":
            return False

        task.state = models.STITCH_STATE_READY
        print "add_task, state: %d" %(task.state)
        self._tasks.append(task)
        return


    def cancel_task(self, task_id):
        task = self.get_task(task_id)
        if not task:
            return False
        print "remove_task"
        stitcher_id = self._task_stitcher_map[task_id]
        stitcher = self._stitchers[stitcher_id]
        stitcher.cancel()
        self._stitchers.pop(stitcher_id, None)
        self._task_stitcher_map.pop(task_id, None)
        self._tasks.remove(task)
        self._state = models.STITCHWORKER_STATE_IDLE
        return True


    def update_task(self, task_id, stitcher_id):
        task = self.get_task(task_id)
        stitcher = self._stitchers[stitcher_id]

        task.progress = stitcher.get_progress()
        if not stitcher.is_running():
            task.state = models.STITCH_STATE_COMPLETED
            task.result = stitcher.get_result()
            self._state == models.STITCHWORKER_STATE_IDLE
            self._task_stitcher_map.pop(task_id, None)
            self._stitchers.pop(stitcher_id, None)
            data = self.get_task_info(task.id)
            self.send_request(data)

        return


    def get_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None


    def get_task_info(self, task_id):
        data = {}
        task = self.get_task(task_id)
        if task:
            data = {
                "id": task.id,
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
        stitcher.process()


    def start(self):
        self._thread = threading.Thread(target=SSWorker.serve, args=(self,))
        self._thread.start()

    def stop(self):
        self._keep_runing = False
        self._thread.join()

    def serve(self):
        last_avail_checking_time = 0
        last_send_heartbeat_time = 0
        last_status_updating_time = 0
        while self._keep_runing:
            if not self._is_registered:
                if self.register():
                    self._is_registered = True
                    last_avail_checking_time == time.time()
                else:
                    time.sleep(1)
                    continue

            num_assigned_tasks = 0
            for task in self._tasks:
                if self._state == models.STITCHWORKER_STATE_IDLE and task.state == models.STITCH_STATE_READY:
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
