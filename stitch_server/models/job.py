from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SS_MAX_PATH = 256
SS_MAX_ID_LEN = 64


class DBStitchJob(base):
    __tablename__ = "stitch_job"

    # table
    id = Column(String(SS_MAX_ID_LEN), primary_key = True)
    src_filename = Column(String(SS_MAX_PATH))
    dst_dir = Column(String(SS_MAX_PATH))
    src_format = Column(String(16))
    map_filename = Column(String(SS_MAX_PATH))
    map_file_id = Column(String(SS_MAX_ID_LEN))
    state = Column(Integer)
    result = Column(Integer)
    create_time = Column(Integer)

    def __init__(self):
        self.id        = ""
        self.src_filename = ""
        self.dst_dir  = ""
        self.src_format = ""
        self.map_filename = ""
        self.map_file_id = ""
        self.state = 0