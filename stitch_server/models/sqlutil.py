import __init__
from pprint import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import constants
from models import StitchJob, StitchTask, StitchSegment

conn_str = "mysql+pymysql://root:coryee@localhost:3306/%s" % (constants.SS_DB_NAME)
DBEngine = create_engine(conn_str, echo = True)

session_maker = sessionmaker(bind=DBEngine)
DBSession = session_maker()


class DBOperator(object):
    def __init__(self):
        return

    def db_oject(self):
        return None

    def add(self, obj):
        print "add obj into db"
        DBSession.add(obj)
        DBSession.commit()
        print "add obj into db end"

    def query_by_id(self, id):
        query = DBSession.query(self.db_oject()).filter_by(id=id)
        for job in query:
            return job
        return None

    def query(self, order_by, offset, limit):
        return DBSession.query(self.db_oject()).order_by(order_by)[offset:limit]

    def delete(self, obj):
        DBSession.delete(obj)
        DBSession.commit()

    def delete_by_id(self, id):
        return



class DBJobOperator(DBOperator):
    def __init__(self):
        return

    def db_oject(self):
        return StitchJob

    # def query_by_id(self, id):
    #     result = DBSession.query(StitchJob).filter(StitchJob.id == "1490776760.13")
    #     return result

    def update(self, obj):
        print "DBJobOperator update"
        DBSession.query(obj)

    
    def delete_by_id(self, id):
        DBSession.query(StitchJob).filter_by(id=id).delete()
        return



class DBSegmentOperator(DBOperator):
    def __init__(self):
        return

    def update(self, obj):
        DBSession.query(obj)


    def query(self, order_by, offset, limit):
        return DBSession.query(StitchSegment).order_by(StitchSegment.create_time)[offset:limit]


    def delete_by_id(self, id):
        DBSession.query(StitchSegment).filter_by(id=id).delete()
        return

    def delete_by_id(self, job_id):
        DBSession.query(StitchSegment).filter_by(job_id=job_id).delete()
        return


job_db_operator = DBJobOperator()
segment_db_operator = DBSegmentOperator()
