import __init__
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import constants

conn_str = "mysql+pymysql://root:coryee@localhost:3306/%s" % (constants.SS_DB_NAME)
DBEngine = create_engine(conn_str, echo = True)

session_maker = sessionmaker(bind=DBEngine)
DBSession = session_maker()


class DBOperator(object):
    @classmethod
    def add(clazz, obj):
        print "add obj into db"
        DBSession.add(obj)
        DBSession.commit()

    @classmethod
    def delete(clazz, obj):
        DBSession.delete(obj)
        DBSession.commit()

    @classmethod
    def query(clazz, obj):
        DBSession.query(obj)


class DBJobOperator(DBOperator):
    @classmethod
    def update(clazz, obj):
        DBSession.query(obj)


class DBTaskOperator(DBOperator):
    @classmethod
    def update(clazz, obj):
        DBSession.query(obj)

