#encoding=utf8

from db import Database
import hashlib
'''
create table lib_user (
    username varchar(128) primary key,
    passwd varchar(256),
    last_lib int,
    last_dir int
);

create table user_library(
    userename varchar(128),
    library_id int
);
'''

SALT='liuwei'

def get_password(username,password):
    return hashlib.md5(bytes(username+password+SALT,'utf8')).hexdigest()

class User(object):

    def __init__(self):
        pass
    @staticmethod
    def change(username,password,new_username=None,new_password=None):
        if User.login(username,password):

            with Database() as db:
                if new_password:
                    if new_username:
                        passwd=get_password(new_username ,new_password)
                    else:
                        passwd=get_password(username ,new_password)
                    db.execute("update lib_user set passwd=%s where username=%s",(passwd,username))
                if new_username:
                    db.execute("update lib_user set username=%s where username=%s",(new_username,username))
            return True
        return False
    @staticmethod
    def login(username,password):
        with Database() as db:
            rows=db.select("select count(1) c from lib_user where username =%s and passwd=%s",(username,get_password(username,password)))
            return rows[0]['c']==1
    @staticmethod
    def isLogin(username,token):
        with Database() as db:
            rows=db.select("select count(1) c from lib_user where username =%s and passwd=%s",(username,token))
            return rows[0]['c']==1
    @staticmethod
    def register(username,password):
        with Database() as db:
            rows=db.select('select count(1) c from lib_user where username=%s',(username,))
            if rows[0]['c']==1:
                raise Exception("用户已经存在")
            db.execute("insert into lib_user (username,passwd) values(%s,%s)",(username,get_password(username,password)))


if __name__=='__main__':
    User.register('liu','llzx')
    print(User.login('liu','llzx'))
