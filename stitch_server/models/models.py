import __init__
import time
from sqlalchemy import Column, String, Integer, Float, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import constants

STITCH_STATE_INIT = 0
STITCH_STATE_READY = 1
STITCH_STATE_INPROGRESS = 2
STITCH_STATE_COMPLETED = 3

STITCH_RESULT_OK = 0
STITCH_RESULT_FAILURE = -1

STITCHWORKER_STATE_IDLE = 0
STITCHWORKER_STATE_INPROGRESS = 1

Base = declarative_base()
 

class StitchTask(Base):
    __tablename__ = "stitch_task"

    # table
    id = Column(String(constants.SS_MAX_ID_LEN), primary_key = True)
    src_filename = Column(String(constants.SS_MAX_PATH))
    src_file_id = Column(String(constants.SS_MAX_ID_LEN))
    dst_dir = Column(String(constants.SS_MAX_PATH))
    dst_format = Column(String(constants.SS_MAX_MEDIA_FORMAT))
    map_filename = Column(String(constants.SS_MAX_PATH))
    map_file_id = Column(String(constants.SS_MAX_ID_LEN))
    create_time = Column(Integer)
    start_time = Column(Integer)
    end_time = Column(Integer)
    worker_id = Column(String(constants.SS_MAX_ID_LEN))
    progress = Column(Float)
    state = Column(Integer)
    result = Column(Integer)

    def __init__(self):
        self.id = "" # must be equal to self.src_file_id
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
        self.state = STITCH_STATE_READY
        self.result = STITCH_RESULT_OK


class StitchJob(Base):
    __tablename__ = "stitch_job"

    # table
    id = Column(String(constants.SS_MAX_ID_LEN), primary_key = True)
    src_filename = Column(String(constants.SS_MAX_PATH))
    src_file_id = Column(String(constants.SS_MAX_ID_LEN))
    dst_dir = Column(String(constants.SS_MAX_PATH))
    dst_format = Column(String(constants.SS_MAX_MEDIA_FORMAT))
    map_filename = Column(String(constants.SS_MAX_PATH))
    map_file_id = Column(String(constants.SS_MAX_ID_LEN))
    segments = Column(String(constants.SS_MAX_PATH))
    state = Column(Integer)
    result = Column(Integer)
    create_time = Column(Integer)

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
        self.segments = "" # 1-5:20-35 ...
        self.state = STITCH_STATE_INIT 
        self.result = STITCH_RESULT_OK
        self.create_time = time.time()

    def to_dict(self):
        result = {}
        result["id"] = self.id
        result["src_filename"] = self.src_filename
        result["dst_dir"] = self.dst_dir
        result["dst_format"] = self.dst_format
        result["segments"] = self.segments
        result["state"] = self.state
        result["result"] = self.result
        result["create_time"] = self.create_time
        return result


class StitchSegment(Base):
    __tablename__ = constants.SS_DB_SEGMENT_TABLE_NAME

    # table
    id = Column(String(constants.SS_MAX_ID_LEN), primary_key = True)
    job_id = Column(String(constants.SS_MAX_ID_LEN), ForeignKey("stitch_job.id"))
    src_filename = Column(String(constants.SS_MAX_PATH))
    src_file_id = Column(String(constants.SS_MAX_ID_LEN))
    create_time = Column(Integer)
    from_time = Column(Integer)
    to_time = Column(Integer)
    state = Column(Integer)
    result = Column(Integer)

    def __init__(self):
        self.id = ""
        self.job_id = ""
        self.src_filename = "" # record.bin
        '''src_file_id: md5 genearted by record_file_utility,
            the value is unique
        '''
        self.src_file_id = "" 
        self.create_time = time.time()
        self.from_time = 0
        self.to_time = 0
        self.state = STITCH_STATE_INIT 
        self.result = STITCH_RESULT_OK


class StitchWorker(object):
    """docstring for StitchTask"""
    def __init__(self):
        self.id = "" # ip:port
        self.ip = "" # 
        self.port = 0
        self.alive = False; # True
        self.state = STITCHWORKER_STATE_IDLE
        self.heartbeat_time = 0 # in seconds