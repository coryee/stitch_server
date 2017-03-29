import __init__
from collections import defaultdict
import time
import threading
from models import models, sqlutil
#from models import DBJobOperator
import ssutils
import constants



class SegmentManager(object):
    def __init__(self, segment, job_id):
        self.segment = segment
        self._job_id = job_id
        self._tasks = [] # [task...]

    @classmethod
    def generate_task_id(clazz, job_id, segment_id, task_idx):
        task_id = segment_id + "%stask%d" % (constants.SS_ID_SEPERATOR, task_idx)
        return task_id


    @classmethod
    def parse_task_id(clazz, task_id):
        ids = task_id.split(constants.SS_ID_SEPERATOR)
        job_id = ids[0]
        segment_id = job_id + constants.SS_ID_SEPERATOR + ids[1]
        return (job_id, segment_id)


    def add_task(self, task):
        self._tasks.append(task)


    def get_new_task(self):
        if self.segment.state != models.STITCH_STATE_READY and self.segment.state != models.STITCH_STATE_INPROGRESS:
            return  None
        for task in self._tasks:
            if task.state == models.STITCH_STATE_READY:
                return task
        return None


    def get_task(self, task_id):
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def get_task_ids(self):
        task_ids = []
        for task in self._tasks:
            task_ids.append(task.id)
        return task_ids


    def cancel_task(self, task_id):
        task = get_task(task_id)
        if not task:
            return False
        
        return self.set_task_state(task_id, models.STITCH_STATE_READY, models.STITCH_RESULT_FAILURE)


    def set_task_state(self, task_id, state, result):
        task = self.get_task(task_id)
        if not task:
            return False

        task.state = state
        task.result = result
        self.update_state()
        return True


    def update_state(self):
        segment_result = models.STITCH_RESULT_OK
        segment_state = models.STITCH_STATE_COMPLETED
        for t in self._tasks:
            if t.state != models.STITCH_STATE_COMPLETED:
                segment_state = models.STITCH_STATE_INPROGRESS
                break
            if t.result != models.STITCH_RESULT_OK:
                segment_result = models.STITCH_RESULT_FAILURE

        self.segment.state = segment_state
        self.segment.result = segment_result
        return True


    def split(self, num_workers):
        print "start split segment, id = %s" % self.segment.id
        segment_duration = self.segment.to_time - self.segment.from_time
        
        if num_workers == 0:
           task_duration = constants.SS_MIN_TASK_DURATION 
        else:
            task_duration = float(segment_duration) / num_workers
            if task_duration > constants.SS_MIN_TASK_DURATION:
                task_duration = constants.SS_MIN_TASK_DURATION

        total_duration = 0
        num_task = 0
        while total_duration < segment_duration:
            from_time = num_task * task_duration
            to_time = from_time + task_duration
            if to_time > segment_duration:
                to_time = segment_duration
            total_duration += to_time - from_time
            # TODO: 
            # 1. call record_file_utility cmd to split record file
            # 2. call record_file_utility cmd to compute the splited file

            task = models.StitchJob()
            task.id = SegmentManager.generate_task_id(self.segment.job_id, self.segment.id, num_task)
            task.src_filename = ""
            task.src_file_id = "" 
            task.create_time = time.time()
            task.start_time = ""
            task.end_time = ""
            task.progress = 0 
            task.state = models.STITCH_STATE_READY
            task.result = models.STITCH_RESULT_OK
            self.add_task(task)
            num_task += 1
            print "split task, id = %s from_time = %d, to_time = %d" % (task.id, from_time, to_time)
        self.segment.state = models.STITCH_STATE_READY
        return