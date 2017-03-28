import sys
sys.path.append("..")

from collections import defaultdict
import time
import threading
from models import models
import ssutils
import constants


class SSMaster(object):
    """docstring for SSMaster"""
    def __init__(self):
        super(SSMaster, self).__init__()
        self._keep_runing = True
        self._workers = {} # {worker_id: worker},
        self._jobs = {} # {job_id: job}
        self._tasks = {} # {task_id: task}
        self._job_tasks = defaultdict() # {job_id: [task_id, task_id]}
        self._assigned_tasks = defaultdict(set) # {worker_id: [task_id, task_id]}

    def register_worker(self, worker):
        print "register worker, worker_id = %s" % worker.id
        worker.alive = True
        self._workers[worker.id] = worker
        return

    def unregister_worker(self, worker_id):
        worker = self._workers.get(worker_id, None)
        if worker is None:
            return

        print "unregister worker, worker_id = %s" % worker.id
        assigned_tasks = self._assigned_tasks[worker.id]
        for task in assigned_tasks:
            task.state = models.STITCHTASK_STATE_READY
            task.result = models.STITCHTASK_RESULT_FAILURE
        worker.alive = False
        return

    def worker_heartbeat(self, worker_id, state):
        worker = self._workers.get(worker_id, None)
        if worker is None:
            return
        worker.heartbeat_time = time.time()
        worker.state = state
        return

    ''' update the basic information about worker. 
        e.g. online/offline, idle/in progress
        worker_state: {
            alive:true,
            status: idle/in-progress/completed
        }
    '''
    def update_worker_state(self):
        print "update_worker_state"
        cur_time = time.time()
        for key in self._workers:
            worker = self._workers[key]
            if cur_time - worker.heartbeat_time > constants.SS_AVAILABILITY_CHECKING_INTERVAL_TIME:
                self.unregister_worker(worker)
        return

    def get_idle_worker(self):
        for key in self._workers:
            worker = self._workers[key]
            if worker.alive and worker.state == models.STITCHWORKER_STATE_IDLE:
                return self._workers[key]
        return None

    ''' handle client request '''
    def add_job(self, job):
        print "add_job, job_id: %s" % (job.id) 
        self._jobs[job.id] = job
        return

    def remove_job(self, job_id):
        print "remove_job, job_id: %s" % (job.id)
        #TODO: remove all the associated task
        task_ids = self._job_tasks[job.id]
        for tid in task_ids:
            self._tasks.pop(tid, None)

        self._jobs.pop(job_id, None)
        #del self._jobs[job.id]
        return

    def set_job_state(self, job_id, state, result):
        print "set_job_state"
        self._jobs[jog_id].state = state
        self._jobs[jog_id].result = result
        return 

    def get_job_state(self, job_id):
        print "get_job_state"
        return self._jobs[jog_id].state

    def split_job_into_tasks(self, job):
        print "split_job_into_tasks"
        id = time.time()
        tasks = []
        for i in range(2):
            id += i
            task = models.StitchTask()
            task.id = id
            task.src_filename = task.id
            task.src_file_id = task.id 
            task.state = models.STITCHTASK_STATE_READY
            tasks.append(task)
        return tasks

    ''' handle worker request '''

    def add_task(self, task):
        print "add_task, state: %d" %(task.state)
        self._tasks[task.id] = task
        return

    def remove_task(self, task):
        print "remove_task"
        self._tasks.pop(task.id, None)
        return

    ''' update state of stask.
        task_state: {
            status: ready/assigned/completed
        }
    '''
    def set_task_state(self, task_id, task_state, task_result):
        task = self._tasks[task_id]
        task.state = task_state
        task.result = task_result

        job_id = task.job_id
        job = self._jobs[job_id]
        task_ids = self._job_tasks[job_id]
        all_task_completed = True
        job_result = STITCHTASK_RESULT_OK
        for tid in task_ids:
            t = self._tasks[tid]
            if t.state != models.STITCHTASK_STATE_COMPLETED:
                all_task_completed = False
                break
            if t.result != STITCHTASK_RESULT_OK:
                job_result = models.STITCHJOB_RESULT_FAILURE

        if all_task_completed:
            self.set_job_state(job_id, models.STITCHTASK_STATE_COMPLETED, job_result)

        return

    '''
    assign task to worker
    '''
    def assign_task(self, task, worker):
        task.state = models.STITCHTASK_STATE_ASSIGNED
        self._assigned_tasks[worker.id].add(task)
        print "assign_task, task_id: %s, task_state: %d" %(task.id, task.state)
        return

    def start(self):
        t = threading.Thread(target=SSMaster.serve, args=(self,))
        t.start()

    def serve(self):
        last_checking_time = time.time()
        while self._keep_runing:
            for key in self._jobs:
                job = self._jobs[key]
                if job.state == models.STITCHJOB_STATE_READY:
                    tasks = self.split_job_into_tasks(job)
                    for task in tasks:
                        self.add_task(task)
                    job.state = models.STITCHJOB_STATE_INPROGRESS;

            num_assigned_tasks = 0
            for key in self._tasks:
                task = self._tasks[key]
                if task.state == models.STITCHTASK_STATE_READY:
                    worker = self.get_idle_worker()
                    if worker:
                        self.assign_task(task, worker)
                        num_assigned_tasks += 1
                    else:
                        break

            cur_time = time.time()
            if cur_time - last_checking_time > constants.SS_AVAILABILITY_CHECKING_INTERVAL_TIME:
                self.update_worker_state()
                last_checking_time = cur_time

            if num_assigned_tasks == 0:    
                time.sleep(0.1)
