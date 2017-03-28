import time
from models import StitchJob
import models
from sqlutil import DBJobOperator



job = StitchJob()
job.id = time.time()
job.src_filename = "/tmp/dump.bin"
job.src_file_id = "xxxxxxx" 
job.dst_dir = "/tmp/"
job.dst_format = "flv"
job.map_filename = "map.offline.4k.map"
job.map_file_id = "xxxx"
job.state = models.STITCHJOB_STATE_READY 
job.result = models.STITCHJOB_RESULT_FAILURE
job.create_time = time.time()


DBJobOperator.add(job)