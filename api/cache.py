#coding: utf8

import pickle
import hashlib
import redis
from config import redis_conn
import json
from datetime import datetime,date
class DateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, date):  
            return obj.strftime("%Y-%m-%d")  
        else:  
            return json.JSONEncoder.default(self, obj)


def func_key(func, args, kw):
    '''
    对于无法序列化的参数跳过处理
    '''
    new_args=[]

    for arg in args:
        try:
            pickle.dumps((arg,))
            new_args.append(arg)
        except Exception as e:
            pass
    new_kw={}
    for k,v in kw.items():
        try:
            pickle.dumps(v)
            new_kw[k]=v
        except:
            pass
    key = pickle.dumps((func.__name__, new_args, new_kw))
    return hashlib.sha1(key).hexdigest()


def cache_wrapper(timeout=0):
    def _cache(func):
        def __cache(*args, **kw):
            key = func_key(func, args, kw)
            conn=redis.Redis(**redis_conn)
            value=conn.get(key)
            if value:
                return json.loads(value)
            result = func(*args, **kw)
            json_result=json.dumps(result, ensure_ascii=False,cls=DateEncoder)
            if timeout == 0:
                conn.set(key, json_result,3600)
            else:
                conn.set(key, json_result, timeout)
            return result
        return __cache
    return _cache
