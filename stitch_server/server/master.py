import __init__
from collections import defaultdict
import time
import threading
import pprint
import copy
from models import models
from models.sqlutil import job_db_operator
import ssutils
import constants
from job_manager import JobManager


class SSMaster(object):
    """docstring for SSMaster"""
    def __init__(self):
        super(SSMaster, self).__init__()
        self._keep_runing = True
        self._workers = [] # [worker...],
        self._job_managers = []

        self._jobs = [] # [job...]
        self._tasks = [] # {task_id: task}
        self._job_tasks = defaultdict() # {job_id: [task_id, task_id]}
        self._assigned_tasks = defaultdict(set) # {worker_id: [task_id, task_id]}
        self._thread = None


    def register_worker(self, worker):
        worker.alive = True
        worker.id = worker.ip + str(worker.port)
        worker.heartbeat_time = time.time()
        print "register worker, worker_id = %s" % worker.id
        self._workers.append(worker)
        return True


    def unregister_worker(self, worker_id):
        worker = self.get_worker(worker_id)
        if not worker:
            return False

        print "unregister worker, worker_id = %s" % worker.id
        assigned_tasks = self._assigned_tasks[worker.id]
        for task in assigned_tasks:
            for job_manager in self._job_managers:
                if job_manager.if_contain_task(task.id):
                    job_manager.set_task_state(task.id, models.STITCH_STATE_READY, models.STITCH_RESULT_OK)
                    break
        self._workers.remove(worker)
        return True


    def worker_heartbeat(self, worker_id, state):
        worker = self.get_worker(worker_id)
        if worker is None:
            return False
        worker.heartbeat_time = time.time()
        worker.state = state
        return True

    ''' update the basic information about worker. 
        e.g. online/offline, idle/in progress
        worker_state: {
            alive:true,
            status: idle/in-progress/completed
        }
    '''
    def update_worker_state(self):
       # print "update_worker_state"
        cur_time = time.time()
        for worker in self._workers:
            if cur_time - worker.heartbeat_time > constants.SS_AVAILABILITY_CHECKING_INTERVAL_TIME:
                self.unregister_worker(worker)
        return


    def get_idle_worker(self):
        for worker in self._workers:
            if worker.alive and worker.state == models.STITCHWORKER_STATE_IDLE:
                return worker
        return None


    def get_worker(self, wid):
        for worker in self._workers:
            if worker.id == wid:
                return worker
        return None


    def get_worker_by_task(self, tid):
        for wid, tids in self._assigned_tasks.items():
            if tid in tids:
                return self.get_worker(wid)
        return  None


    def get_job_manager(self, job_id):
        for job_manager in self._job_managers:
            if job_manager.job.id == job_id:
                return job_manager
        return None


    def get_job_manager_by_task(self, task_id):
        for job_manager in self._job_managers:
            if _job_managers.if_contain_task(task_id):
                return job_manager
        return None


    ''' handle client request '''
    # return job_id if succeed, or None
    def add_job(self, job_dict):
        job = models.StitchJob()
        # TODO: job.id is the same as file_id
        job.id = str(time.time())
        job.src_filename = str(job_dict.get("src_filename", ""))
        job.src_file_id = "" 
        job.dst_dir = str(job_dict.get("dst_dir", ""))
        job.dst_format = str(job_dict.get("dst_format", "flv"))
        job.segments = str(job_dict.get("segments", ""))
        job.map_filename = str(job_dict.get("map_filename", ""))
        job.map_file_id = ""

        print "src_filename = %s, dst_dir = %s" % (job.src_filename, job.dst_dir)
        if job.src_filename == "" or job.dst_dir == "":
            return None

        print "add_job, job_id: %s" % (job.id) 
        try:
            job_db_operator.add(job)
            job_manager = JobManager(job)
            self._job_managers.append(job_manager)
            return job.id
        except Exception as e:
            # TODO: maka a response
            print e.message
        return None


    def remove_job(self, job_id):
        job_manager = self.get_job_manager(job_id)
        if not job_manager:
            return False

        # remove all the associated task
        task_ids = job_manager.get_task_ids()
        for tid in task_ids:
            worker = self.get_worker_by_task(tid)
            self.cancel_task(worker, tid)
        job_manager.cancel()
        self._job_managers.remove(job_manager)
        return True


    def get_job_state(self, job_id):
        print "get_job_state"
        job_manager = self.get_job_manager(job_id)
        if not job_manager:
            return (None, None)
        job = job_manager.job
        return (job.result, job.state)


    def cancel_task(self, worker, task_id):
        # TODO: notify worker
        self._assigned_tasks[worker.id].remove(task_id)
        return

    ''' update state of stask.
        task_state: {
            status: ready/assigned/completed
        }
    '''
    def set_task_state(self, task_id, task_state, task_result):
        job_manager = self.get_job_manager_by_task(task_id)
        if not job_manager:
            return False
        return job_manager.set_task_state(task_id, task_state, task_result)

    '''
    assign task to worker
    '''
    def assign_task(self, task, worker):
        self._assigned_tasks[worker.id].add(task)
        print "assign_task, task_id: %s, task_state: %d" %(task.id, task.state)
        return True

    def start(self):
        self._thread = threading.Thread(target=SSMaster.serve, args=(self,))
        self._thread.start()
    
    def stop(self):
        self._keep_runing = False
        self._thread.join()

    def serve(self):
        last_checking_time = time.time()
        while self._keep_runing:
            num_assigned_tasks = 0

            worker = self.get_idle_worker()
            if worker:
                for job_manager in self._job_managers:
                    if job_manager.get_state() == models.STITCH_STATE_INIT:
                        job_manager.prepare(len(self._workers))
                    while True:
                        task = job_manager.get_new_task()
                        if not task:
                            break
                        if task.state == models.STITCH_STATE_READY:
                            if self.assign_task(task, worker):
                                job_manager.set_task_state(task.id, models.STITCH_STATE_INPROGRESS, models.STITCH_RESULT_OK)
                                num_assigned_tasks += 1


            cur_time = time.time()
            if cur_time - last_checking_time > constants.SS_AVAILABILITY_CHECKING_INTERVAL_TIME:
                self.update_worker_state()
                last_checking_time = cur_time

            if num_assigned_tasks == 0:    
                time.sleep(0.1)