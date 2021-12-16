#encoding=utf8
import config
import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseCursor:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection=psycopg2.connect(config.pg_conninfo)
        self.commit = False
    
    def select(self,sql,param=None,dict_result=False):
        #print(sql,param)
        import time
        t=time.time()
        cursor=self.connection.cursor(cursor_factory =RealDictCursor)

        cursor.execute(sql,param)
        rows=cursor.fetchall()
        cursor.close()
        #print("RT:",time.time()-t)
        return rows

    def execute(self,sql,param=None):
        cursor=self.connection.cursor()
        ret=cursor.execute(sql,param)
        cursor.close()
        self.commit=True
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
        if self.databaseCursor.commit:
            self.databaseCursor.execute('commit')
        self.databaseCursor.close()


if __name__ == "__main__":
    with Database() as db:
        for row in db.select("explain select count(1) from item_test where name like '%C96%'"):
            print(row)
        for row in db.select("explain select count(1) from item_test where name like '%長島超助%'"):
            print(row)
