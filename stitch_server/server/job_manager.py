import __init__
from collections import defaultdict
import time
from pprint import pprint
import threading
from models import models, sqlutil
from models.sqlutil import segment_db_operator
from segment_manager import SegmentManager
import ssutils
import constants



class JobManager(object):
    def __init__(self, job):
        self.job = job
        self._segment_managers = []
        self._assigned_tasks = defaultdict(set) # {worker_id: [task_id, task_id]}


    def add_segment_manager(self, seg_manager):
        self._segment_managers.append(seg_manager)


    def get_segment_manager(self, segment_id):
        for seg_manager in self._segment_managers:
            if seg_manager.segment.id == segment_id:
                return seg_manager
        return

    def get_segment_manager_by_task(self, task_id):
        job_id, segment_id = SegmentManager.parse_task_id(task_id)
        if job_id != self.job.id:
            return None

        seg_manager = self.get_segment_manager(segment_id)
        return seg_manager

    def get_state(self):
        return self.job.state


    def get_result(self):
        return self.job.result


    def prepare(self, num_workers):
        #split segment into multiple smaller tasks
        self._thread = threading.Thread(target=JobManager.split, args=(self, num_workers))
        self._thread.start()
        return


    # split record to the specified segments
    # it will block
    def split(self, num_workers):
        print "start split job, job_id = %s" % self.job.id
        segment_strs = self.job.segments.split(":")
        pprint(segment_strs)
        num_segments = 0
        for segment_str in segment_strs:
            times = segment_str.split("-")
            from_time = int(times[0])
            to_time = int(times[1])
            if len(times) != 2 or from_time >= to_time:
                continue

            # TODO: 
            # 1. call record_file_utility cmd to split record file
            # 2. call record_file_utility cmd to compute the splited file

            segment = models.StitchSegment()
            segment.id = self.job.id + "%ssegment%d" % (constants.SS_ID_SEPERATOR, num_segments)
            segment.job_id = self.job.id
            segment.src_filename = ""
            segment.src_file_id = ""
            segment.create_time = time.time()
            segment.from_time = from_time
            segment.to_time = to_time
            segment.state = models.STITCH_STATE_READY 
            segment.result = models.STITCH_RESULT_OK

            segment_db_operator.add(segment)
            segment_manager = SegmentManager(segment, self.job.id)
            segment_manager.split(num_workers)
            self.add_segment_manager(segment_manager)
            num_segments += 1

        self.job.state = models.STITCH_STATE_READY
        return


    def cancel(self):
        return


    def get_new_task(self):
        if self.job.state != models.STITCH_STATE_READY and self.job.state != models.STITCH_STATE_INPROGRESS:
            return None
        for seg_manager in self._segment_managers:
            task = seg_manager.get_new_task()
            if task:
                return task
        return None


    def get_task(self, task_id):
        for seg_manager in self._segment_managers:
            task = seg_manager.get_task(task_id)
            if not task:
                return task
        return None

    def if_contain_task(self, task_id):
        task = self.get_task(task_id)
        if not task:
            return False
        return True


    def get_task_ids(self):
        task_ids = []
        for seg_manager in self._segment_managers:
            ids = segment.get_task_ids()
            task_ids.extend(ids)
        return task_ids


    def set_task_state(self, task_id, task_state, task_result):
        job_id, segment_id = SegmentManager.parse_task_id(task_id)
        if job_id != self.job.id:
            return False

        seg_manager = self.get_segment_manager(segment_id)
        if not seg_manager:
            return False

        ret = seg_manager.set_task_state(task_id, task_state, task_result)
        if ret:
            self.update_state()
        return


    def cancel_task(self, task_id):
        seg_manager = get_segment_by_task(task_id)
        if not seg_manager:
            return False

        return seg_manager.cancel_task(task_id)


    def update_state(self):
        job_result = models.STITCH_RESULT_OK
        job_state = models.STITCH_STATE_COMPLETED
        for seg_manager in self._segment_managers:
            if seg_manager.segment.state != models.STITCH_STATE_COMPLETED:
                job_state = models.STITCH_STATE_INPROGRESS
                break
            if seg_manager.segment.state != models.STITCH_RESULT_OK:
                job_result = models.STITCH_RESULT_FAILURE

        self.job.state = job_state
        self.job.result = job_result

        return True
