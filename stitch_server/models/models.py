import time

STITCHJOB_STATE_READY = 0
STITCHJOB_STATE_INPROGRESS = 1
STITCHJOB_STATE_COMPLETED = 2

STITCHJOB_RESULT_OK = 0
STITCHJOB_RESULT_FAILURE = 2


STITCHTASK_STATE_READY = 0
STITCHTASK_STATE_ASSIGNED = 1
STITCHTASK_STATE_COMPLETED = 2

STITCHTASK_RESULT_OK = 0
STITCHTASK_RESULT_FAILURE = -1

STITCHWORKER_STATE_IDLE = 0
STITCHWORKER_STATE_INPROGRESS = 1



class StitchTask(object):
    """docstring for StitchTask"""
    def __init__(self):
        self.id = "" # must be equal to self.src_file_id
        self.job_id = ""
        self.src_filename = "" # record-3-13.bin
        '''src_file_id: md5 genearted by record_file_utility,
            the value is unique
        '''
        self.src_file_id = "" 
        self.dst_dir = ""
        self.dst_format = "" # flv, mp4
        self.map_filename = "" # map.offline.4k.map
        self.map_file_id = "" # md5 genearted by md5sum cmd
        self.create_time = time.time()
        self.start_time = ""
        self.end_time = ""
        self.worker_id = "" # ip of worker
        self.progress = 0 # used by worker
        self.state = STITCHTASK_STATE_READY
        self.result = STITCHTASK_RESULT_FAILURE


class StitchJob(object):
    """docstring for StitchTask"""
    def __init__(self):
        self.id = "" # must be equal to self.src_file_id
        self.src_filename = "" # record.bin
        '''src_file_id: md5 genearted by record_file_utility,
            the value is unique
        '''
        self.src_file_id = "" 
        self.dst_dir = ""
        self.dst_format = "" # flv, mp4
        self.map_filename = "" # map.offline.4k.map
        self.map_file_id = "" # md5 genearted by md5sum cmd
        self.state = STITCHJOB_STATE_READY 
        self.result = STITCHJOB_RESULT_FAILURE
        self.create_time = time.time()


class StitchWorker(object):
    """docstring for StitchTask"""
    def __init__(self):
        self.id = "" # ip:port
        self.ip = "" # 
        self.port = 0
        self.alive = False; # True
        self.state = STITCHWORKER_STATE_IDLE
        self.heartbeat_time = 0 # in seconds