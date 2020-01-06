#encoding=utf8
import config
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseCursor:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection=psycopg2.connect(config.pg_conninfo)
    
    def select(self,sql,param=None,dict_result=False):

        cursor=self.connection.cursor(cursor_factory =RealDictCursor)

        cursor.execute(sql,param)
        rows=cursor.fetchall()
        cursor.close()
        return rows

    def execute(self,sql,param=None):
        cursor=self.connection.cursor()
        ret=cursor.execute(sql,param)
        cursor.close()
        return ret

    def close(self):
        self.connection.close()

class Database(object):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self):
        self.databaseCursor=DatabaseCursor()
        return self.databaseCursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.databaseCursor.execute('commit')
        self.databaseCursor.close()
