# encoding=utf8

pg_conninfo = "host=localhost port=5432 user=app password=app dbname=postgres"
ignore_file = ['.DS_Store', 'Thumbs.db']
ignore_dir = ['@eaDir', '__gsdata__']
PHOTO_BUF_SIZE = 1024000
PHOTO_CATCH = "/tmp"
support_file = { # 已经废弃字段，仅为以后考虑保留
    'photo': ",".join(["jpg", 'png', 'bmp', 'jpeg', 'gif']),
    'novel': ",".join(["txt", 'md']),
    'music': ",".join(["mp3", 'wma']),
    'video': ",".join(['mp4', 'avi', 'mkv', 'webm', 'flv', 'mov']),
}
__file_ex2type = {
    'mp4': "video", 'avi': "video", 'mkv': "video", 'webm': "video", 'flv': "video", 'mov': "video",
    "jpg":'photo', 'png':'photo', 'bmp':'photo', 'jpeg':'photo', 'gif':'photo','zip':'compress','rar':'compress','cbz':'compress','cbr':'compress'
}


def file_ex2type(filename):
    ptype = filename.split('.')[-1].lower()
    return __file_ex2type.get(ptype,'file')

ffmpeg_path = "/usr/local/bin/ffmpeg"
ffprobe_path = "/usr/local/bin/ffprobe"
redis_conn = {
    'host': '127.0.0.1',
    'port': 6379
}
