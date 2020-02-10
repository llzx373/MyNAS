# encoding=utf8
from flask import Flask
from flask import render_template
from flask import make_response, send_file, request, Response,send_from_directory
from werkzeug.utils import secure_filename
from datetime import date, datetime
import hashlib
import json
from db import Database
from cache import cache_wrapper
import os
from library import Library
from user import User, get_password
from book import Chapter
from config import PHOTO_BUF_SIZE, PHOTO_CATCH, ffmpeg_path, ffprobe_path, file_ex2type,ffmpeg_codec
import config
import mimetypes
import re
from PIL import Image
import random
import zipfile
import rarfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import subprocess

executor = ThreadPoolExecutor(8)
from flask_cors import CORS

app = Flask(__name__, static_url_path='/static')
CORS(app)
# render = web.template.render('web/')


def flush_lib(lib_id):
    '''
    这里入口更新库状态，要求必须是syncing之外的状态才可以
    lib内sync出口更新库状态
    '''
    with Database() as db:
        status = db.select("select status from library where id=%s",
                           (lib_id,), dict_result=True)[0]['status']
        if status == 'syncing':
            return {
                'message': "当前正在执行同步任务，无法另外启动"
            }
        db.execute("update library set status=%s where id=%s",
                   ('syncing', lib_id))

    def inner_flush_lib(lib_id):
        lib = Library.get(lib_id)
        lib.sync()
    executor.submit(inner_flush_lib, lib_id)
    return {
        'message': "已经开始执行同步任务"
    }


@app.route('/')
def index():
    return render_template('index.html')


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


def get_file(file_id):
    with Database() as db:
        row = db.select("select id,name,path,null file from item where id=%s",
                        (file_id,), dict_result=True)[0]
        return row


def sub_items(lib_id, dir_id, items_per_page=36, page=1):
    with Database() as db:
        count = db.select("select count(1) c from item where library_id=%s and parent=%s and order_id=-1",
                          (lib_id, dir_id), dict_result=True)[0]['c']

        '''
        很多文件命名混乱,此处重排
        新增列order_id 从0开始排序到最大
        逻辑如下：
        1. 根据名称中的数字数量
            没有数字的，按照字母顺序放在最前面
            对于只有一个数字的，直接排序
            多个数字的，分别处理，目前仅考虑最大有4个数字的
        '''
        num_0 = []
        num_1 = []
        num_2 = []
        num_3 = []
        num_4 = []
        if count == 0:
            offset = (page-1)*items_per_page
            return db.select("select id,name,item_type,cover,order_id,library_id,file_type from item where library_id=%s and parent=%s order by order_id limit %s offset %s", (lib_id, dir_id, items_per_page, offset), dict_result=True)

        # 文件夹排序必须在文件前面
        items = []
        dir_rows = db.select(
            "select id,name,order_id from item where library_id=%s and parent=%s and item_type='dir'", (lib_id, dir_id), dict_result=True)
        for row in dir_rows:
            items.append(
                {
                    'id': row['id'],
                    'name': row['name']
                }
            )
        items.sort(key=lambda k: k['name'])
        rows = db.select("select id,name,order_id from item where library_id=%s and parent=%s and item_type='file'",
                         (lib_id, dir_id), dict_result=True)
        for row in rows:
            rf = re.findall('([\d]+)', row['name'])
            if not rf:
                num_0.append({
                    'id': row['id'],
                    'name': row['name'],
                    'sort_key': row['name']
                })
                continue
            rf = [int(x) for x in rf]
            if len(rf) == 1:
                num_1.append({
                    'id': row['id'],
                    'name': row['name'],
                    'sort_key': rf[0]
                })
            elif len(rf) == 2:
                num_2.append({
                    'id': row['id'],
                    'name': row['name'],
                    'sort_key': rf
                })
            elif len(rf) == 3:
                num_3.append({
                    'id': row['id'],
                    'name': row['name'],
                    'sort_key': rf
                })
            elif len(rf) == 4:
                num_4.append({
                    'id': row['id'],
                    'name': row['name'],
                    'sort_key': rf
                })
            else:
                num_0.append({
                    'id': row['id'],
                    'name': row['name'],
                    'sort_key': row['name']
                })
        num_0.sort(key=lambda k: k['sort_key'])
        num_1.sort(key=lambda k: k['sort_key'])
        num_2.sort(key=lambda k: ''.join(
            [str(x).zfill(8) for x in k['sort_key']]))
        num_3.sort(key=lambda k: ''.join(
            [str(x).zfill(8) for x in k['sort_key']]))
        num_4.sort(key=lambda k: ''.join(
            [str(x).zfill(8) for x in k['sort_key']]))
        items.extend(num_0)
        items.extend(num_1)
        items.extend(num_2)
        items.extend(num_3)
        items.extend(num_4)

        for i, item in enumerate(items):
            db.execute('update item set order_id=%s where id=%s',
                       (i, item['id']))
        db.execute('commit')

        offset = (page-1)*items_per_page
        return db.select("select id,name,item_type,order_id,cover,library_id,file_type from item where library_id=%s and parent=%s order by order_id limit %s offset %s", (lib_id, dir_id, items_per_page, offset), dict_result=True)


@cache_wrapper()
def sub_item_count(lib_id, dir_id, item_type=None):
    with Database() as db:
        if item_type:
            return db.select("select count(1) c from item where library_id=%s and parent=%s and item_type=%s", (lib_id, dir_id, item_type), dict_result=True)[0]['c']
        return db.select("select count(1) c from item where library_id=%s and parent=%s", (lib_id, dir_id), dict_result=True)[0]['c']


@cache_wrapper()
def get_dir(lib_id, dir_id):
    with Database() as db:
        if dir_id == 0:
            return {
                'id': 0,
                'name': "",
                'cover': "",
                'path': "",
                "library_id": lib_id,
                "version": 0,
                "parent": 0,
                "order_id": -1
            }
        return db.select("select id,name,cover,path,library_id,version,parent,order_id from item where library_id=%s and id=%s", (lib_id, dir_id), dict_result=True)[0]


@cache_wrapper()
def get_parent(lib_id, dir_id):
    '''
    获取目录的父目录的id
    逐个查询目录
    '''
    with Database() as db:

        row = db.select("select name,path,order_id from  item where library_id=%s and id=%s",
                        (lib_id, dir_id), dict_result=True)[0]
        result = [{
            'id': dir_id,
            'name': row['name'],
            'order_id':row['order_id'],
            'sub_order_id':1
        }, ]
        sub_order_id=result[0]['order_id']
        dsp = row['path'].split(os.path.sep)
        for i in range(1, len(dsp)+1):
            dname = os.path.sep.join(dsp[:-i])
            rows = db.select("select id,name,order_id from  item where library_id=%s and path=%s",
                             (lib_id, dname), dict_result=True)
            if rows:
                result.append(
                {
                    'id':rows[0]['id'],
                    'name':rows[0]['name'],
                    'order_id':rows[0]['order_id'],
                    'sub_order_id':sub_order_id
                })
                sub_order_id=result[-1]['order_id']
            else:
                continue
        result.reverse()
        return result


def get_library(lib_id):
    with Database() as db:
        return db.select("select id,name,dir,status,version from library where id=%s", (lib_id,), dict_result=True)[0]


@cache_wrapper()
def get_cover_for_video(file_name, file_path):
    cn = hashlib.md5(file_path.encode()).hexdigest()
    '''
    对于视频文件，封面来自前半截视频随机一帧
    '''
    ffprobe_command = f'{ffprobe_path}  -print_format json -v error -show_entries format=duration  "{file_path}"'
    result = os.popen(ffprobe_command).read()
    if result:
        video_info = json.loads(result)
        video_len=int(float(video_info['format']['duration']))
        cover_second = random.randint(1, video_len)
        ffmpeg_command = f'{ffmpeg_path} -ss {cover_second}  -i "{file_path}"  -v quiet -r 1 -t 1 -f image2 -y {PHOTO_CATCH}/{cn}.jpg'
        if not os.path.exists(f"{PHOTO_CATCH}/{cn}.jpg"):
            os.popen(ffmpeg_command).read()
        return f"{cn}.jpg", f"{PHOTO_CATCH}/{cn}.jpg"
    else:
        return None, None

def get_pic_from_comress(file_id):

    with Database() as db:
        rows=db.select("select item.name filename,item.path filepath ,parent.path parent_path,parent.file_type parent_file_type from item,item parent where item.parent=parent.id and item.id=%s",(file_id,))
        if not rows:
            return get_file(file_id)
        row=rows[0]
        name=row['filename']
        path=row['filepath']
        parent_file_type=row['parent_file_type']
        parent_path=row['parent_path']
        cn = hashlib.md5(path.encode()).hexdigest()
        file_ex=parent_path.split(".")[-1].lower()
        '''
        对于父级非压缩的，直接返回需求的数据结构
        对于父级别是压缩的，在file字段附带文件流
        '''
        if parent_file_type !='compress':
            return {
                'id':file_id,
                'name':name,
                'path':path,
                'file':None
            }
        if file_ex in ("zip",'cbz'):
            C_cls=zipfile.ZipFile
        elif file_ex in ("rar",'cbr'):
            C_cls=rarfile.RarFile
        else:# 理论上不会运行到这里，避免入库故障
            return {
                'id':file_id,
                'name':name,
                'path':path,
                'file':None
            }

        with C_cls(parent_path) as zf:
            return {
                'id':file_id,
                'name':name,
                'path':path,
                'file':BytesIO(zf.read(name))
            }



@app.route('/api/media/<int:file_id>')
def photo(file_id):
    '''
    对于需要缩略图的情况,这里先查找缓存,如果缓存未命中,生成缩略图后返回
    缩略图为240*320 如果纵横比变化,取最大值
    '''
    cached_photo = request.args.get('cache', 'true') == 'true'
    if file_id == 0:
        return not_found()

    def cached_file(file_id):
        # 不考虑压缩文件的话，这里调用get file
        photo_file = get_pic_from_comress(file_id)
        file_name = photo_file['name']
        ptype = file_name.split('.')[-1]
        file_path = photo_file['path']
        img_open=photo_file['file'] if photo_file['file'] is not None else file_path
        if file_ex2type(file_name) == 'video':
            return get_cover_for_video(file_name, file_path)

        cn = hashlib.md5(file_path.encode()).hexdigest()
        cache = PHOTO_CATCH+f"/{cn}.{ptype}"
        if not os.path.exists(cache):
            with Image.open(img_open) as img:
                width, height = img.size
                widpct = width*1.0/240
                heightpct = height*1.0/320
                dest_pct = max([widpct, heightpct])
                resized_im = img.resize(
                    (int(width/dest_pct), int(height/dest_pct)))
                resized_im.save(cache)
        if cached_photo:
            return file_name, cache
        else:
            '''
            对于非缓存类型，也进行压缩，减小其大小
            压缩为高度1024的图片
            '''
            re_cache = PHOTO_CATCH+f"/{cn}.1024.{ptype}"
            if not os.path.exists(re_cache):
                with Image.open(img_open) as img:
                    width, height = img.size
                    dest_pct = height*1.0/1024
                    resized_im = img.resize(
                        (int(width/dest_pct), int(height/dest_pct)))
                    resized_im.save(re_cache)
            return file_name, re_cache
    file_name, file_path = cached_file(file_id)
    '''
    这里是直接获取原始文件的api影片播放页数从这个路径走
    '''
    if request.args.get('cache', 'true') == 'origin':
        photo_file = get_pic_from_comress(file_id)
        file_name = photo_file['name']
        file_path = photo_file['path']
        img_open=photo_file['file'] if photo_file['file'] is not None else file_path
        mtype=mimetypes.guess_type(file_name)[0] if not file_name.endswith('flv') else 'video/x-flv'
        '''
        这里需要处理不支持的格式，目前暂时考虑使用ffmpeg转码输出
        '''
        return send_file(img_open,attachment_filename=file_name, mimetype=mtype, as_attachment=True, conditional=True)
    return send_file(file_path, mimetype=mimetypes.guess_type(file_name)[0], as_attachment=True, conditional=True)


@app.route('/api/file/<int:file_id>/video_info')
def web_file_video_info(file_id):
    with Database() as db:
        rows = db.select(
            "select id,path,name,parent,order_id,library_id from item where id=%s", (file_id,), dict_result=True)
        if rows:
            file = rows[0]
            ptype = file['name'].split('.')[-1]
            result = {
                'id': file_id,
                'name': file['name'],
                'parent': file['parent'],
                'order_id': file['order_id'],
                'library_id': file['library_id'],
                'file_type': file_ex2type(file['name'])
            }
            ffprobe_command = f'{ffprobe_path} "{file["path"]}" -show_streams -hide_banner  -v quiet'
            ffprobe_out = os.popen(ffprobe_command).read()
            if ffprobe_out:
                result['video_info'] = ffprobe_out
            return result
        return not_found()


@cache_wrapper()
def inner_web_file(file_id, full):
    with Database() as db:

        rows = db.select(
            "select id,name,parent,order_id,library_id from item where id=%s", (file_id,), dict_result=True)
        if rows:
            '''
            处理父目录重新获取sort id 避免更新导致的sort id变更
            '''
            sub_items(rows[0]['library_id'], rows[0]['parent'], 1, 1)
            rows = db.select(
                "select id,name,parent,order_id,library_id from item where id=%s", (file_id,), dict_result=True)
            file = rows[0]
            ptype = file['name'].split('.')[-1]
            result = {
                'id': file_id,
                'name': file['name'],
                'parent': file['parent'],
                'order_id': file['order_id'],
                'library_id': file['library_id'],
                'file_type': file_ex2type(file['name']),
                'mimetypes': mimetypes.guess_type(file['name'])[0] if not file['name'].endswith('flv') else 'video/x-flv'
            }
            if not full:
                return result
            '''
            sort id 排序为先文件夹后文件，因此 前一个文件夹 后一个文件 不需要判断item类型
            '''
            if file['order_id'] > 0:
                rows = db.select("select id,name,parent,order_id,library_id,item_type from item where parent=%s and order_id=%s and item_type='file'", (
                    file['parent'], file['order_id']-1), dict_result=True)
                if rows:
                    result['pre'] = rows[0]
                else:
                    result['pre'] = None
            else:
                result['pre'] = None
            result['dir'] = get_dir(file['library_id'], file['parent'])
            result['dir']['count'] = sub_item_count(
                file['library_id'], file['parent'], 'file')
            if result['dir']['count'] > (file['order_id']+1):
                result['next'] = db.select("select id,name,parent,item_type,order_id,library_id from item where parent=%s and order_id=%s", (
                    file['parent'], file['order_id']+1), dict_result=True)[0]
            else:
                result['next'] = None
            '''
            处理父目录
            '''
            sub_items(file['library_id'], result['dir']['parent'])
            dir_order_id = result['dir']['order_id']
            order_id_sql = "select id,name,cover,path,library_id,version,parent from item where library_id=%s and parent=%s and order_id=%s and item_type='dir'"
            if dir_order_id > 0:
                rows = db.select(
                    order_id_sql, (file['library_id'], result['dir']['parent'], dir_order_id-1))
                result['pre_dir'] = rows[0]
            else:
                result['pre_dir'] = None
            if (dir_order_id+1) < sub_item_count(file['library_id'], result['dir']['parent'], 'dir'):
                rows = db.select(
                    order_id_sql, (file['library_id'], result['dir']['parent'], dir_order_id+1))
                if rows:
                    result['next_dir'] = rows[0]
                else:
                    result['next_dir'] = None
            else:
                result['next_dir'] = None
            return result
        else:
            return {}


@app.route('/api/file/<int:file_id>')
def web_file(file_id):
    # 这里处理全信息
    # 包括 前一个文件，后一个文件
    # 包括 当前目录信息，当前目录文件总数
    # 包括 前一个目录信息，后一个目录信息 目录的前一个后一个允许跨越父目录
    full = request.args.get('full', 'false') == 'true'
    return json_return(inner_web_file(file_id, full))

    # '/photo/library', 'library_list',
    # '/photo/library/(\d+)', 'library',
    # '/photo/library/(\d+)/(\d+)', 'directory',


@app.route('/api/library/random')
def random_item():
    count = int(request.args.get("count", "12"))
    library = int(request.args.get("library", "0"))
    item_type = request.args.get("item_type", "dir")
    if item_type not in ('file', 'dir'):
        return json_return({
            'message': f"error request for item_type:{item_type}"
        })
    file_type = request.args.get("file_type", None)
    if file_type is not None:
        if file_type not in ('photo', 'video'):
            return json_return({
                'message': f"error request for file_type:{file_type}"
            })
    # 最近新增，如果定义了，根据id逆序排列（不能根据文件更新时间，新增文件可能是时间非常久之前的文件）
    new_add = request.args.get("new_add", None)
    if new_add:
        new_add = int(new_add)
    with Database() as db:
        sql = f"select id,name,cover,path,library_id,item_type,version,parent from item where item_type='{item_type}'"
        if library:
            sql += f" and library_id={library}"
        if file_type:
            sql += f" and file_type='{file_type}'"
        if new_add:
            sql = f"select * from ( {sql} order by id desc limit {new_add}) x order by random() limit {count}"
        else:
            sql+=f" order by random() limit {count}"
        return json_return(
            db.select(sql)
        )


@app.route('/api/library/search')
def search():
    count = int(request.args.get("count", "12"))
    library = int(request.args.get("library", "0"))
    item_type = request.args.get("item_type", "dir")
    keyword = request.args.get("keyword", None)
    if keyword is None:
        return {
            "message": "必须指定搜索关键字"
        }
    keyword = '%'+keyword+'%'
    with Database() as db:
        if library:
            rows = db.select(
                "select id,name,cover,path,library_id,item_type,version,parent from item where library_id=%s  and item_type=%s and name ilike %s order by name limit %s", (library, item_type, keyword, count,))
        else:
            rows = db.select(
                "select id,name,cover,path,library_id,item_type,version,parent from item  where item_type=%s and name ilike %s order by name limit %s", (item_type, keyword, count,))
    return json_return(
        rows
    )


@app.route('/api/library/<lib_id>/<int:dir_id>')
def directory(lib_id, dir_id):
    '''
    这里处理分页
    入参为：
    items_per_page:30,
    page:1
    返回：
    总数
    '''
    def toInt(val, default):
        try:
            return int(val)
        except:
            return default
    items_per_page = toInt(request.args.get("items_per_page", "30"), 30)
    page = toInt(request.args.get("page", "1"), 1)
    if dir_id == 0:
        result = {
            'library': get_library(lib_id),
            'dir': [],
            'items': sub_items(lib_id, dir_id, items_per_page, page),
            'item_count': sub_item_count(lib_id, dir_id),
            'parents': []
        }
        return json_return(
            result
        )
    return json_return(
        {
            'library': get_library(lib_id),
            'dir': get_dir(lib_id, dir_id),
            'items': sub_items(lib_id, dir_id, items_per_page, page),
            'item_count': sub_item_count(lib_id, dir_id),
            'parents': get_parent(lib_id, dir_id)
        }
    )


@app.route('/api/library/<int:lib_id>', methods=['GET', "DELETE", "POST"])
def library(lib_id):
    if request.method == 'DELETE':
        Library.drop(lib_id)
        return json_return(
            {
                'message': "删除成功"
            }
        )
    if request.method == 'POST':
        data = json.loads(request.data.decode("utf8"))
        Library.changeName(lib_id, data['name'])
        return json_return(
            {
                'message': "修改名称成功"
            }
        )
    return json_return(
        {
            'library': get_library(lib_id),
            'dirs': sub_items(lib_id, 0)
        }
    )


@app.route('/api/library/<int:lib_id>/sync')
def library_sync(lib_id):
    return json_return(
        flush_lib(lib_id)
    )


@app.route('/api/library', methods=['GET', "PUT"])
def library_list():
    if request.method == 'PUT':
        data = json.loads(request.get_data().decode("utf8"))
        Library.add(data['name'], data['path'], data['lib_type'],'','','')
        return json_return(
            {
                'message': "添加成功"
            }
        )

    full = request.args.get("full", "false") == 'true'
    with Database() as db:
        rows = db.select(
            "select id,name,lib_type,dir,status,version from library order by id", dict_result=True)
        if not full:
            return json_return(rows)
        result = {
            row['id']: {
                'id': row['id'],
                'name': row['name'],
                'lib_type': row['lib_type'],
                'dir': row['dir'],
                'status': row['status'],
                'version': row['version'],
                'count': 0,
                'next_count': 0
            } for row in rows}
        item_sql = "select library_id,version,count(1) c from item group by library_id,version"
        item_rows = db.select(item_sql, dict_result=True)
        for row in item_rows:
            if row['version'] == result[row['library_id']]['version']:
                result[row['library_id']]['count'] = row['c']
            else:
                result[row['library_id']]['next_count'] = row['c']
        return json_return(
            [item for item in result.values()]
        )

# @app.before_request


def auth():
    if request.path in ('/api/login'):
        return
    if request.path.startswith('/static/') or request.path.startswith('/api/public/'):
        return
    username = request.cookies.get('username')
    token = request.cookies.get('token')
    if not User.isLogin(username, token):
        resp = json_return(
            {
                'token': None
            }
        )
        resp.delete_cookie('username')
        resp.delete_cookie('token')
        return resp


@app.route("/api/library/default_config")
def library_default_config():
    '''
    返回默认的配置值
    包括：
        默认需要跳过的文件
        默认需要跳过的文件夹
        默认支持的文件类型
    '''
    return {
        'skip_file': config.ignore_file,
        'skip_dir': config.ignore_dir,
        'supprot_file': config.support_file
    }


@app.route("/api/library/lsdir")
def library_lsdir():
    '''
    这里用来支持页面选择库路径
    对于windows，如果列出根/目录，则返回盘符列表
    可以通过选项仅选择文件或者仅选择目录
    '''
    data = request.get_data()
    json_data = json.loads(data.decode('utf8'))
    path = json_data['path']
    show_file = json_data.get('show_file', 'true') == 'true'
    show_dir = json_data.get('show_dir', 'true') == 'true'
    result = []
    for name in os.listdir(path):
        item = {
            'name': name,
            'isdir': os.path.isdir(path+'/'+name)
        }
        if show_file and not item['isdir']:
            result.append(item)
        if show_dir and item['isdir']:
            result.append(item)
    return json_return(result)


@app.route('/api/changeAuth', methods=['POST', ])
def changeAuth():
    data = request.get_data()
    json_data = json.loads(data.decode('utf8'))
    username = json_data['username']
    password = json_data['password']
    new_username = json_data.get('new_username', None)
    new_password = json_data.get('new_password', None)
    try:
        if User.change(username, password, new_username, new_password):
            return json_return(
                {
                    'message': "修改用户成功"
                }
            )
        else:
            return json_return(
                {
                    'message': "用户密码填写错误"
                }
            )
    except Exception as e:
        return json_return(
            {
                'message': str(e)
            }
        )


@app.route('/api/login', methods=['POST', ])
def login():
    data = request.get_data()
    json_data = json.loads(data.decode('utf8'))
    username = json_data['username']
    password = json_data['password']
    if User.login(username, password):
        return json_return(
            {
                'token': get_password(username, password)
            }
        )
    else:
        return json_return(
            {
                'token': None
            }
        )


'''


/api/chapter/<int:lib_id>
    GET 获取书列表
    POST 新增书
'''
@app.route('/api/chapter/<int:lib_id>', methods=['POST', "GET"])
def chapter_library(lib_id):
    if request.method == 'POST':
        data = request.get_data()
        json_data = json.loads(data.decode('utf8'))
        title = json_data['title']
        summary = json_data['summary']
        Chapter.newBook(lib_id, title, summary, None)
        return json_return(
            {
                "message": f"新增书 {title} 成功"
            }
        )

    result = []
    with Database() as db:
        for row in db.select("select id from chapter where library_id=%s and parent=0", (lib_id,), dict_result=True):
            chapter = Chapter.getChapter(row['id'])
            chapter.cover = None
            result.append({
                k: v
                for k, v in chapter.__dict__.items() if not k.startswith('__')})
    return json_return(
        result
    )


'''
处理写作相关API
/api/chapter/<int:lib_id>/<int:chapter_id>
    获取chapter
    chapter 0为库根
    GET 获取当前chapter
    POST 为当前chapter新增chapter
    PUT 修改当前chapter
    DELETE 删除当前chapter
'''


@app.route('/api/chapter/<int:lib_id>/<int:chapter_id>/cover/<random>')
def chapter_cover_radom(lib_id, chapter_id, random):
    '''
    这个api处理封面变更后页面不刷新的问题
    '''
    return chapter_cover(lib_id, chapter_id)


@app.route('/api/chapter/<int:lib_id>/<int:chapter_id>/cover', methods=['POST', "GET"])
def chapter_cover(lib_id, chapter_id):
    file_root = None
    with Database() as db:

        rows = db.select("select dir from library where id=%s", (lib_id,))

        if rows:
            file_root = rows[0]['dir']
        else:
            return not_found()
        if request.method == 'POST':
            if 'file' not in request.files:
                return not_found()
            file = request.files['file']
            filename = str(chapter_id)+'.'+file.filename.split(".")[-1]
            file.save(file_root+'/'+filename)
            # 封面都保存在 库目录下根目录，文件名为chapter id
            db.execute("update chapter set cover=%s where id=%s",
                       (filename, chapter_id))
            return {
                'message': "上传封面成功"
            }
        rows = db.select(
            "select cover from chapter where id=%s", (chapter_id,))
        if rows:
            if rows[0]['cover']:
                filename = rows[0]['cover']
                return send_file(file_root+'/'+filename, mimetype=mimetypes.guess_type(filename)[0], as_attachment=True)
            else:
                return not_found()
        else:
            return not_found()


@app.route('/api/chapter/<int:lib_id>/<int:chapter_id>', methods=['POST', "GET", "PUT", "DELETE"])
def chapter_info(lib_id, chapter_id):
    chapter = Chapter.getChapter(chapter_id)
    if chapter is None:
        return not_found("没有找到章节")
    if request.method == 'PUT':
        data = request.get_data()
        json_data = json.loads(data.decode('utf8'))
        current_update_id = chapter.update_id
        for name in ('title', 'summary', 'note', 'status', 'chapter_type', 'context', 'update_id'):
            if name in json_data:
                if json_data[name]:
                    chapter.__dict__[name] = json_data[name]
        '''
        注意，这里为了防止客户端服务端时间不一，响应时间不一的情况，导致更新乱序(比如自动保存触发的update，后发先至)，chapter更新时候需要附带update id，只有update id大于当前update id的情况，才会触发章节更新

        '''
        if chapter.update_id > current_update_id:
            chapter.update()
            return json_return(
                {
                    'utime': chapter.utime,
                    "message": f"修改章节 {chapter.title} 成功"
                }
            )
        else:
            return json_return(
                {
                    'utime': chapter.utime,
                    "message": "这是一个过老的更新请求，请设置最新的update id"
                }
            )
    if request.method == 'POST':
        data = request.get_data()
        json_data = json.loads(data.decode('utf8'))
        title = json_data['title']
        summary = json_data['summary']
        new_chapter = chapter.newChapter(title, summary)
        return json_return(
            {
                "chapter": {
                    'id': new_chapter.id
                },
                "message": f"新增章节 {title} 成功"
            }
        )

    if request.method == 'DELETE':
        chapter.drop()
        return json_return(
            {
                "message": f"删除章节 {chapter.title} 成功"
            }
        )
    # GET
    full = request.args.get("full", "false") == 'true'
    if not full:
        chapter.children = chapter.getChildren()
        chapter.parents = chapter.getParents()
        return json_return(chapter.__dict__
                           )
    else:
        chapter.children = chapter.getChildren(all=True, asList=False)
        chapter.parents = chapter.getParents()
        return json_return(chapter.__dict__
                           )


@app.route('/api/chapter/<int:lib_id>/<int:chapter_id>/change_pos', methods=['POST'])
def change_pos(lib_id, chapter_id):
    chapter = Chapter.getChapter(chapter_id)
    data = request.get_data()
    json_data = json.loads(data.decode('utf8'))
    dest_chapter = json_data['dest_chapter']
    dest_position = json_data['dest_position']
    chapter.changePositon(dest_chapter, dest_position)
    return json_return({
        "message": f"修改节点{chapter_id} 到目标节点 {dest_chapter} 位置 {dest_position} 成果"
    }
    )


@app.route('/api/chapter/<int:lib_id>/<int:chapter_id>/preview')
def chapter_prevew(lib_id, chapter_id):
    chapter = Chapter.getChapter(chapter_id)
    return json_return({
        'context': chapter.preview()
    }
    )


@app.route('/api/books/<int:lib_id>/sync')
def books_sync(lib_id):
    with Database() as db:
        status = db.select("select status from library where id=%s",
                           (lib_id,), dict_result=True)[0]['status']
        if status == 'syncing':
            return {
                'message': "当前正在执行同步任务，无法另外启动"
            }
        db.execute("update library set status=%s where id=%s",
                   ('syncing', lib_id))

    def inner_sync_books(lib_id):
        Chapter.syncWordCount(lib_id)
        with Database() as db:
            db.execute("update library set status=%s where id=%s",
                       ('synced', lib_id))

    executor.submit(inner_sync_books, lib_id)
    return json_return(
        {
            "message": "重新统计字数开始执行"
        }

    )


'''
视频播放解码播放逻辑如下:

1. 页面请求/api/video/hls/<video_id>
    1 从url参数获取开始时间
    2 启动ffmppg转译hls
        1. 如果当前有ffmpeg在运行，结束进程
        2. 清空ffmpeg缓存文件夹
        3. 启动ffmpeg

1. 页面请求是<videoid>.m3u8
    1. 返回m3u8文件，处理request no cache
2. 页面请求<videoid>.<index>.ts
    1. 确认当前ts是否是最后一个ts（如果ffmpeg还在运行，或者index+1之后的文件仍然存在，则认为不是最后一个）
    2. 如果是最后一个，直接返回
    3. 如果index+1存在，返回，
    4. 否则等待直到ffmpeg结束或者index+1出现，返回请求文件
    request处理为no cache
'''
import time
def inner_ffmpeg(ffmpeg_command):
    '''
    管理ffmpeg进程的状态
    '''

    with Database() as db:
        rows=db.select("select pid from ffmpeg_info")
        for row in rows:
            pid=row['pid']
            try:
                os.kill(pid,9)
            except:
                pass
            finally:
                db.execute("delete from ffmpeg_info where pid=%s",(pid,))
        ffmpeg_popen=subprocess.Popen(ffmpeg_command,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pid=ffmpeg_popen.pid
        db.execute("insert into ffmpeg_info(pid,command) values(%s,%s)",(pid,ffmpeg_command))
        db.execute("commit")
        while ffmpeg_popen.poll() is None:
            time.sleep(1)
        db.execute("delete from ffmpeg_info where pid=%s",(pid,))
        db.execute("commit")


# ffmpen_popen=None
import shutil
@app.route('/api/video/hls/<video_id>')
def ffmpeg_hls(video_id):
    # global ffmpen_popen
    start_time = request.args.get("start", "0")
    start_time=float(start_time)
    video=get_file(video_id)
    ffmpeg_cache=f'{PHOTO_CATCH}/ffmpeg'

    ffmpeg_command=f'{ffmpeg_path} -ss {start_time} -i "{video["path"]}" -c:a aac  -vcodec {ffmpeg_codec} -f hls  -bsf:v h264_mp4toannexb -hls_list_size 100 -b:v 6000k  -hls_time 10 "{ffmpeg_cache}/index.m3u8"'
    shutil.rmtree(ffmpeg_cache)
    os.makedirs(ffmpeg_cache)
    executor.submit(inner_ffmpeg, ffmpeg_command)
    ffprobe_command = f'{ffprobe_path}  -print_format json -v error -show_entries format=duration  "{video["path"]}"'
    result = os.popen(ffprobe_command).read()
    if result:
        video_info = json.loads(result)
        duration=float(video_info['format']['duration'])
    return json_return({
        'message':f"视频 {video['name']} {video['id']}开始转码",
        'duration':duration
    }
    )

@app.route('/api/video/<video_id>')
def video_ffprobe_info(video_id):
    video=get_file(video_id)
    ffprobe_command = f'{ffprobe_path}  -print_format json -v error -show_entries format=duration  "{video["path"]}"'
    result = os.popen(ffprobe_command).read()
    if result:
        video_info = json.loads(result)
        duration=float(video_info['format']['duration'])
    return json_return({
        'message':f"视频 {video['name']} {video['id']}开始转码",
        'duration':duration
    }
    )

@app.route('/api/video/hls/index.m3u8')
def hsl_index():
    # ffmpeg_cache=f'{PHOTO_CATCH}/ffmpeg'
    file_path=f'{PHOTO_CATCH}/ffmpeg/'+'index.m3u8'
    '''
    这里可能无法找到文件，最多等待10s，如果10s后依然没有文件，返回错误
    '''
    for i in range(100):
        if os.path.exists(file_path):
            return send_file(file_path,cache_timeout=0)
        time.sleep(0.1)
    return json_return({
        'message':f"文件{file_path}没有找到，解码错误或者失败"
    })

@app.route('/api/video/hls/index<index_id>.ts')
def hsl_file(index_id):
    # ffmpeg_cache=f'{PHOTO_CATCH}/ffmpeg'
    '''
    这里认为从m3u8获取到的都是有效文件
    '''
    return send_file(f'{PHOTO_CATCH}/ffmpeg/'+f'index{index_id}.ts',cache_timeout=0)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=4999)
