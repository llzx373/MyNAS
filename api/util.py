#encoding=utf8
import json
from flask import make_response
from datetime import date, datetime
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


def json_return(result):
    response = make_response(json.dumps(
        result, ensure_ascii=False, cls=DateEncoder))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Content-Type'] = 'text/html;charset=UTF-8'
    return response


def not_found(message='not found'):
    response = make_response(message, 404)
    return response