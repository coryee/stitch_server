import MySQLdb

import constants

def init_db():
    conn = MySQLdb.connect(host = "127.0.0.1", user = constants.SS_DB_USER, passwd = constants.SS_DB_PASSWD)
    cursor = conn.cursor()

    create_db_sql = "create database if not exists %s" % (constants.SS_DB_NAME)
    cursor.execute(create_db_sql)
    conn.select_db(constants.SS_DB_NAME)

    create_job_sql = """ create table if not exists %s
        (
            id varchar(%d),
            src_filename varchar(%d),
            src_file_id varchar(%d),
            dst_dir varchar(%d),
            dst_format varchar(%d),
            map_filename varchar(%d),
            map_file_id varchar(%d),
            segments varchar(%d),
            state int(3),
            result int(3),
            create_time int(64)
        )
        """ % (constants.SS_DB_JOB_TABLE_NAME, constants.SS_MAX_ID_LEN, constants.SS_MAX_PATH,
            constants.SS_MAX_ID_LEN, constants.SS_MAX_PATH, constants.SS_MAX_MEDIA_FORMAT, 
            constants.SS_MAX_PATH, constants.SS_MAX_ID_LEN, constants.SS_MAX_PATH)
    cursor.execute(create_job_sql)

    segment_table_sql = """ create table if not exists %s
        (
            id varchar(%d),
            job_id varchar(%d),
            src_filename varchar(%d),
            src_file_id varchar(%d),
            create_time int(64),
            from_time int(32),
            to_time int(32),
            state int(3),
            result int(3)
        )
        """ % (constants.SS_DB_SEGMENT_TABLE_NAME, constants.SS_MAX_ID_LEN, constants.SS_MAX_ID_LEN, 
            constants.SS_MAX_PATH, constants.SS_MAX_ID_LEN)
    print segment_table_sql
    cursor.execute(segment_table_sql)


    cursor.close()